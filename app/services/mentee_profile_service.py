import logging
from typing import Dict, Any
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.models.mentee_profile import MenteeProfile
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.repositories.physical_data_repository import PhysicalDataRepository
from app.schemas.physical_data_schema import RequestPhysicalData

mentee_service_logger = logging.getLogger("dreamfit_api.mentee_service")


class MenteeProfileService:
    @staticmethod
    async def get_by_coach(coach_id: str) -> list:
        mentee_service_logger.info(f"GET_MENTEES_BY_COACH_START | CoachID: {coach_id}")

        try:
            mentees = await MenteeProfileRepository.get_by_coach(coach_id)

            if len(mentees) > 0:
                mentee_service_logger.info(
                    f"GET_MENTEES_BY_COACH_SUCCESS | CoachID: {coach_id} | Count: {len(mentees)}"
                )
                return [mentee.model_dump() for mentee in mentees]

            mentee_service_logger.info(f"GET_MENTEES_BY_COACH_EMPTY | CoachID: {coach_id}")
            return []

        except Exception as e:
            mentee_service_logger.error(
                f"GET_MENTEES_BY_COACH_ERROR | CoachID: {coach_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @classmethod
    async def add_physical_data(cls, data: RequestPhysicalData, mentee_id: str) -> Dict[str, Any]:
        mentee_service_logger.info(f"ADD_PHYSICAL_DATA_START | MenteeID: {mentee_id}")

        try:
            current_date = datetime.now(timezone.utc)
            results: Dict[str, Any] = {}

            weight_data = data.weight.dict()
            weight_data["date"] = current_date
            weight_data["user_id"] = mentee_id
            results["weight"] = await PhysicalDataRepository.create_weight_record(weight_data)
            mentee_service_logger.debug(f"WEIGHT_RECORD_CREATED | MenteeID: {mentee_id}")

            chest_data = data.chest.dict()
            chest_data["date"] = current_date
            chest_data["user_id"] = mentee_id
            results["chest"] = await PhysicalDataRepository.create_chest_measurement(chest_data)
            mentee_service_logger.debug(f"CHEST_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            waist_data = data.waist.dict()
            waist_data["date"] = current_date
            waist_data["user_id"] = mentee_id
            results["waist"] = await PhysicalDataRepository.create_waist_measurement(waist_data)
            mentee_service_logger.debug(f"WAIST_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            hips_data = data.hips.dict()
            hips_data["date"] = current_date
            hips_data["user_id"] = mentee_id
            results["hips"] = await PhysicalDataRepository.create_hips_measurement(hips_data)
            mentee_service_logger.debug(f"HIPS_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            neck_data = data.neck.dict()
            neck_data["date"] = current_date
            neck_data["user_id"] = mentee_id
            results["neck"] = await PhysicalDataRepository.create_neck_measurement(neck_data)
            mentee_service_logger.debug(f"NECK_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            leg_data = {"measurements": data.leg.dict()}
            leg_data["date"] = current_date
            leg_data["user_id"] = mentee_id
            results["leg"] = await PhysicalDataRepository.create_leg_measurement(leg_data)
            mentee_service_logger.debug(f"LEG_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            arms_data = {"measurements": data.arms.dict()}
            arms_data["date"] = current_date
            arms_data["user_id"] = mentee_id
            results["arms"] = await PhysicalDataRepository.create_arm_measurement(arms_data)
            mentee_service_logger.debug(f"ARM_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            calves_data = {"measurements": data.calves.dict()}
            calves_data["date"] = current_date
            calves_data["user_id"] = mentee_id
            results["calves"] = await PhysicalDataRepository.create_calf_measurement(calves_data)
            mentee_service_logger.debug(f"CALF_MEASUREMENT_CREATED | MenteeID: {mentee_id}")

            mentee_service_logger.info(
                f"ADD_PHYSICAL_DATA_SUCCESS | MenteeID: {mentee_id} | RecordsCreated: {len(results)}"
            )

        except Exception as e:
            mentee_service_logger.error(
                f"ADD_PHYSICAL_DATA_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving physical data"
            )

    @staticmethod
    async def update_profile(user_id: str, update_data: dict) -> MenteeProfile:
        mentee_service_logger.info(f"UPDATE_PROFILE_START | MenteeID: {user_id}")

        try:
            profile = await MenteeProfileRepository.get_by_user_id(user_id)

            if not profile:
                mentee_service_logger.warning(f"UPDATE_PROFILE_NOT_FOUND | MenteeID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee profile not found"
                )

            update_dict = update_data.dict(exclude_unset=True)

            profile.age = update_dict["age"]
            profile.gender = update_dict["gender"]
            profile.height = update_dict["height"]
            profile.supplements = update_dict["supplements"]
            profile.weeklyExerciseFrequency = update_dict["weeklyExerciseFrequency"]
            profile.activityLevel = update_dict["activityLevel"]

            await profile.save()

            mentee_service_logger.info(f"UPDATE_PROFILE_SUCCESS | MenteeID: {user_id}")
            return profile.dict()

        except HTTPException:
            raise
        except Exception as e:
            mentee_service_logger.error(
                f"UPDATE_PROFILE_ERROR | MenteeID: {user_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating profile"
            )

    @staticmethod
    async def get_by_user_id(user_id: str) -> MenteeProfile:
        mentee_service_logger.info(f"GET_BY_USER_ID_START | UserID: {user_id}")

        try:
            profile = await MenteeProfileRepository.get_by_user_id(user_id)

            if not profile:
                mentee_service_logger.warning(f"GET_BY_USER_ID_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee profile not found"
                )

            mentee_service_logger.info(f"GET_BY_USER_ID_SUCCESS | UserID: {user_id}")
            return jsonable_encoder(profile)

        except HTTPException:
            raise
        except Exception as e:
            mentee_service_logger.error(
                f"GET_BY_USER_ID_ERROR | UserID: {user_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid user id provided"
            )