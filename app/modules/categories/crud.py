from typing import Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category


class CategoryCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Category:
        category = Category(**data)
        self.db.add(category)
        await self.db.flush()
        return category

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Category], int]:
        query = select(Category)
        count_query = select(func.count(Category.id))
        if search:
            query = query.where(Category.name.ilike(f"%{search}%"))
            count_query = count_query.where(Category.name.ilike(f"%{search}%"))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Category.name).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, category: Category, data: dict) -> Category:
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)
        await self.db.flush()
        return category

    async def delete(self, category_id: str) -> bool:
        result = await self.db.execute(delete(Category).where(Category.id == category_id))
        return result.rowcount > 0

    async def count_books(self, category_id: str) -> int:
        from app.models.book import Book
        result = await self.db.execute(
            select(func.count(Book.id)).where(Book.category_id == category_id)
        )
        return result.scalar() or 0
