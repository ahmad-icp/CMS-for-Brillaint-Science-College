import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.authentication.models import RefreshToken, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user: User) -> str:
    now = _utc_now()
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.id,
        "college_id": user.college_id,
        "role": user.role,
        "type": "access",
        "exp": expires_at,
        "iat": now,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if payload.get("type") != "access" or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return payload


class AuthenticationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def authenticate(self, username: str, password: str, college_id: str) -> User:
        user = self.db.scalar(
            select(User).where(
                User.college_id == college_id,
                or_(User.username == username, User.email == username),
            )
        )
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        return user

    def issue_tokens(self, user: User) -> tuple[str, str]:
        access_token = create_access_token(user)
        refresh_token = secrets.token_urlsafe(48)
        expires_at = _utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.db.add(RefreshToken(user_id=user.id, token_hash=_hash_token(refresh_token), expires_at=expires_at))
        self.db.commit()
        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        now = _utc_now()
        stored = self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == _hash_token(refresh_token)))
        expires_at = None
        if stored is not None:
            expires_at = stored.expires_at if stored.expires_at.tzinfo else stored.expires_at.replace(tzinfo=UTC)
        if (
            stored is None
            or stored.revoked_at is not None
            or expires_at is None
            or expires_at <= now
            or not stored.user.is_active
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        stored.revoked_at = now
        access_token, new_refresh_token = self.issue_tokens(stored.user)
        return access_token, new_refresh_token

    def logout(self, refresh_token: str) -> None:
        stored = self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == _hash_token(refresh_token)))
        if stored and stored.revoked_at is None:
            stored.revoked_at = _utc_now()
            self.db.commit()
