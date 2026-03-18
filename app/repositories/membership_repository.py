from typing import Any, Dict, Optional

from app.models.membership import Membership


class MembershipRepository:
    @staticmethod
    async def create(membership_data: Dict[str, Any]) -> Membership:
        membership = Membership(**membership_data)
        await membership.insert()
        return membership

    @staticmethod
    async def get_by_user_id(user_id: str) -> Optional[Membership]:
        return await Membership.find_one(Membership.user_id == user_id)
