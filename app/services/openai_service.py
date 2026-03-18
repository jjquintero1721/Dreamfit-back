import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from fastapi import HTTPException, status

openai_logger = logging.getLogger("dreamfit_api.openai_service")

SYSTEM_PROMPT = (
    "Eres un experto en la creación de planes nutricionales para deportistas.\n"
    "Tu salida debe ser EXCLUSIVAMENTE un JSON válido, sin texto adicional.\n\n"
    "Reglas obligatorias:\n"
    "- Devuelve SOLO un JSON EXACTAMENTE con esta estructura y nombres de llaves:\n"
    '  {"calories":"NNNN","dailyMacros":{"protein":"NNg","fat":"NNg","carbs":"NNg"},"days":[{"dayNumber":1,"meals":[{"mealnumber":1,"name":"...","recipee":"...","mealMacros":{"protein":"...g","fat":"...g","carbs":"...g"}}]}]}\n'
    '- "calories" debe ser una cadena numérica sin sufijos (ej. "2946").\n'
    '- "protein","fat","carbs" SIEMPRE como cadenas con sufijo "g" (ej. "30g").\n'
    "- Crea EXACTAMENTE D días dentro de \"days\", con \"dayNumber\" empezando en 1 y secuencial.\n"
    "- En cada día, crea EXACTAMENTE M comidas, con \"mealnumber\" empezando en 1 y secuencial.\n"
    "- La suma diaria debe aproximarse a los \"dailyMacros\" indicados (tolerancia ±10 g por macro).\n"
    '- Escribe "name" y "recipee" en español, con instrucciones breves y realistas.\n'
    '- Evita repetir el mismo "name" en días consecutivos.\n\n'
    "Si NO puedes cumplir con lo solicitado (por restricciones, inconsistencias o imposibilidad), "
    'devuelve ÚNICAMENTE este JSON de error: {"error":"No se ha podido cumplir con la solicitud"}'
)


class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not self.api_key:
            openai_logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required")

        self.client = OpenAI(api_key=self.api_key)

    async def generate_meal_plan(
        self,
        calories: int,
        protein: int,
        carbs: int,
        fat: int,
        days: int,
        meals_per_day: int,
        notes: str = ""
    ) -> Dict[str, Any]:

        openai_logger.info(
            f"GENERATE_MEAL_PLAN_START | Calories: {calories} | Days: {days} | Meals: {meals_per_day}"
        )

        user_prompt = (
            f"Crea un plan de alimentación que cumpla con {calories} calorías diarias y estos macronutrientes diarios: "
            f"{protein} gramos de proteína, {carbs} gramos de carbohidratos, y {fat} gramos de grasa.\n"
            f"El plan debe ser para {days} días, con {meals_per_day} comidas por día, y teniendo en cuenta las siguientes observaciones: {notes}.\n\n"
            f"Recuerda: EXACTAMENTE {days} días y EXACTAMENTE {meals_per_day} comidas por día; índices desde 1; "
            f"sin texto fuera del JSON; tolerancia ±10g por macro; si no puedes, devuelve "
            f'{{"error":"No se ha podido cumplir con la solicitud"}}.'
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                #max_tokens=max(500, days * meals_per_day * 70),
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                openai_logger.error("OPENAI_EMPTY_RESPONSE")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OpenAI returned empty response"
                )

            openai_logger.debug(f"OPENAI_RAW_RESPONSE: {content[:500]}...")

            try:
                meal_plan = json.loads(content)
            except json.JSONDecodeError as e:
                openai_logger.error(f"OPENAI_JSON_DECODE_ERROR | Error: {str(e)} | Content: {content[:500]}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to parse OpenAI response as JSON"
                )

            if "error" in meal_plan:
                openai_logger.warning(f"OPENAI_PLAN_ERROR | Error: {meal_plan['error']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=meal_plan["error"]
                )

            required_keys = ["calories", "dailyMacros", "days"]
            if not all(key in meal_plan for key in required_keys):
                openai_logger.error(f"OPENAI_INVALID_STRUCTURE | Keys: {meal_plan.keys()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid meal plan structure from OpenAI"
                )

            if not isinstance(meal_plan["days"], list) or len(meal_plan["days"]) != days:
                openai_logger.error(
                    f"OPENAI_INVALID_DAYS | Expected: {days} | Got: {len(meal_plan.get('days', []))}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid number of days in meal plan. Expected {days}, got {len(meal_plan.get('days', []))}"
                )

            openai_logger.info(
                f"GENERATE_MEAL_PLAN_SUCCESS | Days: {len(meal_plan['days'])} | "
                f"Meals per day: {len(meal_plan['days'][0]['meals']) if meal_plan['days'] else 0}"
            )

            return meal_plan

        except HTTPException:
            raise
        except Exception as e:
            openai_logger.error(f"GENERATE_MEAL_PLAN_ERROR | Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate meal plan: {str(e)}"
            )
