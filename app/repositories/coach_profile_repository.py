from typing import Optional

from app.models.coach_profile import CoachProfile

class CoachProfileRepository:
    @staticmethod
    async def create(profile_data: dict) -> CoachProfile:
        profile = CoachProfile(**profile_data)
        await profile.insert()
        return profile

    @staticmethod
    async def get_by_user_id(user_id: str) -> Optional[CoachProfile]:
        return await CoachProfile.find_one(CoachProfile.user_id == user_id)

    @staticmethod
    async def reset_daily_meal_plan_count() -> int:
        result = await CoachProfile.find_all().update({"$set": {"dailyMealPlansCount": 0}})
        return getattr(result, "modified_count", 0)
