import logging
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.services.mentee_profile_service import MenteeProfileService
from app.schemas.physical_data_schema import RequestPhysicalData
from app.schemas.response_schemas import ResponsePayload
from app.schemas.mentee_profile_schema import MenteeProfileResponse, UpdateMenteeProfileRequest, \
    MenteeProfileUpdateResponse
from app.security.auth_middleware import require_roles
from app.utils.requestor_utils import RequestorUtils
from app.utils.enums import RoleName

mentee_logger = logging.getLogger("dreamfit_api.mentee_profile")


class MenteeProfileController:
    router = APIRouter(prefix="/mentees", tags=["Mentees"])

    @staticmethod
    @router.get("/{coach_id}")
    async def get_by_coach(
            coach_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        mentee_logger.info(
            f"GET_MENTEES_BY_COACH | CoachID: {coach_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            RequestorUtils.validate_requestor_id(logged_user_id, coach_id)
            mentee_logger.debug(f"REQUESTOR_VALIDATION_PASSED | CoachID: {coach_id}")

            mentees = await MenteeProfileService.get_by_coach(coach_id)
            mentee_count = len(mentees) if mentees else 0

            mentee_logger.info(
                f"GET_MENTEES_SUCCESS | CoachID: {coach_id} | "
                f"MenteeCount: {mentee_count} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", mentees)
            )

        except HTTPException as e:
            mentee_logger.warning(
                f"GET_MENTEES_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            mentee_logger.error(
                f"GET_MENTEES_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.patch("/{mentee_id}")
    async def update_mentee_profile(
            mentee_id: str,
            update_data: UpdateMenteeProfileRequest,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        mentee_logger.info(
            f"UPDATE_MENTEE_PROFILE | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        update_fields = []
        if update_data.age: update_fields.append("age")
        if update_data.gender: update_fields.append("gender")
        if update_data.height: update_fields.append("height")
        if update_data.supplements: update_fields.append("supplements")
        if update_data.weeklyExerciseFrequency: update_fields.append("weeklyExerciseFrequency")
        if update_data.activityLevel: update_fields.append("activityLevel")

        mentee_logger.debug(
            f"UPDATE_FIELDS | MenteeID: {mentee_id} | Fields: {update_fields}"
        )

        try:
            RequestorUtils.validate_requestor_id(logged_user_id, mentee_id)
            mentee_logger.debug(f"REQUESTOR_VALIDATION_PASSED | MenteeID: {mentee_id}")

            updated_profile = await MenteeProfileService.update_profile(mentee_id, update_data)

            mentee_logger.info(
                f"UPDATE_MENTEE_SUCCESS | MenteeID: {mentee_id} | "
                f"UpdatedFields: {update_fields} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create(
                    "OK",
                    jsonable_encoder(updated_profile, exclude={"id", "user_id", "coach_id"})
                )
            )

        except HTTPException as e:
            mentee_logger.warning(
                f"UPDATE_MENTEE_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            mentee_logger.error(
                f"UPDATE_MENTEE_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/physical-data/{mentee_id}")
    async def add_physical_data(
            mentee_id: str,
            request_data: RequestPhysicalData,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.mentee]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        mentee_logger.info(
            f"ADD_PHYSICAL_DATA | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        data_types = []
        if request_data.weight: data_types.append("weight")
        if request_data.chest: data_types.append("chest")
        if request_data.waist: data_types.append("waist")
        if request_data.hips: data_types.append("hips")
        if request_data.neck: data_types.append("neck")
        if request_data.leg: data_types.append("leg")
        if request_data.arms: data_types.append("arms")
        if request_data.calves: data_types.append("calves")

        mentee_logger.debug(
            f"PHYSICAL_DATA_TYPES | MenteeID: {mentee_id} | Types: {data_types}"
        )

        try:
            RequestorUtils.validate_requestor_id(logged_user_id, mentee_id)
            mentee_logger.debug(f"REQUESTOR_VALIDATION_PASSED | MenteeID: {mentee_id}")

            await MenteeProfileService.add_physical_data(request_data, mentee_id)

            mentee_logger.info(
                f"ADD_PHYSICAL_DATA_SUCCESS | MenteeID: {mentee_id} | "
                f"DataTypes: {data_types} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=ResponsePayload.create("CREATED")
            )

        except HTTPException as e:
            mentee_logger.warning(
                f"ADD_PHYSICAL_DATA_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            mentee_logger.error(
                f"ADD_PHYSICAL_DATA_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/info/{mentee_id}")
    async def get_mentee_info(
            mentee_id: str,
            request: Request,
            logged_user_id: str = Depends(require_roles([RoleName.mentee, RoleName.coach]))
    ):
        client_ip = request.client.host if request.client else "unknown"

        mentee_logger.info(
            f"GET_MENTEE_INFO | MenteeID: {mentee_id} | "
            f"RequestedBy: {logged_user_id} | IP: {client_ip}"
        )

        try:
            profile = await MenteeProfileService.get_by_user_id(mentee_id)

            mentee_logger.info(
                f"GET_MENTEE_INFO_SUCCESS | MenteeID: {mentee_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", profile)
            )

        except HTTPException as e:
            mentee_logger.warning(
                f"GET_MENTEE_INFO_HTTP_ERROR | MenteeID: {mentee_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            mentee_logger.error(
                f"GET_MENTEE_INFO_ERROR | MenteeID: {mentee_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )