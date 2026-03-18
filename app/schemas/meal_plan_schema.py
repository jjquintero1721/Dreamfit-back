from pydantic import BaseModel, Field
from typing import Optional


class CreateMealPlanRequest(BaseModel):
    mentee_id: str = Field(..., description="ID del alumno")
    days: int = Field(..., ge=1, le=7, description="Número de días del plan (1-7)")
    meals_per_day: int = Field(..., ge=1, le=5, description="Número de comidas por día (1-5)")
    notes: Optional[str] = Field(None, description="Observaciones, restricciones alimentarias, preferencias, etc.")


class MealPlanResponse(BaseModel):
    plan_id: str
    message: str