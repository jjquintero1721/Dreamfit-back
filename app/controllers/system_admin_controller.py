import logging
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.system_admin_service import SystemAdminService
from app.services.content_service import ContentService
from app.schemas.system_admin_schemas import (
    AssignMembershipRequest,
    UpdateCoachPasswordRequest
)
from app.schemas.response_schemas import ResponsePayload
from app.security.auth_middleware import require_roles

system_admin_logger = logging.getLogger("dreamfit_api.system_admin")


class SystemAdminController:
    router = APIRouter(prefix="/system-admin", tags=["System Admin"])

    @staticmethod
    @router.get("/coaches")
    async def get_all_coaches(
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Obtener todos los coaches del sistema"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"GET_ALL_COACHES | IP: {client_ip}"
        )

        try:
            coaches = await SystemAdminService.get_all_coaches()

            system_admin_logger.info(
                f"GET_ALL_COACHES_SUCCESS | Count: {len(coaches)} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create(
                    "OK",
                    [coach.model_dump(mode='json', by_alias=True) for coach in coaches]
                )
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"GET_ALL_COACHES_HTTP_ERROR | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"GET_ALL_COACHES_ERROR | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/coaches/{coach_id}")
    async def get_coach_details(
        coach_id: str,
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Obtener detalles completos de un coach"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"GET_COACH_DETAILS | CoachID: {coach_id} | IP: {client_ip}"
        )

        try:
            coach_details = await SystemAdminService.get_coach_details(coach_id)

            system_admin_logger.info(
                f"GET_COACH_DETAILS_SUCCESS | CoachID: {coach_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", coach_details.model_dump(mode='json', by_alias=True))
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"GET_COACH_DETAILS_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"GET_COACH_DETAILS_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/coaches/{coach_id}/mentees")
    async def get_coach_mentees(
        coach_id: str,
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Obtener todos los mentees de un coach"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"GET_COACH_MENTEES | CoachID: {coach_id} | IP: {client_ip}"
        )

        try:
            mentees = await SystemAdminService.get_coach_mentees(coach_id)

            system_admin_logger.info(
                f"GET_COACH_MENTEES_SUCCESS | CoachID: {coach_id} | "
                f"Count: {len(mentees)} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create(
                    "OK",
                    [mentee.model_dump(mode='json', by_alias=True) for mentee in mentees]
                )
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"GET_COACH_MENTEES_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"GET_COACH_MENTEES_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.post("/coaches/{coach_id}/membership")
    async def assign_membership(
        coach_id: str,
        membership_data: AssignMembershipRequest,
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Asignar o cambiar la membresía de un coach"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"ASSIGN_MEMBERSHIP | CoachID: {coach_id} | "
            f"PlanID: {membership_data.plan_id} | IP: {client_ip}"
        )

        try:
            result = await SystemAdminService.assign_membership(
                coach_id=coach_id,
                plan_id=membership_data.plan_id,
                duration_months=membership_data.duration_months
            )

            system_admin_logger.info(
                f"ASSIGN_MEMBERSHIP_SUCCESS | CoachID: {coach_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Membership assigned successfully", result)
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"ASSIGN_MEMBERSHIP_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"ASSIGN_MEMBERSHIP_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.delete("/coaches/{coach_id}/membership")
    async def cancel_membership(
        coach_id: str,
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Cancelar la membresía de un coach"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"CANCEL_MEMBERSHIP | CoachID: {coach_id} | IP: {client_ip}"
        )

        try:
            result = await SystemAdminService.cancel_membership(coach_id)

            system_admin_logger.info(
                f"CANCEL_MEMBERSHIP_SUCCESS | CoachID: {coach_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Membership canceled successfully", result)
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"CANCEL_MEMBERSHIP_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"CANCEL_MEMBERSHIP_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.patch("/coaches/{coach_id}/password")
    async def update_coach_password(
        coach_id: str,
        password_data: UpdateCoachPasswordRequest,
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Cambiar la contraseña de un coach"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(
            f"UPDATE_COACH_PASSWORD | CoachID: {coach_id} | IP: {client_ip}"
        )

        try:
            result = await SystemAdminService.update_coach_password(
                coach_id=coach_id,
                new_password=password_data.new_password
            )

            system_admin_logger.info(
                f"UPDATE_COACH_PASSWORD_SUCCESS | CoachID: {coach_id} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("Password updated successfully", result)
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"UPDATE_COACH_PASSWORD_HTTP_ERROR | CoachID: {coach_id} | "
                f"Error: {e.detail} | Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"UPDATE_COACH_PASSWORD_ERROR | CoachID: {coach_id} | "
                f"Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )

    @staticmethod
    @router.get("/plans")
    async def get_plans(
        request: Request,
        _=Depends(require_roles(["system"]))
    ):
        """Obtener todos los planes disponibles del CMS"""
        client_ip = request.client.host if request.client else "unknown"

        system_admin_logger.info(f"GET_PLANS | IP: {client_ip}")

        try:
            plans = await ContentService.get_plans()

            system_admin_logger.info(
                f"GET_PLANS_SUCCESS | Count: {len(plans)} | IP: {client_ip}"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResponsePayload.create("OK", plans)
            )

        except HTTPException as e:
            system_admin_logger.warning(
                f"GET_PLANS_HTTP_ERROR | Error: {e.detail} | "
                f"Status: {e.status_code} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ResponsePayload.create(e.detail, {})
            )
        except Exception as e:
            system_admin_logger.error(
                f"GET_PLANS_ERROR | Unexpected error: {str(e)} | IP: {client_ip}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponsePayload.create("Internal server error", {})
            )
