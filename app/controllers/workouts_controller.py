import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.workout_plan_service import WorkoutPlanService
from app.schemas.workout_plan_schema import CreateWorkoutPlanRequest
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

workouts_logger = logging.getLogger("dreamfit_api.workouts")


class WorkoutsController:
    router = APIRouter(prefix="/workout-plans", tags=["Workout Plans"])

    @staticmethod
    @router.post("")
    async def create_workout_plan(
            request_data: CreateWorkoutPlanRequest,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"CREATE_WORKOUT_PLAN | CoachID: {logged_user_id} | "
            f"MenteeID: {request_data.mentee_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.create_workout_plan(
                coach_id=logged_user_id,
                request_data=request_data
            )

            workouts_logger.info(
                f"CREATE_WORKOUT_PLAN_SUCCESS | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | PlanID: {result.get('plan_id')} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=ResponsePayload.create("Workout plan created successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"CREATE_WORKOUT_PLAN_HTTP_ERROR | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )

        except Exception as e:
            workouts_logger.error(
                f"CREATE_WORKOUT_PLAN_ERROR | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponsePayload.create("Error creating workout plan", {})
            )

    @staticmethod
    @router.put("/{plan_id}")
    async def update_workout_plan(
            plan_id: str,
            request_data: CreateWorkoutPlanRequest,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"UPDATE_WORKOUT_PLAN | PlanID: {plan_id} | CoachID: {logged_user_id} | "
            f"MenteeID: {request_data.mentee_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.update_workout_plan(
                plan_id=plan_id,
                coach_id=logged_user_id,
                request_data=request_data
            )

            workouts_logger.info(
                f"UPDATE_WORKOUT_PLAN_SUCCESS | PlanID: {plan_id} | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Workout plan updated successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"UPDATE_WORKOUT_PLAN_HTTP_ERROR | PlanID: {plan_id} | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )

        except Exception as e:
            workouts_logger.error(
                f"UPDATE_WORKOUT_PLAN_ERROR | PlanID: {plan_id} | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponsePayload.create("Error updating workout plan", {})
            )

    @staticmethod
    @router.get("/{plan_id}")
    async def get_workout_plan(
            plan_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"GET_WORKOUT_PLAN | PlanID: {plan_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.get_workout_plan_by_id(plan_id, logged_user_id)

            workouts_logger.info(
                f"GET_WORKOUT_PLAN_SUCCESS | PlanID: {plan_id} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Workout plan retrieved successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"GET_WORKOUT_PLAN_HTTP_ERROR | PlanID: {plan_id} | "
                f"RequestedBy: {logged_user_id} | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            workouts_logger.error(
                f"GET_WORKOUT_PLAN_ERROR | PlanID: {plan_id} | "
                f"RequestedBy: {logged_user_id} | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/coach/{coach_id}")
    async def get_coach_workout_plans(
            coach_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"GET_COACH_WORKOUT_PLANS | CoachID: {coach_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.get_workout_plans_by_coach(coach_id, logged_user_id)
            plan_count = len(result) if result else 0

            workouts_logger.info(
                f"GET_COACH_WORKOUT_PLANS_SUCCESS | CoachID: {coach_id} | "
                f"PlanCount: {plan_count} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Workout plans retrieved successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"GET_COACH_WORKOUT_PLANS_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            workouts_logger.error(
                f"GET_COACH_WORKOUT_PLANS_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/mentee/{mentee_id}")
    async def get_mentee_workout_plans(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"GET_MENTEE_WORKOUT_PLANS | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.get_workout_plans_by_mentee(mentee_id, logged_user_id)
            plan_count = len(result) if result else 0

            workouts_logger.info(
                f"GET_MENTEE_WORKOUT_PLANS_SUCCESS | MenteeID: {mentee_id} | "
                f"PlanCount: {plan_count} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Workout plans retrieved successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"GET_MENTEE_WORKOUT_PLANS_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            workouts_logger.error(
                f"GET_MENTEE_WORKOUT_PLANS_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/current/{mentee_id}")
    async def get_current_workout_plan(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        workouts_logger.info(
            f"GET_CURRENT_WORKOUT_PLAN | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            result = await WorkoutPlanService.get_current_workout_plan_by_mentee(mentee_id, logged_user_id)

            workouts_logger.info(
                f"GET_CURRENT_WORKOUT_PLAN_SUCCESS | MenteeID: {mentee_id} | "
                f"PlanID: {result.get('_id')} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Current workout plan retrieved successfully", result)
            )

        except HTTPException as e:
            workouts_logger.warning(
                f"GET_CURRENT_WORKOUT_PLAN_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            workouts_logger.error(
                f"GET_CURRENT_WORKOUT_PLAN_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )