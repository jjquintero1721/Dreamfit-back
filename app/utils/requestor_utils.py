import logging
from fastapi import HTTPException, status

requestor_logger = logging.getLogger("dreamfit_api.requestor_utils")


class RequestorUtils:
    @staticmethod
    def validate_requestor_id(logged_user_id: str, request_id: str):
        requestor_logger.debug(f"VALIDATING_REQUESTOR | LoggedID: {logged_user_id} | RequestID: {request_id}")

        if str(logged_user_id) != str(request_id):
            requestor_logger.warning(
                f"REQUESTOR_ID_MISMATCH | LoggedID: {logged_user_id} | RequestID: {request_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Data access denied"
            )

        requestor_logger.debug(f"REQUESTOR_VALIDATION_PASSED | UserID: {logged_user_id}")