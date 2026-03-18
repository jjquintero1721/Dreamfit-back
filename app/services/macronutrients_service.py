import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.repositories.macronutrients_repository import MacronutrientsRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.schemas.macronutrients_schema import (
    MacronutrientsCalculationRequest,
    MacronutrientsCalculationResponse,
    MacronutrientsResponse,
    MacrosResponse,
    ObjectiveType
)
from app.models.macronutrients import Macros

macronutrients_service_logger = logging.getLogger("dreamfit_api.macronutrients_service")


class MacronutrientsService:
    @staticmethod
    async def calculate_and_save_macronutrients(
        data: MacronutrientsCalculationRequest,
        coach_id: str
    ) -> MacronutrientsCalculationResponse:
        macronutrients_service_logger.info(
            f"CALCULATE_MACRONUTRIENTS_START | MenteeID: {data.mentee_id} | CoachID: {coach_id}"
        )

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(data.mentee_id)
            if not mentee_profile:
                macronutrients_service_logger.warning(
                    f"MENTEE_NOT_FOUND | MenteeID: {data.mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee not found"
                )

            if mentee_profile.coach_id != coach_id:
                macronutrients_service_logger.warning(
                    f"UNAUTHORIZED_ACCESS | MenteeID: {data.mentee_id} | CoachID: {coach_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            calculations = MacronutrientsService._calculate_macronutrients(data)

            await MacronutrientsRepository.delete_by_mentee_id(data.mentee_id)
            macronutrients_service_logger.debug(
                f"PREVIOUS_MACRONUTRIENTS_DELETED | MenteeID: {data.mentee_id}"
            )

            macronutrients_data = {
                "mentee_id": data.mentee_id,
                "coach_id": coach_id,
                "calories": str(calculations["final_calories"]),
                "macros": Macros(
                    protein=f"{calculations['protein_grams']}g",
                    fat=f"{calculations['fat_grams']}g",
                    carbs=f"{calculations['carbs_grams']}g"
                ),
                "created_at": datetime.now(timezone.utc)
            }

            saved_macronutrients = await MacronutrientsRepository.create(macronutrients_data)

            macronutrients_response = MacronutrientsResponse(
                id=str(saved_macronutrients.id),
                mentee_id=saved_macronutrients.mentee_id,
                coach_id=saved_macronutrients.coach_id,
                calories=saved_macronutrients.calories,
                macros=MacrosResponse(
                    protein=saved_macronutrients.macros.protein,
                    fat=saved_macronutrients.macros.fat,
                    carbs=saved_macronutrients.macros.carbs
                ),
                created_at=saved_macronutrients.created_at.isoformat()
            )

            response = MacronutrientsCalculationResponse(
                bmr=calculations["bmr"],
                tdee=calculations["tdee"],
                final_calories=calculations["final_calories"],
                protein_grams=calculations["protein_grams"],
                protein_calories=calculations["protein_calories"],
                fat_grams=calculations["fat_grams"],
                fat_calories=calculations["fat_calories"],
                carbs_grams=calculations["carbs_grams"],
                carbs_calories=calculations["carbs_calories"],
                macronutrients=macronutrients_response
            )

            macronutrients_service_logger.info(
                f"CALCULATE_MACRONUTRIENTS_SUCCESS | MenteeID: {data.mentee_id} | "
                f"Calories: {calculations['final_calories']} | MacroID: {saved_macronutrients.id}"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            macronutrients_service_logger.error(
                f"CALCULATE_MACRONUTRIENTS_ERROR | MenteeID: {data.mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @staticmethod
    def _calculate_macronutrients(data: MacronutrientsCalculationRequest) -> Dict[str, int]:
        bmr = int(data.weight * 22)

        tdee = int(bmr * data.activity_factor)

        objective_multipliers = {
            ObjectiveType.bulking: 1.20,      # +20%
            ObjectiveType.cutting: 0.80,      # -20%
            ObjectiveType.maintenance: 1.00   # 0%
        }
        final_calories = int(tdee * objective_multipliers[data.objective])

        protein_grams = int(data.weight * data.protein_factor)
        protein_calories = protein_grams * 4

        fat_grams = int(data.weight * data.fat_factor)
        fat_calories = fat_grams * 9

        carbs_calories = final_calories - (protein_calories + fat_calories)
        carbs_grams = int(carbs_calories / 4)

        return {
            "bmr": bmr,
            "tdee": tdee,
            "final_calories": final_calories,
            "protein_grams": protein_grams,
            "protein_calories": protein_calories,
            "fat_grams": fat_grams,
            "fat_calories": fat_calories,
            "carbs_grams": carbs_grams,
            "carbs_calories": carbs_calories
        }

    @staticmethod
    async def get_macronutrients_by_mentee(mentee_id: str, requestor_id: str) -> List[MacronutrientsResponse]:
        macronutrients_service_logger.info(
            f"GET_MACRONUTRIENTS_BY_MENTEE_START | MenteeID: {mentee_id} | RequestorID: {requestor_id}"
        )

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)
            if not mentee_profile:
                macronutrients_service_logger.warning(
                    f"MENTEE_NOT_FOUND | MenteeID: {mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee not found"
                )

            if mentee_profile.coach_id != requestor_id and mentee_id != requestor_id:
                macronutrients_service_logger.warning(
                    f"UNAUTHORIZED_ACCESS | MenteeID: {mentee_id} | RequestorID: {requestor_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            macronutrients_list = await MacronutrientsRepository.get_by_mentee_id(mentee_id)

            response = []
            for macro in macronutrients_list:
                response.append(MacronutrientsResponse(
                    id=str(macro.id),
                    mentee_id=macro.mentee_id,
                    coach_id=macro.coach_id,
                    calories=macro.calories,
                    macros=MacrosResponse(
                        protein=macro.macros.protein,
                        fat=macro.macros.fat,
                        carbs=macro.macros.carbs
                    ),
                    created_at=macro.created_at.isoformat()
                ))

            macronutrients_service_logger.info(
                f"GET_MACRONUTRIENTS_BY_MENTEE_SUCCESS | MenteeID: {mentee_id} | Count: {len(response)}"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            macronutrients_service_logger.error(
                f"GET_MACRONUTRIENTS_BY_MENTEE_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @staticmethod
    async def get_latest_macronutrients_by_mentee(mentee_id: str, requestor_id: str) -> MacronutrientsResponse:
        macronutrients_service_logger.info(
            f"GET_LATEST_MACRONUTRIENTS_START | MenteeID: {mentee_id} | RequestorID: {requestor_id}"
        )

        try:
            mentee_profile = await MenteeProfileRepository.get_by_user_id(mentee_id)
            if not mentee_profile:
                macronutrients_service_logger.warning(
                    f"MENTEE_NOT_FOUND | MenteeID: {mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentee not found"
                )

            if mentee_profile.coach_id != requestor_id and mentee_id != requestor_id:
                macronutrients_service_logger.warning(
                    f"UNAUTHORIZED_ACCESS | MenteeID: {mentee_id} | RequestorID: {requestor_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            latest_macro = await MacronutrientsRepository.get_latest_by_mentee(mentee_id)
            if not latest_macro:
                macronutrients_service_logger.warning(
                    f"NO_MACRONUTRIENTS_FOUND | MenteeID: {mentee_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No macronutrients found for this mentee"
                )

            response = MacronutrientsResponse(
                id=str(latest_macro.id),
                mentee_id=latest_macro.mentee_id,
                coach_id=latest_macro.coach_id,
                calories=latest_macro.calories,
                macros=MacrosResponse(
                    protein=latest_macro.macros.protein,
                    fat=latest_macro.macros.fat,
                    carbs=latest_macro.macros.carbs
                ),
                created_at=latest_macro.created_at.isoformat()
            )

            macronutrients_service_logger.info(
                f"GET_LATEST_MACRONUTRIENTS_SUCCESS | MenteeID: {mentee_id} | MacroID: {latest_macro.id}"
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            macronutrients_service_logger.error(
                f"GET_LATEST_MACRONUTRIENTS_ERROR | MenteeID: {mentee_id} | Error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )