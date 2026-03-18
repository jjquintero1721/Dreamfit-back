from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TokenRefreshRequest(BaseModel):
    refresh_token: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    coach_code: Optional[str] = Field(default="", alias="coachCode")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
