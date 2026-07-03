from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserAdminResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.users.crud import UserCRUD
from app.models.user import UserRole
from app.core.permissions import require_admin_only
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


def get_crud(db: AsyncSession = Depends(get_db)) -> UserCRUD:
    return UserCRUD(db)


@router.get("", response_model=PaginatedResponse)
async def list_users(
    search: str = Query(None),
    role: UserRole = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_admin_only),
    crud: UserCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, role=role, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[UserAdminResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserAdminResponse)
async def get_user(
    user_id: str,
    _: User = Depends(require_admin_only),
    crud: UserCRUD = Depends(get_crud),
):
    user = await crud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserAdminResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserAdminResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    _: User = Depends(require_admin_only),
    crud: UserCRUD = Depends(get_crud),
):
    user = await crud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = await crud.update(user, data.model_dump(exclude_unset=True))
    return UserAdminResponse.model_validate(updated)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    _: User = Depends(require_admin_only),
    crud: UserCRUD = Depends(get_crud),
):
    deleted = await crud.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MessageResponse(message="User deleted successfully")
