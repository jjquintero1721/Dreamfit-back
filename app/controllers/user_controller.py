import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.services.user_service import UserService
from app.schemas.user_schemas import (
    UpdateUserRequest,
    UserProfileResponse,
    ChangePasswordRequest,
    UpdatePasswordRequest,
)
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles, get_current_user
from app.utils.enums import RoleName

user_logger = logging.getLogger("dreamfit_api.user")


class UserController:
    router = APIRouter(prefix="/user", tags=["User"])

    @staticmethod
    @router.get("/profile")
    async def get_user_profile(
            request: Request,
            current_user=Depends(get_current_user)
    ):
        client_ip = request.client.host if request.client else "unknown"

        user_logger.info(
            f"GET_USER_PROFILE | UserID: {current_user['userId']} | "
            f"IP: {client_ip}"
        )

        try:
            user_profile = await UserService.get_user_profile(current_user['userId'])

            user_logger.info(
                f"GET_USER_PROFILE_SUCCESS | UserID: {current_user['userId']} | "
                f"IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", user_profile)
            )

        except HTTPException as e:
            user_logger.warning(
                f"GET_USER_PROFILE_HTTP_ERROR | UserID: {current_user['userId']} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            user_logger.error(
                f"GET_USER_PROFILE_ERROR | UserID: {current_user['userId']} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.patch("/profile")
    async def update_user_profile(
            update_data: UpdateUserRequest,
            request: Request,
            current_user=Depends(get_current_user)
    ):
        client_ip = request.client.host if request.client else "unknown"

        user_logger.info(
            f"UPDATE_USER_PROFILE | UserID: {current_user['userId']} | "
            f"IP: {client_ip}"
        )

        try:
            updated_profile = await UserService.update_user_profile(
                user_id=current_user['userId'],
                role=current_user['role'],
                update_data=update_data
            )

            user_logger.info(
                f"UPDATE_USER_PROFILE_SUCCESS | UserID: {current_user['userId']} | "
                f"IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Perfil actualizado exitosamente", updated_profile)
            )

        except HTTPException as e:
            user_logger.warning(
                f"UPDATE_USER_PROFILE_HTTP_ERROR | UserID: {current_user['userId']} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            user_logger.error(
                f"UPDATE_USER_PROFILE_ERROR | UserID: {current_user['userId']} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/change-password")
    async def change_password(
            password_data: ChangePasswordRequest,
            request: Request,
            current_user=Depends(get_current_user)
    ):
        client_ip = request.client.host if request.client else "unknown"

        user_logger.info(
            f"CHANGE_PASSWORD | UserID: {current_user['userId']} | "
            f"IP: {client_ip}"
        )

        try:
            await UserService.change_password(
                user_id=current_user['userId'],
                current_password=password_data.current_password,
                new_password=password_data.new_password
            )

            user_logger.info(
                f"CHANGE_PASSWORD_SUCCESS | UserID: {current_user['userId']} | "
                f"IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Contraseña actualizada exitosamente", {})
            )

        except HTTPException as e:
            user_logger.warning(
                f"CHANGE_PASSWORD_HTTP_ERROR | UserID: {current_user['userId']} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            user_logger.error(
                f"CHANGE_PASSWORD_ERROR | UserID: {current_user['userId']} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/actualizar-password/{user_id}")
    async def update_password_by_id(
            user_id: str,
            password_data: UpdatePasswordRequest,
            request: Request,
    ):
        client_ip = request.client.host if request.client else "unknown"

        user_logger.info(
            f"UPDATE_PASSWORD_BY_ID | UserID: {user_id} | "
            f"IP: {client_ip}"
        )

        try:
            await UserService.update_password_by_id(
                user_id=user_id,
                new_password=password_data.new_password
            )

            user_logger.info(
                f"UPDATE_PASSWORD_BY_ID_SUCCESS | UserID: {user_id} | "
                f"IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Contraseña actualizada exitosamente", {})
            )

        except HTTPException as e:
            user_logger.warning(
                f"UPDATE_PASSWORD_BY_ID_HTTP_ERROR | UserID: {user_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception:
            user_logger.exception(
                f"UPDATE_PASSWORD_BY_ID_ERROR | UserID: {user_id} | "
                f"Unexpected error | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )
