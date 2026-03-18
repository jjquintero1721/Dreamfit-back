import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.content_service import ContentService
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

content_logger = logging.getLogger("dreamfit_api.content")


class ContentController:
    router = APIRouter(prefix="/content", tags=["Content"])

    @staticmethod
    @router.get("/workouts")
    async def get_workouts(
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        content_logger.info(
            f"GET_WORKOUTS | RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            workouts = await ContentService.get_workouts()
            workout_count = len(workouts) if workouts else 0

            content_logger.info(
                f"GET_WORKOUTS_SUCCESS | Count: {workout_count} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )

            payload = {"muscularGroups": workouts}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            content_logger.warning(
                f"GET_WORKOUTS_HTTP_ERROR | Error: {e.detail} | "
                f"Status: {e.status_code} | RequestedBy: {logged_user_id} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            content_logger.error(
                f"GET_WORKOUTS_ERROR | Unexpected error: {str(e)} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/training-options")
    async def get_training_options(
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        content_logger.info(
            f"GET_TRAINING_OPTIONS | RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            training_options = await ContentService.get_training_options()

            elements_count = len(training_options.get("elements", []))
            technics_count = len(training_options.get("technics", []))
            rirs_count = len(training_options.get("rirs", []))

            content_logger.info(
                f"GET_TRAINING_OPTIONS_SUCCESS | Elements: {elements_count} | "
                f"Technics: {technics_count} | RIRs: {rirs_count} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", training_options)
            )

        except HTTPException as e:
            content_logger.warning(
                f"GET_TRAINING_OPTIONS_HTTP_ERROR | Error: {e.detail} | "
                f"Status: {e.status_code} | RequestedBy: {logged_user_id} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            content_logger.error(
                f"GET_TRAINING_OPTIONS_ERROR | Unexpected error: {str(e)} | "
                f"RequestedBy: {logged_user_id} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/plans")
    async def get_plans(request: Request):
        client_ip = request.client.host if request.client else "unknown"

        content_logger.info(
            f"GET_PLANS | IP: {client_ip}"
        )

        try:
            plans = await ContentService.get_plans()
            plan_count = len(plans) if plans else 0

            content_logger.info(
                f"GET_PLANS_SUCCESS | Count: {plan_count} | IP: {client_ip}"
            )

            payload = {"plans": plans}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            content_logger.warning(
                f"GET_PLANS_HTTP_ERROR | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            content_logger.error(
                f"GET_PLANS_ERROR | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )