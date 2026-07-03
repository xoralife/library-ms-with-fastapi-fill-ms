from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    ChangePasswordRequest,
    AdminResetPasswordRequest,
    LoginResponse,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.core.permissions import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.login(data.username_or_email, data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    _: User = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    try:
        user = await service.register(data)
        from app.core.auth import create_tokens
        tokens = create_tokens(user)
        return TokenResponse(**tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    data: TokenRefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.refresh_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: User = Depends(get_current_user)):
    return None


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    try:
        await service.change_password(current_user.id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/admin/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def admin_reset_password(
    data: AdminResetPasswordRequest,
    _: User = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    try:
        await service.admin_reset_password(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
