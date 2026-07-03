from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import authenticate_user, create_tokens, verify_refresh_token, create_user
from app.core.security import hash_password, decode_token, create_access_token
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest,
    ChangePasswordRequest,
    AdminResetPasswordRequest,
    UserResponse,
    LoginResponse,
    TokenResponse,
    TokenRefreshResponse,
)
from app.models.base import UUIDMixin


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, username_or_email: str, password: str) -> LoginResponse:
        user = await authenticate_user(self.db, username_or_email, password)
        if not user:
            raise ValueError("Invalid credentials or inactive account")

        tokens = create_tokens(user)
        user_data = UserResponse.model_validate(user)
        return LoginResponse(**tokens, user=user_data)

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self.db.execute(
            select(User).where(
                (User.email == data.email) | (User.username == data.username)
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email or username already registered")

        user = await create_user(
            db=self.db,
            email=data.email,
            username=data.username,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
        )
        return UserResponse.model_validate(user)

    async def refresh_token(self, refresh_token: str) -> TokenRefreshResponse:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        token_data = {"sub": user.id, "role": user.role.value}
        access_token = create_access_token(data=token_data)
        return TokenRefreshResponse(access_token=access_token)

    async def change_password(
        self, user_id: str, data: ChangePasswordRequest
    ) -> None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        from app.core.security import verify_password as vp
        if not vp(data.old_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        user.hashed_password = hash_password(data.new_password)

    async def admin_reset_password(self, data: AdminResetPasswordRequest) -> None:
        result = await self.db.execute(select(User).where(User.id == data.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        user.hashed_password = hash_password(data.new_password)
