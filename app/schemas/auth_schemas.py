from pydantic import BaseModel, EmailStr, Field


class TokenRefreshRequest(BaseModel):
    refresh_token: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
