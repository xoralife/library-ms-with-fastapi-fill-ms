from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.activity_log import ActivityLogResponse
from app.schemas.common import PaginatedResponse
from app.modules.activity_logs.crud import ActivityLogCRUD
from app.core.permissions import require_admin_only
from app.models.user import User

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


def get_crud(db: AsyncSession = Depends(get_db)) -> ActivityLogCRUD:
    return ActivityLogCRUD(db)


@router.get("", response_model=PaginatedResponse)
async def list_activity_logs(
    user_id: str = Query(None),
    action: str = Query(None),
    entity_type: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_admin_only),
    crud: ActivityLogCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(
        user_id=user_id, action=action, entity_type=entity_type, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[ActivityLogResponse.model_validate(log) for log in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
