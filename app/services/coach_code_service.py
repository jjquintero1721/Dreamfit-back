import logging
from uuid import uuid4
from typing import List
from app.models.coach_code import CoachCode

coach_code_logger = logging.getLogger("dreamfit_api.coach_code_service")


class CoachCodeService:
    @staticmethod
    async def update_all_coach_codes() -> int:

        coach_code_logger.info("UPDATE_ALL_CODES_START | Iniciando actualización de códigos")

        try:
            # Obtener todos los códigos existentes
            all_codes = await CoachCode.find_all().to_list()

            if not all_codes:
                coach_code_logger.info("UPDATE_ALL_CODES_EMPTY | No hay códigos para actualizar")
                return 0

            updated_count = 0
            errors = []

            for coach_code in all_codes:
                old_code = coach_code.code
                new_code = str(uuid4())

                try:
                    # Actualizar el código
                    coach_code.code = new_code
                    await coach_code.save()

                    updated_count += 1
                    coach_code_logger.debug(
                        f"CODE_UPDATED | UserID: {coach_code.user_id} | "
                        f"OldCode: {old_code} | NewCode: {new_code}"
                    )

                except Exception as e:
                    error_msg = f"UserID: {coach_code.user_id}, Error: {str(e)}"
                    errors.append(error_msg)
                    coach_code_logger.error(
                        f"CODE_UPDATE_FAILED | {error_msg}"
                    )

            # Log final del proceso
            if errors:
                coach_code_logger.warning(
                    f"UPDATE_ALL_CODES_COMPLETED_WITH_ERRORS | "
                    f"Updated: {updated_count} | Errors: {len(errors)}"
                )
            else:
                coach_code_logger.info(
                    f"UPDATE_ALL_CODES_SUCCESS | TotalUpdated: {updated_count}"
                )

            return updated_count

        except Exception as e:
            coach_code_logger.error(
                f"UPDATE_ALL_CODES_ERROR | Unexpected error: {str(e)}"
            )
            raise