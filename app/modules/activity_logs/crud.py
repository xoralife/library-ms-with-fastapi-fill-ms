from typing import Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog


class ActivityLogCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: str, action: str, entity_type: str,
        entity_id: Optional[str] = None, details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> ActivityLog:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_all(
        self, user_id: Optional[str] = None, action: Optional[str] = None,
        entity_type: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[ActivityLog], int]:
        query = select(ActivityLog)
        count_query = select(func.count(ActivityLog.id))
        if user_id:
            query = query.where(ActivityLog.user_id == user_id)
            count_query = count_query.where(ActivityLog.user_id == user_id)
        if action:
            query = query.where(ActivityLog.action == action)
            count_query = count_query.where(ActivityLog.action == action)
        if entity_type:
            query = query.where(ActivityLog.entity_type == entity_type)
            count_query = count_query.where(ActivityLog.entity_type == entity_type)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
