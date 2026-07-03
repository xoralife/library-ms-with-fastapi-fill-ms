from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book, BookStatus
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.librarian import Librarian
from app.models.borrow import BorrowRecord, BorrowStatus
from app.models.fine import Fine
from app.models.activity_log import ActivityLog


class ReportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self) -> dict:
        books_result = await self.db.execute(select(func.count(Book.id)))
        total_books = books_result.scalar() or 0

        students_result = await self.db.execute(select(func.count(Student.id)))
        total_students = students_result.scalar() or 0

        librarians_result = await self.db.execute(select(func.count(Librarian.id)))
        total_librarians = librarians_result.scalar() or 0

        borrowed_result = await self.db.execute(
            select(func.count(BorrowRecord.id)).where(BorrowRecord.status == BorrowStatus.BORROWED)
        )
        total_borrowed = borrowed_result.scalar() or 0

        available_result = await self.db.execute(
            select(func.sum(Book.available_copies))
        )
        total_available = available_result.scalar() or 0

        overdue_result = await self.db.execute(
            select(func.count(BorrowRecord.id)).where(
                and_(
                    BorrowRecord.status == BorrowStatus.BORROWED,
                    BorrowRecord.due_date < datetime.now(timezone.utc),
                )
            )
        )
        total_overdue = overdue_result.scalar() or 0

        fines_result = await self.db.execute(
            select(func.coalesce(func.sum(Fine.amount), 0)).where(Fine.is_paid == True)
        )
        total_fines = float(fines_result.scalar() or 0)

        logs_result = await self.db.execute(
            select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(10)
        )
        recent_activities = [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "created_at": str(log.created_at),
            }
            for log in logs_result.scalars().all()
        ]

        return {
            "total_books": total_books,
            "total_students": total_students,
            "total_librarians": total_librarians,
            "total_borrowed": total_borrowed,
            "total_available": total_available,
            "total_overdue": total_overdue,
            "total_fines_collected": total_fines,
            "recent_activities": recent_activities,
        }

    async def get_report_data(self, report_type: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        now = datetime.now(timezone.utc)

        if report_type == "borrowed":
            query = select(BorrowRecord).where(BorrowRecord.status == BorrowStatus.BORROWED)
            count_query = select(func.count(BorrowRecord.id)).where(BorrowRecord.status == BorrowStatus.BORROWED)
        elif report_type == "returned":
            query = select(BorrowRecord).where(BorrowRecord.status == BorrowStatus.RETURNED)
            count_query = select(func.count(BorrowRecord.id)).where(BorrowRecord.status == BorrowStatus.RETURNED)
        elif report_type == "overdue":
            query = select(BorrowRecord).where(
                and_(
                    BorrowRecord.status == BorrowStatus.BORROWED,
                    BorrowRecord.due_date < now,
                )
            )
            count_query = select(func.count(BorrowRecord.id)).where(
                and_(
                    BorrowRecord.status == BorrowStatus.BORROWED,
                    BorrowRecord.due_date < now,
                )
            )
        elif report_type == "fines":
            query = select(Fine).where(Fine.is_paid == False)
            count_query = select(func.count(Fine.id)).where(Fine.is_paid == False)
        else:
            query = select(BorrowRecord)
            count_query = select(func.count(BorrowRecord.id))

        if start_date:
            from datetime import datetime as dt
            start_dt = dt.fromisoformat(start_date)
            query = query.where(BorrowRecord.created_at >= start_dt)
            count_query = count_query.where(BorrowRecord.created_at >= start_dt)
        if end_date:
            from datetime import datetime as dt
            end_dt = dt.fromisoformat(end_date)
            query = query.where(BorrowRecord.created_at <= end_dt)
            count_query = count_query.where(BorrowRecord.created_at <= end_dt)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(BorrowRecord.created_at.desc()).limit(100)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {"type": report_type, "total": total, "items": items}

    async def get_export_data(self, report_type: str) -> tuple[list[str], list[list]]:
        data = await self.get_report_data(report_type)
        if report_type in ("borrowed", "returned", "overdue"):
            headers = ["ID", "Book ID", "Student ID", "Issue Date", "Due Date", "Status"]
            rows = [
                [str(r.id), str(r.book_id), str(r.student_id), str(r.issue_date), str(r.due_date), r.status.value]
                for r in data["items"]
            ]
        elif report_type == "fines":
            headers = ["ID", "Amount", "Reason", "Status", "Created"]
            rows = [
                [str(f.id), str(f.amount), f.reason.value, "Unpaid" if not f.is_paid else "Paid", str(f.created_at)]
                for f in data["items"]
            ]
        else:
            headers = ["ID", "Type", "Count"]
            rows = [[data["type"], str(data["total"])]]
        return headers, rows
