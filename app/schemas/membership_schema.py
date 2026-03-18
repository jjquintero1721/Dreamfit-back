from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MembershipRequest(BaseModel):
    plan_id: str = Field(..., alias="planId")
    user_id: str = Field(..., alias="userId")
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")

    class Config:
        allow_population_by_field_name = True
