from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.notification import NotificationResponse, NotificationListResponse
from app.schemas.common import MessageResponse
from app.modules.notifications.crud import NotificationCRUD
from app.core.permissions import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_crud(db: AsyncSession = Depends(get_db)) -> NotificationCRUD:
    return NotificationCRUD(db)


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    crud: NotificationCRUD = Depends(get_crud),
):
    items, total = await crud.get_user_notifications(
        current_user.id, unread_only=unread_only, page=page, page_size=page_size
    )
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    crud: NotificationCRUD = Depends(get_crud),
):
    notification = await crud.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationResponse.model_validate(notification)


@router.put("/read-all", response_model=MessageResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    crud: NotificationCRUD = Depends(get_crud),
):
    count = await crud.mark_all_as_read(current_user.id)
    return MessageResponse(message=f"{count} notifications marked as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    crud: NotificationCRUD = Depends(get_crud),
):
    deleted = await crud.delete(notification_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return MessageResponse(message="Notification deleted")
