from pydantic import BaseModel
from typing import List, Optional


class WeightRequest(BaseModel):
    value: str
    units: str


class WorkoutRequest(BaseModel):
    name: str
    muscularGroup: str
    order: int
    sets: str
    reps: str
    element: Optional[str] = ""
    weight: Optional[WeightRequest] = None
    rest: Optional[str] = ""
    technique: Optional[str] = ""
    RIR: Optional[str] = ""
    videoUrl: Optional[str] = None


class MuscularGroupRequest(BaseModel):
    group: str
    workouts: List[WorkoutRequest]


class DayRequest(BaseModel):
    dayNumber: str
    muscularGroups: List[MuscularGroupRequest]


class CreateWorkoutPlanRequest(BaseModel):
    mentee_id: str
    trainingObjective: str
    days: List[DayRequest]


class WorkoutPlanResponse(BaseModel):
    id: str
    coach_id: str
    mentee_id: str
    trainingObjective: str
    days: List[DayRequest]
    created_at: str
    is_active: bool

    class Config:
        from_attributes = True