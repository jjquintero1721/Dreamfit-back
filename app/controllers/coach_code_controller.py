import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.repositories.coach_code_repository import CoachCodeRepository
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles
from app.utils.enums import RoleName

coach_code_logger = logging.getLogger("dreamfit_api.coach_code")


class CoachCodeController:
    router = APIRouter(prefix="/coach-code", tags=["Coach Code"])

    @staticmethod
    @router.get("/my-code")
    async def get_my_coach_code(
        request: Request,
        logged_user_id: str = Depends(require_roles([RoleName.coach]))
    ):
        """
        Obtiene el código actualizado del coach desde la base de datos
        """
        client_ip = request.client.host if request.client else "unknown"

        coach_code_logger.info(
            f"GET_MY_CODE | CoachID: {logged_user_id} | IP: {client_ip}"
        )

        try:
            coach_code = await CoachCodeRepository.get_by_user_id(logged_user_id)

            if not coach_code:
                coach_code_logger.warning(
                    f"GET_MY_CODE_NOT_FOUND | CoachID: {logged_user_id} | IP: {client_ip}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coach code not found"
                )

            coach_code_logger.info(
                f"GET_MY_CODE_SUCCESS | CoachID: {logged_user_id} | "
                f"Code: {coach_code.code} | IP: {client_ip}"
            )

            payload = {"code": coach_code.code}
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", payload)
            )

        except HTTPException:
            raise
        except Exception as e:
            coach_code_logger.error(
                f"GET_MY_CODE_ERROR | CoachID: {logged_user_id} | "
                f"Error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )