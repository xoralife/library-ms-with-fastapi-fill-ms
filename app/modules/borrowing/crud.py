from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.borrow import BorrowRecord, BorrowStatus
from app.models.book import Book, BookStatus
from app.models.student import Student
from app.models.fine import Fine, FineReason
from app.modules.books.crud import BookCRUD


class BorrowCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.book_crud = BookCRUD(db)

    async def issue_book(
        self, book_id: str, student_id: str, librarian_id: str, notes: Optional[str] = None
    ) -> BorrowRecord:
        student = await self.db.execute(select(Student).where(Student.id == student_id))
        student_obj = student.scalar_one_or_none()
        if not student_obj or student_obj.is_blocked:
            raise ValueError("Student is blocked or not found")

        book = await self.db.execute(select(Book).where(Book.id == book_id))
        book_obj = book.scalar_one_or_none()
        if not book_obj or book_obj.available_copies < 1:
            raise ValueError("Book not available")

        from app.config import get_settings
        settings = get_settings()

        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=14)

        record = BorrowRecord(
            book_id=book_id,
            student_id=student_id,
            librarian_id=librarian_id,
            issue_date=now,
            due_date=due_date,
            notes=notes,
        )
        self.db.add(record)
        await self.db.flush()

        await self.book_crud.update_available_copies(book_id, -1)
        return record

    async def return_book(self, record_id: str, notes: Optional[str] = None) -> BorrowRecord:
        result = await self.db.execute(select(BorrowRecord).where(BorrowRecord.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Borrow record not found")

        now = datetime.now(timezone.utc)
        record.return_date = now
        record.status = BorrowStatus.RETURNED
        if notes:
            record.notes = notes

        await self.book_crud.update_available_copies(record.book_id, 1)

        if now > record.due_date:
            overdue_days = (now - record.due_date).days
            from app.config import get_settings
            settings = get_settings()
            fine_amount = overdue_days * 0.50
            fine = Fine(
                borrow_record_id=record.id,
                student_id=record.student_id,
                amount=fine_amount,
                reason=FineReason.OVERDUE,
            )
            self.db.add(fine)

        await self.db.flush()
        return record

    async def renew_book(self, record_id: str) -> BorrowRecord:
        result = await self.db.execute(select(BorrowRecord).where(BorrowRecord.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Borrow record not found")
        if record.renewal_count >= record.max_renewals:
            raise ValueError("Maximum renewal limit reached")
        if record.status != BorrowStatus.BORROWED and record.status != BorrowStatus.OVERDUE:
            raise ValueError("Book cannot be renewed in current status")

        record.due_date += timedelta(days=14)
        record.renewal_count += 1
        record.status = BorrowStatus.BORROWED
        await self.db.flush()
        return record

    async def mark_lost_or_damaged(self, record_id: str, status: BorrowStatus, notes: Optional[str] = None) -> BorrowRecord:
        result = await self.db.execute(select(BorrowRecord).where(BorrowRecord.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError("Borrow record not found")

        record.status = status
        record.return_date = datetime.now(timezone.utc)
        if notes:
            record.notes = notes

        book_result = await self.db.execute(select(Book).where(Book.id == record.book_id))
        book = book_result.scalar_one_or_none()
        if book:
            book.total_copies -= 1
            if book.total_copies < 0:
                book.total_copies = 0
            if book.available_copies > book.total_copies:
                book.available_copies = book.total_copies

        reason = FineReason.LOST if status == BorrowStatus.LOST else FineReason.DAMAGED
        from app.config import get_settings
        settings = get_settings()
        fine_amount = 50.0 if status == BorrowStatus.LOST else 25.0
        fine = Fine(
            borrow_record_id=record.id,
            student_id=record.student_id,
            amount=fine_amount,
            reason=reason,
            is_paid=False,
        )
        self.db.add(fine)
        await self.db.flush()
        return record

    async def get_by_id(self, record_id: str) -> Optional[BorrowRecord]:
        result = await self.db.execute(
            select(BorrowRecord).where(BorrowRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[BorrowStatus] = None,
        student_id: Optional[str] = None,
        book_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[list[BorrowRecord], int]:
        query = select(BorrowRecord)
        count_query = select(func.count(BorrowRecord.id))

        if status:
            query = query.where(BorrowRecord.status == status)
            count_query = count_query.where(BorrowRecord.status == status)
        if student_id:
            query = query.where(BorrowRecord.student_id == student_id)
            count_query = count_query.where(BorrowRecord.student_id == student_id)
        if book_id:
            query = query.where(BorrowRecord.book_id == book_id)
            count_query = count_query.where(BorrowRecord.book_id == book_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(BorrowRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_student_current(self, student_id: str) -> list[BorrowRecord]:
        result = await self.db.execute(
            select(BorrowRecord).where(
                and_(
                    BorrowRecord.student_id == student_id,
                    BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.OVERDUE]),
                )
            ).order_by(BorrowRecord.due_date)
        )
        return list(result.scalars().all())

    async def get_student_history(self, student_id: str, page: int = 1, page_size: int = 10) -> Tuple[list[BorrowRecord], int]:
        return await self.get_all(student_id=student_id, page=page, page_size=page_size)
