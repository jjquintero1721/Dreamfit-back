from app.models.coach_code import CoachCode
from typing import Optional


class CoachCodeRepository:
    @staticmethod
    async def get_by_code(code: str) -> Optional[CoachCode]:
        return await CoachCode.find_one(CoachCode.code == code)

    @staticmethod
    async def create(coach_code: CoachCode) -> CoachCode:
        await coach_code.insert()
        return coach_code

    @staticmethod
    async def get_by_user_id(user_id: str) -> CoachCode:
        return await CoachCode.find_one(CoachCode.user_id == user_id)