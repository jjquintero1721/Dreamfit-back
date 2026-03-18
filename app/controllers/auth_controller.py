import logging
from fastapi import APIRouter, status, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.user_service import UserService
from app.schemas.auth_schemas import SignupRequest, LoginRequest, TokenRefreshRequest
from app.schemas.response_schemas import ResponsePayload

auth_logger = logging.getLogger("dreamfit_api.auth")


class AuthController:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    @staticmethod
    @router.post("/signup")
    async def signup(signup_data: SignupRequest, request: Request):
        client_ip = request.client.host if request.client else "unknown"

        auth_logger.info(
            f"SIGNUP_ATTEMPT | Email: {signup_data.email} | "
            f"Role: {signup_data.role} | IP: {client_ip}"
        )

        try:
            await UserService.signup(
                email=signup_data.email,
                password=signup_data.password,
                role=signup_data.role,
                name=signup_data.first_name,
                last_name=signup_data.last_name,
                coach_code=signup_data.coach_code
            )

            auth_logger.info(
                f"SIGNUP_SUCCESS | Email: {signup_data.email} | "
                f"Role: {signup_data.role} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=ResponsePayload.create("User created successfully", {})
            )

        except HTTPException as e:
            auth_logger.warning(
                f"SIGNUP_FAILED | Email: {signup_data.email} | "
                f"Role: {signup_data.role} | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            auth_logger.error(
                f"SIGNUP_ERROR | Email: {signup_data.email} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/login")
    async def login(login_data: LoginRequest, request: Request):
        client_ip = request.client.host if request.client else "unknown"

        auth_logger.info(
            f"LOGIN_ATTEMPT | Email: {login_data.email} | IP: {client_ip}"
        )

        try:
            tokens = await UserService.login(
                email=login_data.email,
                password=login_data.password
            )

            auth_logger.info(
                f"LOGIN_SUCCESS | Email: {login_data.email} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("User logged in successfully", tokens)
            )

        except HTTPException as e:
            if e.status_code == 401:
                auth_logger.warning(
                    f"LOGIN_INVALID_CREDENTIALS | Email: {login_data.email} | IP: {client_ip}"
                )
            else:
                auth_logger.warning(
                    f"LOGIN_FAILED | Email: {login_data.email} | "
                    f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
                )

            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            auth_logger.error(
                f"LOGIN_ERROR | Email: {login_data.email} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/refresh")
    async def refresh_token(token_request: TokenRefreshRequest, request: Request):
        client_ip = request.client.host if request.client else "unknown"

        auth_logger.info(f"TOKEN_REFRESH_ATTEMPT | IP: {client_ip}")

        try:
            tokens = await UserService.refresh_token(token_request.refresh_token)

            auth_logger.info(f"TOKEN_REFRESH_SUCCESS | IP: {client_ip}")

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Tokens refreshed", tokens)
            )

        except HTTPException as e:
            auth_logger.warning(
                f"TOKEN_REFRESH_FAILED | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            auth_logger.error(
                f"TOKEN_REFRESH_ERROR | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )