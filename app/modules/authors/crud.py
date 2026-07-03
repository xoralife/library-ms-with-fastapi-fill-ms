from typing import Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.author import Author


class AuthorCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Author:
        author = Author(**data)
        self.db.add(author)
        await self.db.flush()
        return author

    async def get_by_id(self, author_id: str) -> Optional[Author]:
        result = await self.db.execute(select(Author).where(Author.id == author_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Author], int]:
        query = select(Author)
        count_query = select(func.count(Author.id))
        if search:
            query = query.where(Author.name.ilike(f"%{search}%"))
            count_query = count_query.where(Author.name.ilike(f"%{search}%"))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Author.name).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, author: Author, data: dict) -> Author:
        for key, value in data.items():
            if value is not None:
                setattr(author, key, value)
        await self.db.flush()
        return author

    async def delete(self, author_id: str) -> bool:
        result = await self.db.execute(delete(Author).where(Author.id == author_id))
        return result.rowcount > 0
