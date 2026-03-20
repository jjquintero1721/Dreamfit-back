# Importar instrument.py PRIMERO para inicializar Sentry
from app import instrument

import asyncio
import logging
import time
import traceback
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
from contextlib import asynccontextmanager
import sentry_sdk

from app.config import init_db, app_logger
from app.controllers.content_controller import ContentController
from app.controllers.auth_controller import AuthController
from app.controllers.mentee_profile_controller import MenteeProfileController
from app.controllers.user_controller import UserController
from app.controllers.workouts_controller import WorkoutsController
from app.controllers.physical_data_controller import PhysicalDataController
from app.schemas.response_schemas import ResponsePayload
from app.controllers.macronutrients_controller import MacronutrientsController
from app.controllers.meal_plan_controller import MealPlanController
from app.controllers.system_admin_controller import SystemAdminController
from app.repositories.coach_profile_repository import CoachProfileRepository

load_dotenv(find_dotenv())


@asynccontextmanager
async def lifespan(app: FastAPI):

    app_logger.info("=== INICIANDO DREAMFIT API ===")

    try:
        await init_db()
        app_logger.info("DATABASE_INITIALIZED | Base de datos conectada")
        app_logger.info("=== API INICIADA CORRECTAMENTE ===")

    except Exception as e:
        app_logger.critical(f"CRITICAL_ERROR_STARTUP | Error: {str(e)}")
        raise e

    yield

    app_logger.info("=== CERRANDO DREAMFIT API ===")


app = FastAPI(title="DreamFit App API", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://www.fitconnectpro.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    app_logger.info(
        f"REQUEST | {request.method} {request.url.path} | "
        f"IP: {client_ip} | User-Agent: {user_agent[:50]}..."
    )

    if request.query_params:
        app_logger.info(f"QUERY_PARAMS | {dict(request.query_params)}")

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        app_logger.info(
            f"RESPONSE | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Time: {process_time:.3f}s"
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time

        # Sentry captura automáticamente la excepción con el contexto de FastAPI
        sentry_sdk.capture_exception(e)

        app_logger.error(
            f"UNHANDLED_ERROR | {request.method} {request.url.path} | "
            f"Time: {process_time:.3f}s | Error: {str(e)}"
        )
        app_logger.error(f"TRACEBACK | {traceback.format_exc()}")

        return JSONResponse(
            status_code=500,
            content=ResponsePayload.create("Internal server error", {})
        )


@app.middleware("http")
async def auth_error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)

        if response.status_code == 401:
            app_logger.warning(
                f"AUTH_FAILED | {request.method} {request.url.path} | "
                f"IP: {request.client.host if request.client else 'unknown'}"
            )
        elif response.status_code == 403:
            app_logger.warning(
                f"FORBIDDEN | {request.method} {request.url.path} | "
                f"IP: {request.client.host if request.client else 'unknown'}"
            )

        return response
    except Exception as e:
        app_logger.error(f"AUTH_MIDDLEWARE_ERROR | Error: {str(e)}")
        return await call_next(request)


app.include_router(ContentController.router)
app.include_router(AuthController.router)
app.include_router(MenteeProfileController.router)
app.include_router(WorkoutsController.router)
app.include_router(PhysicalDataController.router)
app.include_router(MacronutrientsController.router)
app.include_router(MealPlanController.router)
app.include_router(UserController.router)
app.include_router(SystemAdminController.router)


_daily_reset_task = None


@app.on_event("startup")
async def on_startup():
    app_logger.info("=== INICIANDO DREAMFIT API ===")
    try:
        await init_db()
        app_logger.info("=== API INICIADA CORRECTAMENTE ===")
        global _daily_reset_task
        _daily_reset_task = asyncio.create_task(_start_daily_reset_job())
    except Exception as e:
        app_logger.critical(f"CRITICAL ERROR AL INICIAR LA API: {str(e)}")
        raise e


@app.on_event("shutdown")
async def on_shutdown():
    app_logger.info("=== CERRANDO DREAMFIT API ===")
    global _daily_reset_task
    if _daily_reset_task:
        _daily_reset_task.cancel()
        with suppress(asyncio.CancelledError):
            await _daily_reset_task
        _daily_reset_task = None


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación"""
    app_logger.info("HEALTH_CHECK | Status requested")
    return {
        "status": "healthy",
        "service": "dreamfit-api",
        "timestamp": time.time()
    }


#@app.get("/sentry-debug")
#async def trigger_sentry_error():
    #"""
    #Endpoint de prueba para verificar que Sentry está funcionando correctamente.
    #Solo debe usarse en desarrollo.

    #IMPORTANTE: Deshabilitar o eliminar este endpoint en producción.
    #"""
    #app_logger.info("SENTRY_DEBUG | Triggering test error")
    #division_by_zero = 1 / 0
    #return {"message": "This should not be returned"}


async def _start_daily_reset_job():
    app_logger.info("DAILY_RESET_JOB_STARTED")
    while True:
        seconds = _seconds_until_next_midnight()
        await asyncio.sleep(seconds)
        await _reset_daily_meal_plan_counts()


def _seconds_until_next_midnight() -> float:
    now = datetime.now(timezone.utc)
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (next_midnight - now).total_seconds()


async def _reset_daily_meal_plan_counts():
    try:
        updated = await CoachProfileRepository.reset_daily_meal_plan_count()
        app_logger.info(f"DAILY_RESET_COMPLETED | UpdatedProfiles: {updated}")
    except Exception as e:
        app_logger.error(f"DAILY_RESET_FAILED | Error: {str(e)}")