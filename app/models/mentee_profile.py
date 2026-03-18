from beanie import Document
from pydantic import BaseModel
from typing import List, Optional

from app.utils.enums import LengthUnit, Gender, ActivityLevel, Suplement, ExerciseFrequency


class PlanInfo(BaseModel):
    active: bool
    planId: str

class UserPlans(BaseModel):
    mealPlan: PlanInfo
    workoutsPlan: PlanInfo

class Height(BaseModel):
    value: float
    units: LengthUnit

class MenteeProfile(Document):
    user_id: str
    name: str
    last_name: str
    coach_id: str
    userPlans: UserPlans
    age: Optional[int] = 0
    gender: Optional[Gender] = Gender.empty
    height: Optional[Height] = {"value": 0, "units": LengthUnit.cm}
    supplements: Optional[List[Suplement]] = []
    weeklyExerciseFrequency: Optional[ExerciseFrequency] = ExerciseFrequency.one
    activityLevel: Optional[ActivityLevel] = ActivityLevel.sedentary

    class Settings:
        collection = "mentee_profiles"
