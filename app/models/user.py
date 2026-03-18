from beanie import Document
from pydantic import EmailStr, field_validator
from typing import Optional
from datetime import datetime


class User(Document):
    email: EmailStr
    password: str
    role: str
    created_at: Optional[datetime] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value):
        if isinstance(value, dict) and "$date" in value:
            return datetime.fromisoformat(value["$date"].replace("Z", "+00:00"))
        return value

    class Settings:
        collection = "users"
