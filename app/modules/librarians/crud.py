from typing import Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.librarian import Librarian
from app.models.user import User, UserRole
from app.core.auth import create_user


class LibrarianCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Librarian:
        user = await create_user(
            db=self.db,
            email=data.pop("email"),
            username=data.pop("username"),
            password=data.pop("password"),
            full_name=data.pop("full_name"),
            role=UserRole.LIBRARIAN,
        )
        librarian = Librarian(user_id=user.id, **data)
        self.db.add(librarian)
        await self.db.flush()
        return librarian

    async def get_by_id(self, librarian_id: str) -> Optional[Librarian]:
        result = await self.db.execute(
            select(Librarian).where(Librarian.id == librarian_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Librarian], int]:
        query = select(Librarian)
        count_query = select(func.count(Librarian.id))
        if search:
            query = query.join(User).where(
                (User.full_name.ilike(f"%{search}%")) | (Librarian.employee_id.ilike(f"%{search}%"))
            )
            count_query = count_query.join(User).where(
                (User.full_name.ilike(f"%{search}%")) | (Librarian.employee_id.ilike(f"%{search}%"))
            )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Librarian.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, librarian: Librarian, data: dict) -> Librarian:
        for key, value in data.items():
            if value is not None:
                setattr(librarian, key, value)
        await self.db.flush()
        return librarian

    async def delete(self, librarian_id: str) -> bool:
        result = await self.db.execute(delete(Librarian).where(Librarian.id == librarian_id))
        return result.rowcount > 0

    async def toggle_active(self, librarian_id: str) -> Optional[Librarian]:
        result = await self.db.execute(select(Librarian).where(Librarian.id == librarian_id))
        librarian = result.scalar_one_or_none()
        if librarian:
            librarian.is_active = not librarian.is_active
            user = await self.db.execute(select(User).where(User.id == librarian.user_id))
            user_obj = user.scalar_one_or_none()
            if user_obj:
                user_obj.is_active = librarian.is_active
            await self.db.flush()
        return librarian
