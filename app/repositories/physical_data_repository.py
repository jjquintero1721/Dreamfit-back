from typing import Dict, Any, List, Optional

from app.models.physical_data import WeightRecord, ChestMeasurement, WaistMeasurement, HipsMeasurement, NeckMeasurement, \
    LegMeasurement, ArmMeasurement, CalfMeasurement


class PhysicalDataRepository:
    @staticmethod
    async def create_weight_record(record_data: Dict[str, Any]) -> WeightRecord:
        record = WeightRecord(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_chest_measurement(record_data: Dict[str, Any]) -> ChestMeasurement:
        record = ChestMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_waist_measurement(record_data: Dict[str, Any]) -> WaistMeasurement:
        record = WaistMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_hips_measurement(record_data: Dict[str, Any]) -> HipsMeasurement:
        record = HipsMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_leg_measurement(record_data: Dict[str, Any]) -> LegMeasurement:
        record = LegMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_neck_measurement(record_data: Dict[str, Any]) -> NeckMeasurement:
        record = NeckMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_arm_measurement(record_data: Dict[str, Any]) -> ArmMeasurement:
        record = ArmMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def create_calf_measurement(record_data: Dict[str, Any]) -> CalfMeasurement:
        record = CalfMeasurement(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def get_weight_records_by_user_id(user_id: str) -> List[WeightRecord]:
        weight_records = await WeightRecord.find(
            WeightRecord.user_id == user_id
        ).sort([("date", -1)]).to_list()

        return weight_records

    @staticmethod
    async def get_latest_arm_measurement(user_id: str) -> Optional[ArmMeasurement]:
        arm_record = await ArmMeasurement.find(
            ArmMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return arm_record

    @staticmethod
    async def get_latest_calf_measurement(user_id: str) -> Optional[CalfMeasurement]:
        calf_record = await CalfMeasurement.find(
            CalfMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return calf_record

    @staticmethod
    async def get_latest_chest_measurement(user_id: str) -> Optional[ChestMeasurement]:
        chest_record = await ChestMeasurement.find(
            ChestMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return chest_record

    @staticmethod
    async def get_latest_hips_measurement(user_id: str) -> Optional[HipsMeasurement]:
        hips_record = await HipsMeasurement.find(
            HipsMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return hips_record

    @staticmethod
    async def get_latest_leg_measurement(user_id: str) -> Optional[LegMeasurement]:
        leg_record = await LegMeasurement.find(
            LegMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return leg_record

    @staticmethod
    async def get_latest_neck_measurement(user_id: str) -> Optional[NeckMeasurement]:
        neck_record = await NeckMeasurement.find(
            NeckMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return neck_record

    @staticmethod
    async def get_latest_waist_measurement(user_id: str) -> Optional[WaistMeasurement]:
        waist_record = await WaistMeasurement.find(
            WaistMeasurement.user_id == user_id
        ).sort([("date", -1)]).limit(1).first_or_none()

        return waist_record