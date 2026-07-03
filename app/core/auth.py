from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole


async def authenticate_user(db: AsyncSession, username_or_email: str, password: str) -> Optional[User]:
    stmt = select(User).where(
        (User.email == username_or_email) | (User.username == username_or_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_tokens(user: User) -> dict:
    token_data = {"sub": user.id, "role": user.role.value}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def verify_refresh_token(token: str) -> Optional[dict]:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "refresh":
        return None
    return payload


async def create_user(
    db: AsyncSession,
    email: str,
    username: str,
    password: str,
    full_name: str,
    role: UserRole = UserRole.STUDENT,
) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    return user
