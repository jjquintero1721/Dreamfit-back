from beanie import Document


class CoachProfile(Document):
    user_id: str
    name: str
    last_name: str
    dailyMealPlansCount: int = 0

    class Settings:
        collection = "coach_profiles"
