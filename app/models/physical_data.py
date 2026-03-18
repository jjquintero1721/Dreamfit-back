from beanie import Document
from datetime import datetime
from pydantic import BaseModel

from app.utils.enums import WeightUnit, LengthUnit


class SideMeasurement(BaseModel):
    value: float
    units: LengthUnit


class DualMeasurement(BaseModel):
    left: SideMeasurement
    right: SideMeasurement


class WeightRecord(Document):
    user_id: str
    value: float
    date: datetime
    units: WeightUnit

    class Settings:
        collection = "weight_records"


class ChestMeasurement(Document):
    user_id: str
    value: float
    date: datetime
    units: LengthUnit

    class Settings:
        collection = "chest_measurements"


class WaistMeasurement(Document):
    user_id: str
    value: float
    date: datetime
    units: LengthUnit

    class Settings:
        collection = "waist_measurements"


class HipsMeasurement(Document):
    user_id: str
    value: float
    date: datetime
    units: LengthUnit

    class Settings:
        collection = "hips_measurements"


class NeckMeasurement(Document):
    user_id: str
    value: float
    date: datetime
    units: LengthUnit

    class Settings:
        collection = "neck_measurements"


class LegMeasurement(Document):
    user_id: str
    date: datetime
    measurements: DualMeasurement

    class Settings:
        collection = "leg_measurements"


class ArmMeasurement(Document):
    user_id: str
    date: datetime
    measurements: DualMeasurement

    class Settings:
        collection = "arm_measurements"


class CalfMeasurement(Document):
    user_id: str
    date: datetime
    measurements: DualMeasurement

    class Settings:
        collection = "calf_measurements"