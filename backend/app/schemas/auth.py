from pydantic import EmailStr, Field

from app.schemas.common import CamelModel
from app.schemas.user import UserResponse


class LoginRequest(CamelModel):
    email: EmailStr
    password: str


class RegisterRequest(CamelModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    role: str
    company_name: str | None = Field(None, alias="companyName")


class RefreshRequest(CamelModel):
    refresh_token: str = Field(alias="refreshToken")


class ForgotPasswordRequest(CamelModel):
    email: EmailStr


class AuthResponse(CamelModel):
    user: UserResponse
    token: str
    refresh_token: str = Field(alias="refreshToken")
