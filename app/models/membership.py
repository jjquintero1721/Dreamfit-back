from datetime import datetime
from typing import Optional

from beanie import Document


class Membership(Document):
    user_id: str
    plan_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Settings:
        collection = "memberships"
