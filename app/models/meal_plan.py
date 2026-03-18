from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone


class MealMacros(BaseModel):
    protein: str
    fat: str
    carbs: str


class Meal(BaseModel):
    mealnumber: int
    name: str
    recipee: str
    mealMacros: MealMacros


class DayPlan(BaseModel):
    dayNumber: int
    meals: List[Meal]


class DailyMacros(BaseModel):
    protein: str
    fat: str
    carbs: str


class MealPlan(Document):
    mentee_id: str
    coach_id: str
    calories: str
    dailyMacros: DailyMacros
    days: List[DayPlan]
    created_at: Optional[datetime] = None

    class Settings:
        collection = "meal_plans"

    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc)
        super().__init__(**data)