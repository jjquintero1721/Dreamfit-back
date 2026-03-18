import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.user import User
from app.models.coach_profile import CoachProfile
from app.models.mentee_profile import MenteeProfile
from app.models.membership import Membership
from app.repositories.user_repository import UserRepository
from app.repositories.coach_profile_repository import CoachProfileRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.content_service import ContentService
from app.schemas.system_admin_schemas import (
    CoachListItemResponse,
    CoachDetailResponse,
    MenteeBasicInfo
)

system_admin_logger = logging.getLogger("dreamfit_api.system_admin_service")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SystemAdminService:
    @staticmethod
    async def get_all_coaches() -> List[CoachListItemResponse]:
        """Obtener todos los coaches del sistema con su información de membresía"""
        system_admin_logger.info("FETCHING_ALL_COACHES")

        try:
            # Obtener todos los usuarios con rol coach
            coaches = await User.find(User.role == "coach").to_list()
            system_admin_logger.info(f"FOUND_COACHES | Count: {len(coaches)}")

            coaches_list = []

            for coach_user in coaches:
                # Obtener perfil del coach
                coach_profile = await CoachProfileRepository.get_by_user_id(str(coach_user.id))

                # Obtener membresía del coach
                membership = await MembershipRepository.get_by_user_id(str(coach_user.id))

                # Verificar si la membresía está activa
                has_active_membership = False
                membership_end_date = None
                plan_id = None
                plan_name = None

                if membership and membership.end_date:
                    if membership.end_date > datetime.now():
                        has_active_membership = True
                        membership_end_date = membership.end_date
                        plan_id = membership.plan_id

                        # Obtener nombre del plan desde el CMS
                        try:
                            plan = await ContentService.get_plan_by_id(plan_id)
                            plan_name = plan.get("name")
                        except Exception as e:
                            system_admin_logger.warning(
                                f"FAILED_TO_GET_PLAN_NAME | PlanID: {plan_id} | Error: {str(e)}"
                            )

                # Contar mentees del coach
                mentees_count = await MenteeProfileRepository.count_by_coach_id(str(coach_user.id))

                coaches_list.append(CoachListItemResponse(
                    userId=str(coach_user.id),
                    email=coach_user.email,
                    name=coach_profile.name if coach_profile else "",
                    lastName=coach_profile.last_name if coach_profile else "",
                    hasActiveMembership=has_active_membership,
                    membershipEndDate=membership_end_date,
                    planId=plan_id,
                    planName=plan_name,
                    menteesCount=mentees_count
                ))

            system_admin_logger.info(f"GET_ALL_COACHES_SUCCESS | Count: {len(coaches_list)}")
            return coaches_list

        except Exception as e:
            system_admin_logger.error(f"GET_ALL_COACHES_ERROR | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving coaches"
            )

    @staticmethod
    async def get_coach_details(coach_id: str) -> CoachDetailResponse:
        """Obtener detalles completos de un coach"""
        system_admin_logger.info(f"FETCHING_COACH_DETAILS | CoachID: {coach_id}")

        try:
            # Obtener usuario
            coach_user = await UserRepository.get_by_id(coach_id)
            if not coach_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach not found"
                )

            if coach_user.role != "coach":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a coach"
                )

            # Obtener perfil del coach
            coach_profile = await CoachProfileRepository.get_by_user_id(coach_id)
            if not coach_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach profile not found"
                )

            # Obtener membresía
            membership = await MembershipRepository.get_by_user_id(coach_id)

            # Verificar si la membresía está activa
            has_active_membership = False
            membership_start_date = None
            membership_end_date = None
            plan_id = None
            plan_name = None
            max_daily_meal_plans = None
            max_mentees = None

            if membership and membership.end_date:
                if membership.end_date > datetime.now():
                    has_active_membership = True
                    membership_start_date = membership.start_date
                    membership_end_date = membership.end_date
                    plan_id = membership.plan_id

                    # Obtener información del plan desde el CMS
                    try:
                        plan = await ContentService.get_plan_by_id(plan_id)
                        plan_name = plan.get("name")
                        max_daily_meal_plans = plan.get("maxDailyMealPlans")
                        max_mentees = plan.get("maxMentees")
                    except Exception as e:
                        system_admin_logger.warning(
                            f"FAILED_TO_GET_PLAN_INFO | PlanID: {plan_id} | Error: {str(e)}"
                        )

            # Contar mentees
            mentees_count = await MenteeProfileRepository.count_by_coach_id(coach_id)

            coach_details = CoachDetailResponse(
                userId=coach_id,
                email=coach_user.email,
                name=coach_profile.name,
                lastName=coach_profile.last_name,
                createdAt=coach_user.created_at,
                hasActiveMembership=has_active_membership,
                membershipStartDate=membership_start_date,
                membershipEndDate=membership_end_date,
                planId=plan_id,
                planName=plan_name,
                dailyMealPlansCount=coach_profile.dailyMealPlansCount,
                maxDailyMealPlans=max_daily_meal_plans,
                maxMentees=max_mentees,
                menteesCount=mentees_count
            )

            system_admin_logger.info(f"GET_COACH_DETAILS_SUCCESS | CoachID: {coach_id}")
            return coach_details

        except HTTPException:
            raise
        except Exception as e:
            system_admin_logger.error(
                f"GET_COACH_DETAILS_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving coach details"
            )

    @staticmethod
    async def get_coach_mentees(coach_id: str) -> List[MenteeBasicInfo]:
        """Obtener todos los mentees de un coach"""
        system_admin_logger.info(f"FETCHING_COACH_MENTEES | CoachID: {coach_id}")

        try:
            # Verificar que el coach existe
            coach_user = await UserRepository.get_by_id(coach_id)
            if not coach_user or coach_user.role != "coach":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach not found"
                )

            # Obtener perfiles de mentees
            mentee_profiles = await MenteeProfile.find(
                MenteeProfile.coach_id == coach_id
            ).to_list()

            system_admin_logger.info(
                f"FOUND_MENTEES | CoachID: {coach_id} | Count: {len(mentee_profiles)}"
            )

            mentees_list = []

            for mentee_profile in mentee_profiles:
                # Obtener información del usuario mentee
                mentee_user = await UserRepository.get_by_id(mentee_profile.user_id)
                if mentee_user:
                    mentees_list.append(MenteeBasicInfo(
                        userId=mentee_profile.user_id,
                        email=mentee_user.email,
                        name=mentee_profile.name,
                        lastName=mentee_profile.last_name,
                        createdAt=mentee_user.created_at
                    ))

            system_admin_logger.info(
                f"GET_COACH_MENTEES_SUCCESS | CoachID: {coach_id} | Count: {len(mentees_list)}"
            )
            return mentees_list

        except HTTPException:
            raise
        except Exception as e:
            system_admin_logger.error(
                f"GET_COACH_MENTEES_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving coach mentees"
            )

    @staticmethod
    async def assign_membership(
        coach_id: str,
        plan_id: str,
        duration_months: int
    ) -> dict:
        """Asignar o cambiar la membresía de un coach"""
        system_admin_logger.info(
            f"ASSIGNING_MEMBERSHIP | CoachID: {coach_id} | PlanID: {plan_id} | "
            f"Duration: {duration_months} months"
        )

        try:
            # Verificar que el coach existe
            coach_user = await UserRepository.get_by_id(coach_id)
            if not coach_user or coach_user.role != "coach":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach not found"
                )

            # Verificar que el plan existe en el CMS
            try:
                plan = await ContentService.get_plan_by_id(plan_id)
            except Exception as e:
                system_admin_logger.error(
                    f"PLAN_NOT_FOUND | PlanID: {plan_id} | Error: {str(e)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plan not found"
                )

            # Verificar si ya tiene una membresía
            existing_membership = await MembershipRepository.get_by_user_id(coach_id)

            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_months * 30)

            system_admin_logger.debug(
                f"MEMBERSHIP_DATES | StartDate: {start_date} | EndDate: {end_date}"
            )

            if existing_membership:
                # Actualizar membresía existente
                existing_membership.plan_id = plan_id
                existing_membership.start_date = start_date
                existing_membership.end_date = end_date
                await existing_membership.save()

                system_admin_logger.info(
                    f"MEMBERSHIP_UPDATED | CoachID: {coach_id} | PlanID: {plan_id}"
                )
            else:
                # Crear nueva membresía
                membership_data = {
                    "user_id": coach_id,
                    "plan_id": plan_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
                await MembershipRepository.create(membership_data)

                system_admin_logger.info(
                    f"MEMBERSHIP_CREATED | CoachID: {coach_id} | PlanID: {plan_id}"
                )

            return {
                "message": "Membership assigned successfully",
                "planName": plan.get("name"),
                "startDate": start_date.isoformat() if start_date else None,
                "endDate": end_date.isoformat() if end_date else None
            }

        except HTTPException:
            raise
        except Exception as e:
            system_admin_logger.error(
                f"ASSIGN_MEMBERSHIP_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error assigning membership"
            )

    @staticmethod
    async def cancel_membership(coach_id: str) -> dict:
        """Cancelar la membresía de un coach"""
        system_admin_logger.info(f"CANCELING_MEMBERSHIP | CoachID: {coach_id}")

        try:
            # Verificar que el coach existe
            coach_user = await UserRepository.get_by_id(coach_id)
            if not coach_user or coach_user.role != "coach":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach not found"
                )

            # Obtener membresía
            membership = await MembershipRepository.get_by_user_id(coach_id)
            if not membership:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No membership found for this coach"
                )

            # Cancelar membresía (establecer end_date a ahora)
            membership.end_date = datetime.now()
            await membership.save()

            system_admin_logger.info(f"MEMBERSHIP_CANCELED | CoachID: {coach_id}")

            return {"message": "Membership canceled successfully"}

        except HTTPException:
            raise
        except Exception as e:
            system_admin_logger.error(
                f"CANCEL_MEMBERSHIP_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error canceling membership"
            )

    @staticmethod
    async def update_coach_password(coach_id: str, new_password: str) -> dict:
        """Cambiar la contraseña de un coach desde el sistema"""
        system_admin_logger.info(f"UPDATING_COACH_PASSWORD | CoachID: {coach_id}")

        try:
            # Verificar que el coach existe
            coach_user = await UserRepository.get_by_id(coach_id)
            if not coach_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach not found"
                )

            if coach_user.role != "coach":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a coach"
                )

            # Hash de la nueva contraseña
            hashed_password = pwd_context.hash(new_password)

            # Actualizar contraseña
            coach_user.password = hashed_password
            await coach_user.save()

            system_admin_logger.info(f"COACH_PASSWORD_UPDATED | CoachID: {coach_id}")

            return {"message": "Password updated successfully"}

        except HTTPException:
            raise
        except Exception as e:
            system_admin_logger.error(
                f"UPDATE_COACH_PASSWORD_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating password"
            )
