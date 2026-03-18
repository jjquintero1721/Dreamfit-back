import logging
from typing import Dict, Any
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.repositories.macronutrients_repository import MacronutrientsRepository
from app.repositories.coach_profile_repository import CoachProfileRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.content_service import ContentService
from app.services.openai_service import OpenAIService
from app.schemas.meal_plan_schema import CreateMealPlanRequest

meal_plan_logger = logging.getLogger("dreamfit_api.meal_plan_service")


class MealPlanService:
    @staticmethod
    async def create_meal_plan(
            coach_id: str,
            request_data: CreateMealPlanRequest
    ) -> Dict[str, Any]:

        meal_plan_logger.info(
            f"CREATE_MEAL_PLAN_START | CoachID: {coach_id} | MenteeID: {request_data.mentee_id}"
        )

        try:
            coach_profile = await MealPlanService._ensure_coach_can_create_meal_plan(coach_id)

            await MealPlanService._validate_mentee_belongs_to_coach(
                coach_id, request_data.mentee_id
            )

            macros = await MealPlanService._get_mentee_macronutrients(request_data.mentee_id)
            if not macros:
                meal_plan_logger.warning(
                    f"NO_MACROS_FOUND | MenteeID: {request_data.mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debes calcular los macronutrientes del alumno antes de crear un plan de alimentación"
                )

            calories = int(macros.calories)
            protein = int(macros.macros.protein.replace('g', ''))
            fat = int(macros.macros.fat.replace('g', ''))
            carbs = int(macros.macros.carbs.replace('g', ''))

            meal_plan_logger.debug(
                f"USING_MACROS | Calories: {calories} | Protein: {protein}g | "
                f"Fat: {fat}g | Carbs: {carbs}g"
            )

            openai_service = OpenAIService()
            generated_plan = await openai_service.generate_meal_plan(
                calories=calories,
                protein=protein,
                carbs=carbs,
                fat=fat,
                days=request_data.days,
                meals_per_day=request_data.meals_per_day,
                notes=request_data.notes or ""
            )

            await MealPlanRepository.delete_previous_plans(request_data.mentee_id)
            meal_plan_logger.debug(f"PREVIOUS_PLANS_DELETED | MenteeID: {request_data.mentee_id}")

            plan_data = {
                "mentee_id": request_data.mentee_id,
                "coach_id": coach_id,
                "calories": generated_plan["calories"],
                "dailyMacros": generated_plan["dailyMacros"],
                "days": generated_plan["days"],
                "created_at": datetime.now(timezone.utc)
            }

            created_plan = await MealPlanRepository.create(plan_data)
            meal_plan_logger.info(f"MEAL_PLAN_CREATED | PlanID: {created_plan.id}")

            await MealPlanService._update_mentee_meal_plan_status(
                request_data.mentee_id,
                str(created_plan.id)
            )

            await MealPlanService._increment_coach_meal_plan_usage(coach_profile)

            meal_plan_logger.info(
                f"CREATE_MEAL_PLAN_SUCCESS | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id} | PlanID: {created_plan.id}"
            )

            return {
                "plan_id": str(created_plan.id),
                "message": "Plan de alimentación creado exitosamente"
            }

        except HTTPException:
            raise
        except Exception as e:
            meal_plan_logger.error(
                f"CREATE_MEAL_PLAN_ERROR | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating meal plan: {str(e)}"
            )

    @staticmethod
    async def get_meal_plan_by_mentee(
            mentee_id: str,
            logged_user_id: str
    ) -> Dict[str, Any]:

        meal_plan_logger.info(
            f"GET_MEAL_PLAN_START | MenteeID: {mentee_id} | UserID: {logged_user_id}"
        )

        try:
            if mentee_id != logged_user_id:
                mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)
                if not mentee_profile or mentee_profile.coach_id != logged_user_id:
                    meal_plan_logger.warning(
                        f"ACCESS_DENIED | MenteeID: {mentee_id} | UserID: {logged_user_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permiso para acceder a este plan de alimentación"
                    )

            plan = await MealPlanRepository.get_by_mentee_id(mentee_id)

            if not plan:
                meal_plan_logger.warning(f"PLAN_NOT_FOUND | MenteeID: {mentee_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró un plan de alimentación para este alumno"
                )

            meal_plan_logger.info(
                f"GET_MEAL_PLAN_SUCCESS | MenteeID: {mentee_id} | PlanID: {plan.id}"
            )

            return MealPlanService._format_meal_plan_response(plan)

        except HTTPException:
            raise
        except Exception as e:
            meal_plan_logger.error(
                f"GET_MEAL_PLAN_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving meal plan: {str(e)}"
            )

    @staticmethod
    async def _validate_mentee_belongs_to_coach(coach_id: str, mentee_id: str) -> None:
        mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)

        if not mentee_profile:
            meal_plan_logger.warning(f"MENTEE_NOT_FOUND | MenteeID: {mentee_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alumno no encontrado"
            )

        if mentee_profile.coach_id != coach_id:
            meal_plan_logger.warning(
                f"MENTEE_COACH_MISMATCH | MenteeID: {mentee_id} | "
                f"ExpectedCoach: {coach_id} | ActualCoach: {mentee_profile.coach_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes crear planes para tus propios alumnos"
            )

    @staticmethod
    async def _get_mentee_macronutrients(mentee_id: str):
        macros_list = await MacronutrientsRepository.get_by_mentee_id(mentee_id)
        return macros_list[0] if macros_list else None

    @staticmethod
    async def _update_mentee_meal_plan_status(mentee_id: str, plan_id: str) -> None:
        mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)

        if mentee_profile:
            mentee_profile.userPlans.mealPlan.active = True
            mentee_profile.userPlans.mealPlan.planId = plan_id
            await mentee_profile.save()
            meal_plan_logger.debug(
                f"MENTEE_STATUS_UPDATED | MenteeID: {mentee_id} | PlanID: {plan_id}"
            )

    @staticmethod
    def _format_meal_plan_response(plan) -> Dict[str, Any]:
        plan_dict = jsonable_encoder(plan)

        return {
            "_id": plan_dict["_id"],
            "coach_id": plan_dict["coach_id"],
            "mentee_id": plan_dict["mentee_id"],
            "created_at": plan_dict["created_at"],
            "mealPlan": {
                "calories": plan_dict["calories"],
                "dailyMacros": plan_dict["dailyMacros"],
                "days": plan_dict["days"]
            }
        }

    @staticmethod
    async def _ensure_coach_can_create_meal_plan(coach_id: str):
        coach_profile = await CoachProfileRepository.get_by_user_id(coach_id)

        if not coach_profile:
            meal_plan_logger.warning(f"COACH_PROFILE_NOT_FOUND | CoachID: {coach_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil del coach no encontrado"
            )

        membership = await MembershipRepository.get_by_user_id(coach_id)
        if not membership:
            meal_plan_logger.warning(f"COACH_MEMBERSHIP_NOT_FOUND | CoachID: {coach_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El coach no tiene una membresía asignada"
            )

        plan = await ContentService.get_plan_by_id(membership.plan_id)
        limit_raw = plan.get("maxDailyMealPlans")

        try:
            limit_value = int(limit_raw) if limit_raw is not None else None
        except (TypeError, ValueError):
            limit_value = None

        if limit_value is not None and coach_profile.dailyMealPlansCount >= limit_value:
            meal_plan_logger.warning(
                f"COACH_MEAL_PLAN_LIMIT_REACHED | CoachID: {coach_id} | Limit: {limit_value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Alcanzaste tu límite diario de planes de alimentación"
            )

        return coach_profile

    @staticmethod
    async def _increment_coach_meal_plan_usage(coach_profile):
        coach_profile.dailyMealPlansCount += 1
        await coach_profile.save()
        meal_plan_logger.debug(
            f"COACH_MEAL_PLAN_COUNT_INCREMENTED | CoachID: {coach_profile.user_id} | "
            f"Count: {coach_profile.dailyMealPlansCount}"
        )
