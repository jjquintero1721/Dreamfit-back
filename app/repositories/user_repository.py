from typing import Optional

from app.models.user import User


class UserRepository:
    @staticmethod
    async def create(user_data: dict) -> User:
        user = User(**user_data)
        await user.insert()
        return user

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        return await User.get(user_id)

    @staticmethod
    async def delete(user: User) -> bool:
        await user.delete()
        return True