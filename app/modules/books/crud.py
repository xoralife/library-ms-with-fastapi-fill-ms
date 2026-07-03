from typing import Optional, Tuple
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book, BookStatus


class BookCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Book:
        book = Book(**data)
        book.available_copies = book.total_copies
        self.db.add(book)
        await self.db.flush()
        return book

    async def get_by_id(self, book_id: str) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).where(Book.isbn == isbn)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        author_id: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[BookStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[list[Book], int]:
        query = select(Book)
        count_query = select(func.count(Book.id))

        if search:
            filter_cond = or_(
                Book.title.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%"),
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)
        if category_id:
            query = query.where(Book.category_id == category_id)
            count_query = count_query.where(Book.category_id == category_id)
        if author_id:
            query = query.where(Book.author_id == author_id)
            count_query = count_query.where(Book.author_id == author_id)
        if language:
            query = query.where(Book.language == language)
            count_query = count_query.where(Book.language == language)
        if status:
            query = query.where(Book.status == status)
            count_query = count_query.where(Book.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            query
            .order_by(Book.title)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, book: Book, data: dict) -> Book:
        for key, value in data.items():
            if value is not None:
                setattr(book, key, value)
        await self.db.flush()
        return book

    async def delete(self, book_id: str) -> bool:
        result = await self.db.execute(delete(Book).where(Book.id == book_id))
        return result.rowcount > 0

    async def update_available_copies(self, book_id: str, delta: int) -> None:
        result = await self.db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if book:
            book.available_copies += delta
            if book.available_copies < 0:
                book.available_copies = 0
            if book.available_copies == 0:
                book.status = BookStatus.UNAVAILABLE
            elif book.available_copies > 0 and book.status == BookStatus.UNAVAILABLE:
                book.status = BookStatus.AVAILABLE
            await self.db.flush()

    async def bulk_create(self, books_data: list[dict]) -> list[Book]:
        books = []
        for data in books_data:
            book = Book(**data)
            book.available_copies = book.total_copies
            self.db.add(book)
            books.append(book)
        await self.db.flush()
        return books
