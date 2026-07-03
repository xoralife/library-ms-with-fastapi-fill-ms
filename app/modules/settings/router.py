from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.setting import SettingUpdate, SettingResponse, SettingsListResponse
from app.schemas.common import MessageResponse
from app.modules.settings.crud import SettingCRUD
from app.core.permissions import require_admin_only
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["Settings"])


def get_crud(db: AsyncSession = Depends(get_db)) -> SettingCRUD:
    return SettingCRUD(db)


@router.get("", response_model=SettingsListResponse)
async def get_settings(
    _: User = Depends(require_admin_only),
    crud: SettingCRUD = Depends(get_crud),
):
    settings = await crud.get_all()
    return SettingsListResponse(
        items=[SettingResponse.model_validate(s) for s in settings]
    )


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    _: User = Depends(require_admin_only),
    crud: SettingCRUD = Depends(get_crud),
):
    setting = await crud.get_by_key(key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return SettingResponse.model_validate(setting)


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingUpdate,
    _: User = Depends(require_admin_only),
    crud: SettingCRUD = Depends(get_crud),
):
    setting = await crud.update_value(key, data.value)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return SettingResponse.model_validate(setting)
