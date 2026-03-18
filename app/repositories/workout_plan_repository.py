from typing import Dict, Any
from bson import ObjectId

from app.models.workout_plan import WorkoutPlan


class WorkoutPlanRepository:
    @staticmethod
    async def create(plan_data: Dict[str, Any]) -> WorkoutPlan:
        plan = WorkoutPlan(**plan_data)
        await plan.insert()
        return plan

    @staticmethod
    async def get_by_id(plan_id: str) -> WorkoutPlan:
        try:
            return await WorkoutPlan.get(ObjectId(plan_id))
        except:
            return None

    @staticmethod
    async def update(plan_id: str, update_data: Dict[str, Any]) -> WorkoutPlan:
        try:
            plan = await WorkoutPlan.get(ObjectId(plan_id))
            if plan:
                for key, value in update_data.items():
                    setattr(plan, key, value)
                await plan.save()
                return plan
            return None
        except:
            return None

    @staticmethod
    async def get_by_mentee_id(mentee_id: str) -> list[WorkoutPlan]:
        return await WorkoutPlan.find(WorkoutPlan.mentee_id == mentee_id).to_list()

    @staticmethod
    async def get_by_coach_id(coach_id: str) -> list[WorkoutPlan]:
        return await WorkoutPlan.find(WorkoutPlan.coach_id == coach_id).to_list()

    @staticmethod
    async def delete_previous_plans(mentee_id: str) -> None:
        await WorkoutPlan.find(WorkoutPlan.mentee_id == mentee_id).delete()

    @staticmethod
    async def get_active_plan_by_mentee(mentee_id: str) -> WorkoutPlan:
        return await WorkoutPlan.find_one(WorkoutPlan.mentee_id == mentee_id)