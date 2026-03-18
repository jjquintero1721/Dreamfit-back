from pydantic import BaseModel
from typing import Optional, List

from app.utils.enums import LengthUnit, WeightUnit


class MeasurementData(BaseModel):
    value: float
    units: LengthUnit | WeightUnit

class SideMeasurementData(BaseModel):
    value: float
    units: LengthUnit

class DualMeasurementData(BaseModel):
    left: SideMeasurementData
    right: SideMeasurementData

class RequestPhysicalData(BaseModel):
    weight: MeasurementData
    chest: MeasurementData
    waist: MeasurementData
    hips: MeasurementData
    neck: MeasurementData
    leg: DualMeasurementData
    arms: DualMeasurementData
    calves: DualMeasurementData