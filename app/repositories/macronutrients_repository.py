from typing import Dict, Any, List, Optional
from bson import ObjectId

from app.models.macronutrients import Macronutrients


class MacronutrientsRepository:
    @staticmethod
    async def create(macronutrients_data: Dict[str, Any]) -> Macronutrients:
        macronutrients = Macronutrients(**macronutrients_data)
        await macronutrients.insert()
        return macronutrients

    @staticmethod
    async def get_by_id(macronutrients_id: str) -> Optional[Macronutrients]:
        try:
            return await Macronutrients.get(ObjectId(macronutrients_id))
        except:
            return None

    @staticmethod
    async def get_by_mentee_id(mentee_id: str) -> List[Macronutrients]:
        return await Macronutrients.find(
            Macronutrients.mentee_id == mentee_id
        ).sort([("created_at", -1)]).to_list()

    @staticmethod
    async def get_by_coach_id(coach_id: str) -> List[Macronutrients]:
        return await Macronutrients.find(
            Macronutrients.coach_id == coach_id
        ).sort([("created_at", -1)]).to_list()

    @staticmethod
    async def get_latest_by_mentee(mentee_id: str) -> Optional[Macronutrients]:
        return await Macronutrients.find(
            Macronutrients.mentee_id == mentee_id
        ).sort([("created_at", -1)]).limit(1).first_or_none()

    @staticmethod
    async def update(macronutrients_id: str, update_data: Dict[str, Any]) -> Optional[Macronutrients]:
        try:
            macronutrients = await Macronutrients.get(ObjectId(macronutrients_id))
            if macronutrients:
                for key, value in update_data.items():
                    setattr(macronutrients, key, value)
                await macronutrients.save()
                return macronutrients
            return None
        except:
            return None

    @staticmethod
    async def delete(macronutrients_id: str) -> bool:
        try:
            macronutrients = await Macronutrients.get(ObjectId(macronutrients_id))
            if macronutrients:
                await macronutrients.delete()
                return True
            return False
        except:
            return False

    @staticmethod
    async def delete_by_mentee_id(mentee_id: str) -> None:
        await Macronutrients.find(Macronutrients.mentee_id == mentee_id).delete()