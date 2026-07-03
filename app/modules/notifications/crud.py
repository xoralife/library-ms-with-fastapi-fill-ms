from typing import Optional, Tuple
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType


class NotificationCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, title: str, message: str, type: NotificationType = NotificationType.GENERAL) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
            count_query = count_query.where(Notification.is_read == False)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        result = await self.db.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.db.flush()
        return notification

    async def mark_all_as_read(self, user_id: str) -> int:
        result = await self.db.execute(
            update(Notification).where(
                (Notification.user_id == user_id) & (Notification.is_read == False)
            ).values(is_read=True)
        )
        await self.db.flush()
        return result.rowcount

    async def delete(self, notification_id: str) -> bool:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification:
            await self.db.delete(notification)
            await self.db.flush()
            return True
        return False
