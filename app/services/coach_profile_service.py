import logging
from fastapi import HTTPException, status

from app.repositories.coach_profile_repository import CoachProfileRepository

coach_service_logger = logging.getLogger("dreamfit_api.coach_service")


class CoachProfileService:
    @staticmethod
    async def get_by_user_id(user_id: str):
        coach_service_logger.info(f"GET_COACH_PROFILE_START | UserID: {user_id}")

        try:
            profile = await CoachProfileRepository.get_by_user_id(user_id)

            if profile:
                coach_service_logger.info(f"GET_COACH_PROFILE_SUCCESS | UserID: {user_id}")
            else:
                coach_service_logger.warning(f"GET_COACH_PROFILE_NOT_FOUND | UserID: {user_id}")

            return profile

        except Exception as e:
            coach_service_logger.error(
                f"GET_COACH_PROFILE_ERROR | UserID: {user_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )