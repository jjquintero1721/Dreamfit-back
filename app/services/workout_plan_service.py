import logging
from fastapi import HTTPException, status
from typing import Dict, Any
from fastapi.encoders import jsonable_encoder

from app.repositories.workout_plan_repository import WorkoutPlanRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.schemas.workout_plan_schema import CreateWorkoutPlanRequest

workout_service_logger = logging.getLogger("dreamfit_api.workout_service")


class WorkoutPlanService:
    @staticmethod
    async def create_workout_plan(coach_id: str, request_data: CreateWorkoutPlanRequest) -> Dict[str, Any]:
        workout_service_logger.info(
            f"CREATE_WORKOUT_PLAN_START | CoachID: {coach_id} | MenteeID: {request_data.mentee_id}"
        )

        try:
            await WorkoutPlanService._validate_mentee_belongs_to_coach(
                coach_id, request_data.mentee_id
            )
            workout_service_logger.debug(
                f"MENTEE_VALIDATION_PASSED | CoachID: {coach_id} | MenteeID: {request_data.mentee_id}")

            await WorkoutPlanRepository.delete_previous_plans(request_data.mentee_id)
            workout_service_logger.debug(f"PREVIOUS_PLANS_DELETED | MenteeID: {request_data.mentee_id}")

            plan_data = {
                "coach_id": coach_id,
                "mentee_id": request_data.mentee_id,
                "trainingObjective": request_data.trainingObjective,
                "days": [day.dict() for day in request_data.days]
            }

            created_plan = await WorkoutPlanRepository.create(plan_data)
            workout_service_logger.info(f"WORKOUT_PLAN_CREATED | PlanID: {created_plan.id}")

            await WorkoutPlanService._update_mentee_workout_plan_status(
                request_data.mentee_id,
                str(created_plan.id)
            )
            workout_service_logger.debug(f"MENTEE_STATUS_UPDATED | MenteeID: {request_data.mentee_id}")

            workout_service_logger.info(
                f"CREATE_WORKOUT_PLAN_SUCCESS | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id} | PlanID: {created_plan.id}"
            )
            return {"plan_id": str(created_plan.id)}

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"CREATE_WORKOUT_PLAN_ERROR | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating workout plan: {str(e)}"
            )

    @staticmethod
    async def update_workout_plan(plan_id: str, coach_id: str, request_data: CreateWorkoutPlanRequest) -> Dict[str, Any]:
        workout_service_logger.info(
            f"UPDATE_WORKOUT_PLAN_START | PlanID: {plan_id} | CoachID: {coach_id} | MenteeID: {request_data.mentee_id}"
        )

        try:
            existing_plan = await WorkoutPlanRepository.get_by_id(plan_id)
            if not existing_plan:
                workout_service_logger.warning(f"WORKOUT_PLAN_NOT_FOUND | PlanID: {plan_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workout plan not found"
                )

            if existing_plan.coach_id != coach_id:
                workout_service_logger.warning(
                    f"UPDATE_PLAN_ACCESS_DENIED | PlanID: {plan_id} | CoachID: {coach_id} | PlanCoachID: {existing_plan.coach_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own workout plans"
                )

            await WorkoutPlanService._validate_mentee_belongs_to_coach(
                coach_id, request_data.mentee_id
            )
            workout_service_logger.debug(
                f"MENTEE_VALIDATION_PASSED | CoachID: {coach_id} | MenteeID: {request_data.mentee_id}")

            update_data = {
                "trainingObjective": request_data.trainingObjective,
                "days": [day.dict() for day in request_data.days]
            }

            updated_plan = await WorkoutPlanRepository.update(plan_id, update_data)
            workout_service_logger.info(f"WORKOUT_PLAN_UPDATED | PlanID: {plan_id}")

            workout_service_logger.info(
                f"UPDATE_WORKOUT_PLAN_SUCCESS | PlanID: {plan_id} | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id}"
            )
            return {"plan_id": plan_id}

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"UPDATE_WORKOUT_PLAN_ERROR | PlanID: {plan_id} | CoachID: {coach_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating workout plan: {str(e)}"
            )

    @staticmethod
    async def get_workout_plan_by_id(plan_id: str, logged_user_id: str) -> Dict[str, Any]:
        workout_service_logger.info(f"GET_WORKOUT_PLAN_START | PlanID: {plan_id} | UserID: {logged_user_id}")

        try:
            plan = await WorkoutPlanRepository.get_by_id(plan_id)

            if not plan:
                workout_service_logger.warning(f"WORKOUT_PLAN_NOT_FOUND | PlanID: {plan_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workout plan not found"
                )

            if plan.coach_id != logged_user_id and plan.mentee_id != logged_user_id:
                workout_service_logger.warning(
                    f"WORKOUT_PLAN_ACCESS_DENIED | PlanID: {plan_id} | "
                    f"UserID: {logged_user_id} | CoachID: {plan.coach_id} | MenteeID: {plan.mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this workout plan"
                )

            workout_service_logger.info(f"GET_WORKOUT_PLAN_SUCCESS | PlanID: {plan_id}")
            return WorkoutPlanService._format_workout_plan_response(plan)

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"GET_WORKOUT_PLAN_ERROR | PlanID: {plan_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving workout plan: {str(e)}"
            )

    @staticmethod
    async def get_workout_plans_by_coach(coach_id: str, logged_user_id: str) -> list:
        workout_service_logger.info(f"GET_PLANS_BY_COACH_START | CoachID: {coach_id} | UserID: {logged_user_id}")

        try:
            if coach_id != logged_user_id:
                workout_service_logger.warning(
                    f"COACH_PLANS_ACCESS_DENIED | CoachID: {coach_id} | UserID: {logged_user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only access your own workout plans"
                )

            plans = await WorkoutPlanRepository.get_by_coach_id(coach_id)
            workout_service_logger.info(
                f"GET_PLANS_BY_COACH_SUCCESS | CoachID: {coach_id} | PlanCount: {len(plans)}"
            )
            return [WorkoutPlanService._format_workout_plan_response(plan) for plan in plans]

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"GET_PLANS_BY_COACH_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving workout plans: {str(e)}"
            )

    @staticmethod
    async def get_workout_plans_by_mentee(mentee_id: str, logged_user_id: str) -> list:
        workout_service_logger.info(f"GET_PLANS_BY_MENTEE_START | MenteeID: {mentee_id} | UserID: {logged_user_id}")

        try:
            if mentee_id != logged_user_id:
                mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)
                if not mentee_profile or mentee_profile.coach_id != logged_user_id:
                    workout_service_logger.warning(
                        f"MENTEE_PLANS_ACCESS_DENIED | MenteeID: {mentee_id} | UserID: {logged_user_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to access these workout plans"
                    )

            plans = await WorkoutPlanRepository.get_by_mentee_id(mentee_id)
            workout_service_logger.info(
                f"GET_PLANS_BY_MENTEE_SUCCESS | MenteeID: {mentee_id} | PlanCount: {len(plans)}"
            )
            return [WorkoutPlanService._format_workout_plan_response(plan) for plan in plans]

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"GET_PLANS_BY_MENTEE_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving workout plans: {str(e)}"
            )

    @staticmethod
    async def get_current_workout_plan_by_mentee(mentee_id: str, logged_user_id: str) -> Dict[str, Any]:
        workout_service_logger.info(f"GET_CURRENT_PLAN_START | MenteeID: {mentee_id} | UserID: {logged_user_id}")

        try:
            if mentee_id != logged_user_id:
                mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)
                if not mentee_profile or mentee_profile.coach_id != logged_user_id:
                    workout_service_logger.warning(
                        f"CURRENT_PLAN_ACCESS_DENIED | MenteeID: {mentee_id} | UserID: {logged_user_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to access this workout plan"
                    )

            plan = await WorkoutPlanRepository.get_active_plan_by_mentee(mentee_id)

            if not plan:
                workout_service_logger.warning(f"CURRENT_PLAN_NOT_FOUND | MenteeID: {mentee_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workout plan found for this mentee"
                )

            workout_service_logger.info(
                f"GET_CURRENT_PLAN_SUCCESS | MenteeID: {mentee_id} | PlanID: {plan.id}"
            )
            return WorkoutPlanService._format_workout_plan_response(plan)

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"GET_CURRENT_PLAN_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving current workout plan: {str(e)}"
            )

    @staticmethod
    def _format_workout_plan_response(plan) -> Dict[str, Any]:
        plan_dict = jsonable_encoder(plan)

        return {
            "_id": plan_dict["_id"],
            "coach_id": plan_dict["coach_id"],
            "mentee_id": plan_dict["mentee_id"],
            "created_at": plan_dict["created_at"],
            "workoutPlan": {
                "trainingObjective": plan_dict["trainingObjective"],
                "days": plan_dict["days"]
            }
        }

    @staticmethod
    async def _validate_mentee_belongs_to_coach(coach_id: str, mentee_id: str) -> None:
        workout_service_logger.debug(f"VALIDATING_MENTEE_COACH | CoachID: {coach_id} | MenteeID: {mentee_id}")

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)

            if not mentee_profile:
                workout_service_logger.warning(f"MENTEE_NOT_FOUND | MenteeID: {mentee_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee not found"
                )

            if mentee_profile.coach_id != coach_id:
                workout_service_logger.warning(
                    f"MENTEE_COACH_MISMATCH | MenteeID: {mentee_id} | "
                    f"ExpectedCoach: {coach_id} | ActualCoach: {mentee_profile.coach_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only create workout plans for your own mentees"
                )

            workout_service_logger.debug(
                f"MENTEE_COACH_VALIDATION_PASSED | CoachID: {coach_id} | MenteeID: {mentee_id}")

        except HTTPException:
            raise
        except Exception as e:
            workout_service_logger.error(
                f"MENTEE_COACH_VALIDATION_ERROR | CoachID: {coach_id} | "
                f"MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error validating mentee-coach relationship"
            )

    @staticmethod
    async def _update_mentee_workout_plan_status(mentee_id: str, plan_id: str) -> None:
        workout_service_logger.debug(f"UPDATING_MENTEE_STATUS | MenteeID: {mentee_id} | PlanID: {plan_id}")

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)

            if mentee_profile:
                mentee_profile.userPlans.workoutsPlan.active = True
                mentee_profile.userPlans.workoutsPlan.planId = plan_id
                await mentee_profile.save()
                workout_service_logger.debug(f"MENTEE_STATUS_UPDATED_SUCCESS | MenteeID: {mentee_id}")
            else:
                workout_service_logger.warning(f"MENTEE_NOT_FOUND_FOR_STATUS_UPDATE | MenteeID: {mentee_id}")

        except Exception as e:
            workout_service_logger.warning(
                f"MENTEE_STATUS_UPDATE_FAILED | MenteeID: {mentee_id} | "
                f"PlanID: {plan_id} | Error: {str(e)}"
            )