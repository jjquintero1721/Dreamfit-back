from pydantic import BaseModel


class CoachProfileResponse(BaseModel):
    user_id: str
    name: str
    last_name: str
    dailyMealPlansCount: int = 0

    class Config:
        from_attributes = True
