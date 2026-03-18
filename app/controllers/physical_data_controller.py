import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.physical_data_service import PhysicalDataService
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

physical_logger = logging.getLogger("dreamfit_api.physical_data")


class PhysicalDataController:
    router = APIRouter(prefix="/physical-data", tags=["Physical Data"])

    @staticmethod
    @router.get("/weight/{mentee_id}")
    async def get_weight_records(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        physical_logger.info(
            f"GET_WEIGHT_RECORDS | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            weight_records = await PhysicalDataService.get_weight_records_by_user_id(mentee_id)
            record_count = len(weight_records) if weight_records else 0

            physical_logger.info(
                f"GET_WEIGHT_RECORDS_SUCCESS | MenteeID: {mentee_id} | "
                f"RecordCount: {record_count} | IP: {client_ip}"
            )

            payload = {"weightRecords": weight_records}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            physical_logger.warning(
                f"GET_WEIGHT_RECORDS_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            physical_logger.error(
                f"GET_WEIGHT_RECORDS_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/{mentee_id}")
    async def get_body_measurements(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach, RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        physical_logger.info(
            f"GET_BODY_MEASUREMENTS | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            measurements = await PhysicalDataService.get_latest_body_measurements(mentee_id)
            measurement_count = len(measurements) if measurements else 0

            physical_logger.info(
                f"GET_BODY_MEASUREMENTS_SUCCESS | MenteeID: {mentee_id} | "
                f"MeasurementTypes: {measurement_count} | IP: {client_ip}"
            )

            payload = {"measurements": measurements}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException as e:
            physical_logger.warning(
                f"GET_BODY_MEASUREMENTS_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            physical_logger.error(
                f"GET_BODY_MEASUREMENTS_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )