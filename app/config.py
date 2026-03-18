import os
import logging
import sys

from dotenv import load_dotenv
from datetime import timedelta
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.user import User
from app.models.coach_profile import CoachProfile
from app.models.coach_code import CoachCode
from app.models.mentee_profile import MenteeProfile
from app.models.physical_data import WeightRecord, ChestMeasurement, WaistMeasurement, HipsMeasurement, NeckMeasurement, \
    LegMeasurement, ArmMeasurement, CalfMeasurement
from app.models.workout_plan import WorkoutPlan
from app.models.macronutrients import Macronutrients
from app.models.meal_plan import MealPlan
from app.models.membership import Membership

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
REDIS_URL = os.getenv("REDIS_URL")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]


def setup_logging():
    log_format = "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(funcName)s | %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    logger = logging.getLogger("dreamfit_api")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    if os.getenv("ENV") == "production":
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger


app_logger = setup_logging()


async def init_db():
    try:
        app_logger.info("Iniciando conexión a la base de datos...")
        await init_beanie(
            database=db,
            document_models=[
                User,
                CoachProfile,
                CoachCode,
                MenteeProfile,
                WeightRecord,
                ChestMeasurement,
                WaistMeasurement,
                HipsMeasurement,
                NeckMeasurement,
                LegMeasurement,
                ArmMeasurement,
                CalfMeasurement,
                WorkoutPlan,
                Macronutrients,
                MealPlan,
                Membership,
            ]
        )
        app_logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        app_logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise e