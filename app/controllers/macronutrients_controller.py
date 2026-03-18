import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.macronutrients_service import MacronutrientsService
from app.schemas.macronutrients_schema import (
    MacronutrientsCalculationRequest,
    MacronutrientsCalculationResponse,
    MacronutrientsResponse
)
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

macronutrients_logger = logging.getLogger("dreamfit_api.macronutrients")


class MacronutrientsController:
    router = APIRouter(prefix="/macronutrients", tags=["Macronutrients"])

    @staticmethod
    @router.post("/calculate")
    async def calculate_macronutrients(
            data: MacronutrientsCalculationRequest,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        macronutrients_logger.info(
            f"CALCULATE_MACRONUTRIENTS | MenteeID: {data.mentee_id} | "
            f"Weight: {data.weight}kg | Objective: {data.objective} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            result = await MacronutrientsService.calculate_and_save_macronutrients(data, logged_user_id)

            macronutrients_logger.info(
                f"CALCULATE_MACRONUTRIENTS_SUCCESS | MenteeID: {data.mentee_id} | "
                f"Calories: {result.final_calories} | MacroID: {result.macronutrients.id} | IP: {client_ip}"
            )

            payload = {"calculation": result.model_dump()}
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=ResponsePayload.create("Macronutrients calculated successfully", payload)
            )

        except HTTPException as e:
            macronutrients_logger.warning(
                f"CALCULATE_MACRONUTRIENTS_HTTP_ERROR | MenteeID: {data.mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            macronutrients_logger.error(
                f"CALCULATE_MACRONUTRIENTS_ERROR | MenteeID: {data.mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/mentee/{mentee_id}")
    async def get_macronutrients_by_mentee(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        macronutrients_logger.info(
            f"GET_MACRONUTRIENTS_BY_MENTEE | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            macronutrients_list = await MacronutrientsService.get_macronutrients_by_mentee(
                mentee_id, logged_user_id
            )

            macronutrients_logger.info(
                f"GET_MACRONUTRIENTS_BY_MENTEE_SUCCESS | MenteeID: {mentee_id} | "
                f"Count: {len(macronutrients_list)} | IP: {client_ip}"
            )

            payload = {"macronutrients": [macro.model_dump() for macro in macronutrients_list]}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            macronutrients_logger.warning(
                f"GET_MACRONUTRIENTS_BY_MENTEE_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            macronutrients_logger.error(
                f"GET_MACRONUTRIENTS_BY_MENTEE_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/mentee/{mentee_id}/latest")
    async def get_latest_macronutrients_by_mentee(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        macronutrients_logger.info(
            f"GET_LATEST_MACRONUTRIENTS | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            latest_macronutrients = await MacronutrientsService.get_latest_macronutrients_by_mentee(
                mentee_id, logged_user_id
            )

            macronutrients_logger.info(
                f"GET_LATEST_MACRONUTRIENTS_SUCCESS | MenteeID: {mentee_id} | "
                f"MacroID: {latest_macronutrients.id} | IP: {client_ip}"
            )

            payload = {"macronutrients": latest_macronutrients.model_dump()}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            macronutrients_logger.warning(
                f"GET_LATEST_MACRONUTRIENTS_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            macronutrients_logger.error(
                f"GET_LATEST_MACRONUTRIENTS_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )