from beanie import Document
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone


class Macros(BaseModel):
    protein: str
    fat: str
    carbs: str


class Macronutrients(Document):
    mentee_id: str
    coach_id: str
    calories: str
    macros: Macros
    created_at: Optional[datetime] = None

    class Settings:
        collection = "macronutrients"

    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc)
        super().__init__(**data)