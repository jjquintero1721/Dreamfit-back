import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from app.repositories.physical_data_repository import PhysicalDataRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository

physical_service_logger = logging.getLogger("dreamfit_api.physical_service")


class PhysicalDataService:
    @staticmethod
    async def get_weight_records_by_user_id(user_id: str) -> List[dict]:
        physical_service_logger.info(f"GET_WEIGHT_RECORDS_START | UserID: {user_id}")

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(user_id)
            if not mentee_profile:
                physical_service_logger.warning(f"GET_WEIGHT_RECORDS_USER_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            weight_records = await PhysicalDataRepository.get_weight_records_by_user_id(user_id)

            formatted_records = []
            for record in weight_records:
                formatted_records.append({
                    "value": record.value,
                    "date": record.date.isoformat(),
                    "units": record.units
                })

            physical_service_logger.info(
                f"GET_WEIGHT_RECORDS_SUCCESS | UserID: {user_id} | RecordCount: {len(formatted_records)}"
            )
            return formatted_records

        except HTTPException:
            raise
        except Exception as e:
            physical_service_logger.error(
                f"GET_WEIGHT_RECORDS_ERROR | UserID: {user_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving weight records"
            )

    @staticmethod
    async def get_latest_body_measurements(user_id: str) -> Dict[str, Any]:
        physical_service_logger.info(f"GET_BODY_MEASUREMENTS_START | UserID: {user_id}")

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(user_id)
            if not mentee_profile:
                physical_service_logger.warning(f"GET_BODY_MEASUREMENTS_USER_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            measurements = {}

            arm_record = await PhysicalDataRepository.get_latest_arm_measurement(user_id)
            if arm_record:
                measurements["arm"] = {
                    "left": {
                        "value": arm_record.measurements.left.value,
                        "units": arm_record.measurements.left.units
                    },
                    "right": {
                        "value": arm_record.measurements.right.value,
                        "units": arm_record.measurements.right.units
                    }
                }
                physical_service_logger.debug(f"ARM_MEASUREMENT_FOUND | UserID: {user_id}")

            calf_record = await PhysicalDataRepository.get_latest_calf_measurement(user_id)
            if calf_record:
                measurements["calf"] = {
                    "left": {
                        "value": calf_record.measurements.left.value,
                        "units": calf_record.measurements.left.units
                    },
                    "right": {
                        "value": calf_record.measurements.right.value,
                        "units": calf_record.measurements.right.units
                    }
                }
                physical_service_logger.debug(f"CALF_MEASUREMENT_FOUND | UserID: {user_id}")

            chest_record = await PhysicalDataRepository.get_latest_chest_measurement(user_id)
            if chest_record:
                measurements["chest"] = {
                    "value": chest_record.value,
                    "units": chest_record.units
                }
                physical_service_logger.debug(f"CHEST_MEASUREMENT_FOUND | UserID: {user_id}")

            hips_record = await PhysicalDataRepository.get_latest_hips_measurement(user_id)
            if hips_record:
                measurements["hips"] = {
                    "value": hips_record.value,
                    "units": hips_record.units
                }
                physical_service_logger.debug(f"HIPS_MEASUREMENT_FOUND | UserID: {user_id}")

            leg_record = await PhysicalDataRepository.get_latest_leg_measurement(user_id)
            if leg_record:
                measurements["leg"] = {
                    "left": {
                        "value": leg_record.measurements.left.value,
                        "units": leg_record.measurements.left.units
                    },
                    "right": {
                        "value": leg_record.measurements.right.value,
                        "units": leg_record.measurements.right.units
                    }
                }
                physical_service_logger.debug(f"LEG_MEASUREMENT_FOUND | UserID: {user_id}")

            neck_record = await PhysicalDataRepository.get_latest_neck_measurement(user_id)
            if neck_record:
                measurements["neck"] = {
                    "value": neck_record.value,
                    "units": neck_record.units
                }
                physical_service_logger.debug(f"NECK_MEASUREMENT_FOUND | UserID: {user_id}")

            waist_record = await PhysicalDataRepository.get_latest_waist_measurement(user_id)
            if waist_record:
                measurements["waist"] = {
                    "value": waist_record.value,
                    "units": waist_record.units
                }
                physical_service_logger.debug(f"WAIST_MEASUREMENT_FOUND | UserID: {user_id}")

            physical_service_logger.info(
                f"GET_BODY_MEASUREMENTS_SUCCESS | UserID: {user_id} | MeasurementTypes: {len(measurements)}"
            )
            return measurements

        except HTTPException:
            raise
        except Exception as e:
            physical_service_logger.error(
                f"GET_BODY_MEASUREMENTS_ERROR | UserID: {user_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving body measurements"
            )