from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone


class Weight(BaseModel):
    value: str
    units: str


class Workout(BaseModel):
    name: str
    muscularGroup: str
    order: int
    sets: str
    reps: str
    element: Optional[str] = ""
    weight: Optional[Weight] = None
    rest: Optional[str] = ""
    technique: Optional[str] = ""
    RIR: Optional[str] = ""
    videoUrl: Optional[str] = None


class MuscularGroup(BaseModel):
    group: str
    workouts: List[Workout]


class Day(BaseModel):
    dayNumber: str
    muscularGroups: List[MuscularGroup]


class WorkoutPlan(Document):
    coach_id: str
    mentee_id: str
    trainingObjective: str
    days: List[Day]
    created_at: Optional[datetime] = None

    class Settings:
        collection = "workout_plans"

    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc)
        super().__init__(**data)