import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.meal_plan_service import MealPlanService
from app.schemas.meal_plan_schema import CreateMealPlanRequest
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

meal_plan_logger = logging.getLogger("dreamfit_api.meal_plan")


class MealPlanController:
    router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])

    @staticmethod
    @router.post("")
    async def create_meal_plan(
            request_data: CreateMealPlanRequest,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        meal_plan_logger.info(
            f"CREATE_MEAL_PLAN | CoachID: {logged_user_id} | "
            f"MenteeID: {request_data.mentee_id} | Days: {request_data.days} | "
            f"MealsPerDay: {request_data.meals_per_day} | IP: {client_ip}"
        )

        try:
            result = await MealPlanService.create_meal_plan(
                coach_id=logged_user_id,
                request_data=request_data
            )

            meal_plan_logger.info(
                f"CREATE_MEAL_PLAN_SUCCESS | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | PlanID: {result.get('plan_id')} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=ResponsePayload.create("Plan de alimentación creado exitosamente", result)
            )

        except HTTPException as e:
            meal_plan_logger.warning(
                f"CREATE_MEAL_PLAN_HTTP_ERROR | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )

        except Exception as e:
            meal_plan_logger.error(
                f"CREATE_MEAL_PLAN_ERROR | CoachID: {logged_user_id} | "
                f"MenteeID: {request_data.mentee_id} | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Error interno del servidor", {})
            )

    @staticmethod
    @router.get("/mentee/{mentee_id}")
    async def get_meal_plan(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        meal_plan_logger.info(
            f"GET_MEAL_PLAN | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            meal_plan = await MealPlanService.get_meal_plan_by_mentee(
                mentee_id=mentee_id,
                logged_user_id=logged_user_id
            )

            meal_plan_logger.info(
                f"GET_MEAL_PLAN_SUCCESS | MenteeID: {mentee_id} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", meal_plan)
            )

        except HTTPException as e:
            meal_plan_logger.warning(
                f"GET_MEAL_PLAN_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )

        except Exception as e:
            meal_plan_logger.error(
                f"GET_MEAL_PLAN_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Error interno del servidor", {})
            )