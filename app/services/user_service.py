import logging
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from bson import ObjectId

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY, ALGORITHM
from app.repositories.user_repository import UserRepository
from app.repositories.coach_profile_repository import CoachProfileRepository
from app.repositories.coach_code_repository import CoachCodeRepository
from app.repositories.mentee_profile_repository import MenteeProfileRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.content_service import ContentService
from app.models.user import User
from app.models.coach_code import CoachCode
from app.utils.auth_utils import AuthUtils
from app.utils.enums import RoleName

user_logger = logging.getLogger("dreamfit_api.user_service")


class UserService:
    @classmethod
    async def signup(cls, email: str, password: str, role: str, name: str, last_name: str, coach_code: str = ""):
        user_logger.info(f"SIGNUP_START | Email: {email} | Role: {role}")
        user = None

        try:
            await cls._ensure_email_is_unique(email)
            user_logger.debug(f"EMAIL_UNIQUE_CHECK_PASSED | Email: {email}")

            cls._validate_role(RoleName(role).value)
            user_logger.debug(f"ROLE_VALIDATION_PASSED | Role: {role}")

            await cls._validate_coach_code(RoleName(role).value, coach_code)
            user_logger.debug(f"COACH_CODE_VALIDATION_PASSED | Role: {role}")

            hashed_password = AuthUtils.get_password_hash(password)
            user_data = {
                "email": email,
                "password": hashed_password,
                "role": RoleName(role).value,
                "created_at": datetime.now(timezone.utc)
            }

            user = await UserRepository.create(user_data)
            user_logger.info(f"USER_CREATED | UserID: {user.id} | Email: {email}")

            try:
                if role == RoleName.coach:
                    await cls._create_coach_profile(user, name, last_name)
                    user_logger.info(f"COACH_PROFILE_CREATED | UserID: {user.id}")
                elif role == RoleName.mentee:
                    await cls._create_mentee_profile(user, name, last_name, coach_code)
                    user_logger.info(f"MENTEE_PROFILE_CREATED | UserID: {user.id}")
            except Exception as profile_error:
                user_logger.error(
                    f"PROFILE_CREATION_FAILED | UserID: {user.id} | "
                    f"Rolling back user creation | Error: {str(profile_error)}"
                )
                await UserRepository.delete(user)
                user_logger.info(f"USER_ROLLBACK_SUCCESS | UserID: {user.id} | Email: {email}")
                raise profile_error

            user_logger.info(f"SIGNUP_COMPLETED | UserID: {user.id} | Email: {email}")

        except HTTPException as e:
            user_logger.error(f"SIGNUP_HTTP_ERROR | Email: {email} | Error: {e.detail}")
            raise e
        except Exception as e:
            user_logger.error(f"SIGNUP_UNEXPECTED_ERROR | Email: {email} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )

    @staticmethod
    async def _ensure_email_is_unique(email: str):
        user_logger.debug(f"CHECKING_EMAIL_UNIQUENESS | Email: {email}")
        try:
            existing_user = await UserRepository.get_by_email(email)
            if existing_user:
                user_logger.warning(f"EMAIL_ALREADY_EXISTS | Email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user_logger.debug(f"EMAIL_UNIQUE_CONFIRMED | Email: {email}")
        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"EMAIL_CHECK_ERROR | Email: {email} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error validating email"
            )

    @staticmethod
    def _validate_role(role: str):
        user_logger.debug(f"VALIDATING_ROLE | Role: {role}")
        if role not in (RoleName.coach, RoleName.mentee, RoleName.system):
            user_logger.warning(f"INVALID_ROLE | Role: {role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        user_logger.debug(f"ROLE_VALID | Role: {role}")

    @staticmethod
    async def _validate_coach_code(role: str, coach_code: str):
        if role == RoleName.mentee:
            user_logger.debug(f"VALIDATING_COACH_CODE | Code: {coach_code}")

            if not coach_code:
                user_logger.warning("COACH_CODE_MISSING")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Coach code not provided"
                )

            try:
                coach_code_obj = await CoachCodeRepository.get_by_code(coach_code)
                if not coach_code_obj:
                    user_logger.warning(f"COACH_CODE_INVALID | Code: {coach_code}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid coach code provided"
                    )
                user_logger.debug(f"COACH_CODE_VALID | Code: {coach_code} | CoachID: {coach_code_obj.user_id}")
            except HTTPException:
                raise
            except Exception as e:
                user_logger.error(f"COACH_CODE_VALIDATION_ERROR | Code: {coach_code} | Error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error validating coach code"
                )

    @staticmethod
    async def _create_coach_profile(user: User, name: str, last_name: str):
        user_logger.info(f"CREATING_COACH_PROFILE | UserID: {user.id}")
        try:
            profile_data = {
                "user_id": str(user.id),
                "name": name,
                "last_name": last_name,
                "dailyMealPlansCount": 0,
            }

            await CoachProfileRepository.create(profile_data)
            coach_code_obj = CoachCode.create_code(user_id=str(user.id))
            await CoachCodeRepository.create(coach_code_obj)

            # Asignar membresía free por defecto con 1 año de duración
            start_date = datetime.now()
            end_date = start_date + timedelta(days=365)

            await MembershipRepository.create({
                "user_id": str(user.id),
                "plan_id": "4",
                "start_date": start_date,
                "end_date": end_date,
            })

            user_logger.info(f"COACH_PROFILE_COMPLETE | UserID: {user.id} | Code: {coach_code_obj.code}")
        except Exception as e:
            user_logger.error(f"COACH_PROFILE_ERROR | UserID: {user.id} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating coach profile"
            )

    @staticmethod
    async def _create_mentee_profile(user: User, name: str, last_name: str, coach_code: str):
        user_logger.info(f"CREATING_MENTEE_PROFILE | UserID: {user.id} | CoachCode: {coach_code}")
        try:
            coach_code_obj = await CoachCodeRepository.get_by_code(coach_code)

            await UserService._ensure_coach_can_accept_mentee(coach_code_obj.user_id)

            profile_data = {
                "user_id": str(user.id),
                "name": name,
                "last_name": last_name,
                "coach_id": coach_code_obj.user_id,
                "userPlans": {
                    "mealPlan": {
                        "active": False,
                        "planId": ""
                    },
                    "workoutsPlan": {
                        "active": False,
                        "planId": ""
                    }
                }
            }

            await MenteeProfileRepository.create(profile_data)
            user_logger.info(f"MENTEE_PROFILE_COMPLETE | UserID: {user.id} | CoachID: {coach_code_obj.user_id}")
        except Exception as e:
            user_logger.error(f"MENTEE_PROFILE_ERROR | UserID: {user.id} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating mentee profile"
            )

    @staticmethod
    async def _ensure_coach_can_accept_mentee(coach_id: str):
        membership = await MembershipRepository.get_by_user_id(coach_id)
        if not membership:
            user_logger.warning(f"MENTEE_SIGNUP_NO_MEMBERSHIP | CoachID: {coach_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El coach no tiene una membresía activa"
            )

        plan = await ContentService.get_plan_by_id(membership.plan_id)
        max_mentees_raw = plan.get("maxMentees")

        try:
            max_mentees = int(max_mentees_raw) if max_mentees_raw is not None else None
        except (TypeError, ValueError):
            max_mentees = None

        if max_mentees is None:
            user_logger.warning(
                f"MENTEE_SIGNUP_NO_LIMIT | CoachID: {coach_id} | RawValue: {max_mentees_raw}"
            )
            return

        current_mentees = await MenteeProfileRepository.count_by_coach_id(coach_id)

        if current_mentees >= max_mentees:
            user_logger.warning(
                f"MENTEE_SIGNUP_LIMIT_REACHED | CoachID: {coach_id} | "
                f"Max: {max_mentees} | Current: {current_mentees}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El coach alcanzó el límite de asesorados para su plan"
            )

    @classmethod
    async def login(cls, email: str, password: str) -> str:
        user_logger.info(f"LOGIN_START | Email: {email}")

        try:
            user = await UserRepository.get_by_email(email)

            if not user:
                user_logger.warning(f"LOGIN_USER_NOT_FOUND | Email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            if not AuthUtils.verify_password(password, user.password):
                user_logger.warning(f"LOGIN_INVALID_PASSWORD | Email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            user_logger.info(f"LOGIN_CREDENTIALS_VALID | UserID: {user.id} | Email: {email}")

            token_data = {
                "sub": user.email,
                "userId": str(user.id),
                "role": user.role,
            }

            if user.role == RoleName.coach:
                user_data = await CoachProfileRepository.get_by_user_id(str(user.id))
                coach_code = await CoachCodeRepository.get_by_user_id(str(user.id))
                token_data.update({
                    "firstName": user_data.name,
                    "coachCode": coach_code.code
                })
                user_logger.debug(f"COACH_DATA_LOADED | UserID: {user.id}")

            elif user.role == RoleName.mentee:
                user_data = await MenteeProfileRepository.get_by_user_id(str(user.id))
                token_data.update({"firstName": user_data.name})
                user_logger.debug(f"MENTEE_DATA_LOADED | UserID: {user.id}")

            elif user.role == RoleName.system:
                token_data.update({"firstName": "System Admin"})
                user_logger.debug(f"SYSTEM_DATA_LOADED | UserID: {user.id}")

            access_token = AuthUtils.create_token(
                data=token_data,
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            refresh_token = AuthUtils.create_token(
                data=token_data,
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            user_logger.info(f"LOGIN_SUCCESS | UserID: {user.id} | Email: {email}")
            return {"access_token": access_token, "refresh_token": refresh_token}

        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"LOGIN_UNEXPECTED_ERROR | Email: {email} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login error"
            )

    @classmethod
    async def refresh_token(cls, refresh_token: str) -> dict:
        user_logger.info("TOKEN_REFRESH_START")

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")

            if email is None:
                user_logger.warning("TOKEN_REFRESH_INVALID_TOKEN")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            user_logger.debug(f"TOKEN_REFRESH_VALID | Email: {email}")

        except JWTError as e:
            user_logger.warning(f"TOKEN_REFRESH_JWT_ERROR | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        try:
            user = await UserRepository.get_by_email(email)

            if not user:
                user_logger.warning(f"TOKEN_REFRESH_USER_NOT_FOUND | Email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            token_data = {
                "sub": user.email,
                "userId": str(user.id),
                "role": user.role,
            }

            if user.role == RoleName.coach:
                user_data = await CoachProfileRepository.get_by_user_id(str(user.id))
                coach_code = await CoachCodeRepository.get_by_user_id(str(user.id))
                token_data.update({
                    "firstName": user_data.name,
                    "coachCode": coach_code.code
                })
            elif user.role == RoleName.mentee:
                user_data = await MenteeProfileRepository.get_by_user_id(str(user.id))
                token_data.update({"firstName": user_data.name})
            elif user.role == RoleName.system:
                token_data.update({"firstName": "System Admin"})

            new_access_token = AuthUtils.create_token(
                data=token_data,
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            new_refresh_token = AuthUtils.create_token(
                data=token_data,
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            user_logger.info(f"TOKEN_REFRESH_SUCCESS | UserID: {user.id}")
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"TOKEN_REFRESH_ERROR | Email: {email} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh error"
            )

    @classmethod
    async def get_user_profile(cls, user_id: str) -> dict:
        user_logger.info(f"GET_USER_PROFILE_START | UserID: {user_id}")

        try:
            user = await UserRepository.get_by_id(user_id)

            if not user:
                user_logger.warning(f"GET_USER_PROFILE_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            profile_data = {
                "email": user.email,
                "role": user.role
            }

            if user.role == RoleName.coach:
                coach_profile = await CoachProfileRepository.get_by_user_id(user_id)
                if coach_profile:
                    profile_data["first_name"] = coach_profile.name
                    profile_data["last_name"] = coach_profile.last_name
            elif user.role == RoleName.mentee:
                mentee_profile = await MenteeProfileRepository.get_by_user_id(user_id)
                if mentee_profile:
                    profile_data["first_name"] = mentee_profile.name
                    profile_data["last_name"] = mentee_profile.last_name

            user_logger.info(f"GET_USER_PROFILE_SUCCESS | UserID: {user_id}")
            return profile_data

        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"GET_USER_PROFILE_ERROR | UserID: {user_id} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error obteniendo perfil del usuario"
            )

    @classmethod
    async def update_user_profile(cls, user_id: str, role: str, update_data) -> dict:
        user_logger.info(f"UPDATE_USER_PROFILE_START | UserID: {user_id}")

        try:
            if role == RoleName.coach:
                profile = await CoachProfileRepository.get_by_user_id(user_id)
                if not profile:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Perfil de entrenador no encontrado"
                    )

                if update_data.first_name:
                    profile.name = update_data.first_name
                if update_data.last_name:
                    profile.last_name = update_data.last_name

                await profile.save()

            elif role == RoleName.mentee:
                profile = await MenteeProfileRepository.get_by_user_id(user_id)
                if not profile:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Perfil de asesorado no encontrado"
                    )

                if update_data.first_name:
                    profile.name = update_data.first_name
                if update_data.last_name:
                    profile.last_name = update_data.last_name

                await profile.save()

            user_logger.info(f"UPDATE_USER_PROFILE_SUCCESS | UserID: {user_id}")
            return await cls.get_user_profile(user_id)

        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"UPDATE_USER_PROFILE_ERROR | UserID: {user_id} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando perfil del usuario"
            )

    @classmethod
    async def change_password(cls, user_id: str, current_password: str, new_password: str):
        user_logger.info(f"CHANGE_PASSWORD_START | UserID: {user_id}")

        try:
            user = await UserRepository.get_by_id(user_id)

            if not user:
                user_logger.warning(f"CHANGE_PASSWORD_USER_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            if not AuthUtils.verify_password(current_password, user.password):
                user_logger.warning(f"CHANGE_PASSWORD_INVALID_CURRENT | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contraseña actual incorrecta"
                )

            user.password = AuthUtils.get_password_hash(new_password)
            await user.save()

            user_logger.info(f"CHANGE_PASSWORD_SUCCESS | UserID: {user_id}")

        except HTTPException:
            raise
        except Exception as e:
            user_logger.error(f"CHANGE_PASSWORD_ERROR | UserID: {user_id} | Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error cambiando contraseña"
            )

    @classmethod
    async def update_password_by_id(cls, user_id: str, new_password: str):
        user_logger.info(f"UPDATE_PASSWORD_BY_ID_START | UserID: {user_id}")

        try:
            if not ObjectId.is_valid(user_id):
                user_logger.warning(f"UPDATE_PASSWORD_BY_ID_INVALID_ID | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de usuario inválido"
                )

            user = await UserRepository.get_by_id(user_id)

            if not user:
                user_logger.warning(f"UPDATE_PASSWORD_BY_ID_USER_NOT_FOUND | UserID: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            user.password = AuthUtils.get_password_hash(new_password)
            await user.save()

            user_logger.info(f"UPDATE_PASSWORD_BY_ID_SUCCESS | UserID: {user_id}")

        except HTTPException:
            raise
        except Exception:
            user_logger.exception(f"UPDATE_PASSWORD_BY_ID_ERROR | UserID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando contraseña"
            )
