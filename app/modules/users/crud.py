from typing import Optional, Tuple
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.core.security import hash_password


class UserCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, role: Optional[UserRole] = None,
        page: int = 1, page_size: int = 10
    ) -> Tuple[list[User], int]:
        query = select(User)
        count_query = select(func.count(User.id))
        if search:
            filter_cond = or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.flush()
        return user

    async def delete(self, user_id: str) -> bool:
        result = await self.db.execute(delete(User).where(User.id == user_id))
        return result.rowcount > 0
