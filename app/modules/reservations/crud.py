from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reservation import Reservation, ReservationStatus


class ReservationCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, book_id: str, student_id: str, notes: Optional[str] = None) -> Reservation:
        result = await self.db.execute(
            select(func.count(Reservation.id)).where(
                (Reservation.book_id == book_id)
                & (Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.APPROVED]))
            )
        )
        current_queue = result.scalar() or 0

        now = datetime.now(timezone.utc)
        expiry = now + timedelta(days=3)

        reservation = Reservation(
            book_id=book_id,
            student_id=student_id,
            reservation_date=now,
            expiry_date=expiry,
            queue_position=current_queue + 1,
            notes=notes,
        )
        self.db.add(reservation)
        await self.db.flush()
        return reservation

    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, status: Optional[ReservationStatus] = None,
        book_id: Optional[str] = None,
        student_id: Optional[str] = None,
        page: int = 1, page_size: int = 10
    ) -> Tuple[list[Reservation], int]:
        query = select(Reservation)
        count_query = select(func.count(Reservation.id))
        if status:
            query = query.where(Reservation.status == status)
            count_query = count_query.where(Reservation.status == status)
        if book_id:
            query = query.where(Reservation.book_id == book_id)
            count_query = count_query.where(Reservation.book_id == book_id)
        if student_id:
            query = query.where(Reservation.student_id == student_id)
            count_query = count_query.where(Reservation.student_id == student_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Reservation.queue_position).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def cancel(self, reservation_id: str) -> Optional[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        reservation = result.scalar_one_or_none()
        if reservation and reservation.status == ReservationStatus.PENDING:
            reservation.status = ReservationStatus.CANCELLED
            await self.db.flush()
        return reservation

    async def approve(self, reservation_id: str) -> Optional[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        reservation = result.scalar_one_or_none()
        if reservation and reservation.status == ReservationStatus.PENDING:
            reservation.status = ReservationStatus.APPROVED
            await self.db.flush()
        return reservation

    async def reject(self, reservation_id: str) -> Optional[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        reservation = result.scalar_one_or_none()
        if reservation and reservation.status == ReservationStatus.PENDING:
            reservation.status = ReservationStatus.CANCELLED
            await self.db.flush()
        return reservation

    async def get_student_reservations(self, student_id: str) -> list[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(Reservation.student_id == student_id)
            .order_by(Reservation.created_at.desc())
        )
        return list(result.scalars().all())
