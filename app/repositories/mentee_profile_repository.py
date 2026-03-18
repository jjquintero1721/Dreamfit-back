from app.models.mentee_profile import MenteeProfile
from app.schemas.mentee_profile_schema import MenteeProfileResponse


class MenteeProfileRepository:
    @staticmethod
    async def create(profile_data: dict) -> MenteeProfile:
        profile = MenteeProfile(**profile_data)
        await profile.insert()
        return profile

    @staticmethod
    async def get_by_coach(coach_id: str):
        mentees = await MenteeProfile.find(MenteeProfile.coach_id == coach_id).to_list()
        return [MenteeProfileResponse.from_orm(mentee) for mentee in mentees]

    @staticmethod
    async def get_by_user_id(user_id: str) -> MenteeProfile:
        return await MenteeProfile.find_one(MenteeProfile.user_id == user_id)

    @staticmethod
    async def count_by_coach_id(coach_id: str) -> int:
        return await MenteeProfile.find(MenteeProfile.coach_id == coach_id).count()
