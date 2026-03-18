from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., alias="currentPassword")
    new_password: str = Field(..., alias="newPassword")


class UpdatePasswordRequest(BaseModel):
    new_password: str = Field(..., alias="newPassword")


class UserProfileResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str