from pydantic import BaseModel
from typing import Optional


class ResponsePayload(BaseModel):
    message: str
    payload: Optional[dict] = None

    @classmethod
    def create(cls, message: str, data: dict|list = None) -> dict:
        return {"message": message, "data": data}
