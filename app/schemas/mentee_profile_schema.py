from pydantic import BaseModel
from typing import List, Dict

from app.utils.enums import ActivityLevel, ExerciseFrequency, Gender, Suplement


class PlanInfo(BaseModel):
    active: bool
    planId: str

    class Config:
        from_attributes = True


class UserPlans(BaseModel):
    mealPlan: PlanInfo
    workoutsPlan: PlanInfo

    class Config:
        from_attributes = True


class MenteeProfileResponse(BaseModel):
    user_id: str
    name: str
    last_name: str
    userPlans: UserPlans

    class Config:
        from_attributes = True


class HeightData(BaseModel):
    value: float
    units: str


class UpdateMenteeProfileRequest(BaseModel):
    age: int
    gender: Gender
    height: HeightData
    supplements: List[Suplement]
    weeklyExerciseFrequency: ExerciseFrequency
    activityLevel: ActivityLevel


class MenteeProfileUpdateResponse(BaseModel):
    name: str
    last_name: str
    age: int
    gender: str
    height: Dict
    supplements: List
    weeklyExerciseFrequency: str
    activityLevel: str

    class Config:
        from_attributes = True