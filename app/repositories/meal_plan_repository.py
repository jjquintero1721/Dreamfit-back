from typing import Optional, List
from bson import ObjectId

from app.models.meal_plan import MealPlan


class MealPlanRepository:
    @staticmethod
    async def create(plan_data: dict) -> MealPlan:
        plan = MealPlan(**plan_data)
        await plan.insert()
        return plan

    @staticmethod
    async def get_by_id(plan_id: str) -> Optional[MealPlan]:
        try:
            return await MealPlan.get(ObjectId(plan_id))
        except:
            return None

    @staticmethod
    async def get_by_mentee_id(mentee_id: str) -> Optional[MealPlan]:
        plans = await MealPlan.find(MealPlan.mentee_id == mentee_id).sort(-MealPlan.created_at).limit(1).to_list()
        return plans[0] if plans else None

    @staticmethod
    async def get_all_by_mentee_id(mentee_id: str) -> List[MealPlan]:
        return await MealPlan.find(MealPlan.mentee_id == mentee_id).sort(-MealPlan.created_at).to_list()

    @staticmethod
    async def delete_previous_plans(mentee_id: str) -> None:
        await MealPlan.find(MealPlan.mentee_id == mentee_id).delete()

    @staticmethod
    async def update(plan_id: str, update_data: dict) -> Optional[MealPlan]:
        try:
            plan = await MealPlan.get(ObjectId(plan_id))
            if plan:
                for key, value in update_data.items():
                    setattr(plan, key, value)
                await plan.save()
                return plan
            return None
        except:
            return None