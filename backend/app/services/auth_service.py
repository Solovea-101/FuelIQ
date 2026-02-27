from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.company import Company
from app.models.refresh_token import RefreshToken
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.config import settings


def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    access_token = create_access_token(user.id, user.role.value, user.company_id)
    refresh_tok = create_refresh_token()

    # Store hashed refresh token
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_tok),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()

    return user, access_token, refresh_tok


def register(
    db: Session,
    email: str,
    password: str,
    name: str,
    phone: str,
    role: str,
    company_name: str | None = None,
) -> tuple[User, str, str]:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise BadRequestException("Email already registered")

    user_role = UserRole(role)

    # Create or find company
    if company_name:
        company = Company(name=company_name)
        db.add(company)
        db.flush()
    else:
        # For drivers without company, create a default
        company = db.query(Company).first()
        if not company:
            company = Company(name="Default Company")
            db.add(company)
            db.flush()

    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        phone=phone,
        role=user_role,
        company_id=company.id,
    )
    db.add(user)
    db.flush()

    access_token = create_access_token(user.id, user.role.value, user.company_id)
    refresh_tok = create_refresh_token()

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_tok),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()
    db.refresh(user)

    return user, access_token, refresh_tok


def refresh_tokens(db: Session, refresh_token_str: str) -> tuple[User, str, str]:
    token_hash = hash_token(refresh_token_str)
    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    if not db_token:
        raise UnauthorizedException("Invalid or expired refresh token")

    # Revoke old token
    db_token.revoked = True

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise UnauthorizedException("User not found")

    # Issue new tokens
    access_token = create_access_token(user.id, user.role.value, user.company_id)
    new_refresh = create_refresh_token()

    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_db_token)
    db.commit()

    return user, access_token, new_refresh


def logout(db: Session, user_id: str) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False,
    ).update({"revoked": True})
    db.commit()
