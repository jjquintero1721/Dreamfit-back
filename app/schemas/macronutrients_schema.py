from pydantic import BaseModel, Field
from typing import Dict

from app.utils.enums import ObjectiveType


class MacronutrientsCalculationRequest(BaseModel):
    mentee_id: str = Field(..., description="ID del mentee")
    weight: float = Field(..., gt=0, description="Peso en kilogramos")
    activity_factor: float = Field(..., ge=1.0, le=1.9, description="Factor de actividad (1.0-1.9)")
    objective: ObjectiveType = Field(..., description="Objetivo: bulking, cutting o maintenance")
    protein_factor: float = Field(..., ge=1.0, le=3.0, description="Factor de proteína (1.0-3.0)")
    fat_factor: float = Field(..., ge=0.6, le=6.0, description="Factor de grasa (0.6-6.0)")


class MacrosResponse(BaseModel):
    protein: str
    fat: str
    carbs: str

    class Config:
        from_attributes = True


class MacronutrientsResponse(BaseModel):
    id: str
    mentee_id: str
    coach_id: str
    calories: str
    macros: MacrosResponse
    created_at: str

    class Config:
        from_attributes = True


class MacronutrientsCalculationResponse(BaseModel):
    bmr: int
    tdee: int
    final_calories: int
    protein_grams: int
    protein_calories: int
    fat_grams: int
    fat_calories: int
    carbs_grams: int
    carbs_calories: int
    macronutrients: MacronutrientsResponse

    class Config:
        from_attributes = True