from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, DB, CurrentUser
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    ForgotPasswordRequest,
    AuthResponse,
)
from app.schemas.user import UserResponse
from app.schemas.common import MessageResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_auth_response(user: User, token: str, refresh_token: str) -> dict:
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role.value,
            "companyId": user.company_id,
            "companyName": user.company.name,
            "avatarUrl": user.avatar_url,
            "createdAt": user.created_at.isoformat() if user.created_at else "",
        },
        "token": token,
        "refreshToken": refresh_token,
    }


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: DB):
    user, token, refresh = auth_service.login(db, body.email, body.password)
    return _build_auth_response(user, token, refresh)


@router.post("/register", response_model=AuthResponse)
def register(body: RegisterRequest, db: DB):
    user, token, refresh = auth_service.register(
        db,
        email=body.email,
        password=body.password,
        name=body.name,
        phone=body.phone,
        role=body.role,
        company_name=body.company_name,
    )
    return _build_auth_response(user, token, refresh)


@router.post("/refresh", response_model=AuthResponse)
def refresh(body: RefreshRequest, db: DB):
    user, token, refresh_tok = auth_service.refresh_tokens(db, body.refresh_token)
    return _build_auth_response(user, token, refresh_tok)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser, db: DB):
    auth_service.logout(db, current_user.id)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(body: ForgotPasswordRequest, db: DB):
    # In production, send email with reset link
    return {"message": "Password reset instructions sent to your email"}


@router.get("/me")
def get_me(current_user: CurrentUser):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "companyId": current_user.company_id,
        "companyName": current_user.company.name,
        "avatarUrl": current_user.avatar_url,
        "createdAt": current_user.created_at.isoformat() if current_user.created_at else "",
    }
