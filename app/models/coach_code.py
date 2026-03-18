from beanie import Document
from pydantic import BaseModel
from uuid import uuid4


class CoachCode(Document):
    user_id: str
    code: str

    class Settings:
        collection = "coach_codes"

    @classmethod
    def create_code(cls, user_id: str) -> "CoachCode":
        return cls(user_id=user_id, code=str(uuid4()))
