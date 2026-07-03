from typing import Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.publisher import Publisher


class PublisherCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Publisher:
        publisher = Publisher(**data)
        self.db.add(publisher)
        await self.db.flush()
        return publisher

    async def get_by_id(self, publisher_id: str) -> Optional[Publisher]:
        result = await self.db.execute(select(Publisher).where(Publisher.id == publisher_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Publisher], int]:
        query = select(Publisher)
        count_query = select(func.count(Publisher.id))
        if search:
            query = query.where(Publisher.name.ilike(f"%{search}%"))
            count_query = count_query.where(Publisher.name.ilike(f"%{search}%"))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Publisher.name).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, publisher: Publisher, data: dict) -> Publisher:
        for key, value in data.items():
            if value is not None:
                setattr(publisher, key, value)
        await self.db.flush()
        return publisher

    async def delete(self, publisher_id: str) -> bool:
        result = await self.db.execute(delete(Publisher).where(Publisher.id == publisher_id))
        return result.rowcount > 0
