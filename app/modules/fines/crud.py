from typing import Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.fine import Fine, FineReason, Payment


class FineCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, fine_id: str) -> Optional[Fine]:
        result = await self.db.execute(select(Fine).where(Fine.id == fine_id))
        return result.scalar_one_or_none()

    async def get_all(
        self, student_id: Optional[str] = None,
        is_paid: Optional[bool] = None,
        page: int = 1, page_size: int = 10
    ) -> Tuple[list[Fine], int]:
        query = select(Fine)
        count_query = select(func.count(Fine.id))
        if student_id:
            query = query.where(Fine.student_id == student_id)
            count_query = count_query.where(Fine.student_id == student_id)
        if is_paid is not None:
            query = query.where(Fine.is_paid == is_paid)
            count_query = count_query.where(Fine.is_paid == is_paid)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Fine.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def pay_fine(
        self, fine_id: str, payment_method: str,
        transaction_id: Optional[str] = None, received_by: Optional[str] = None
    ) -> tuple[Fine, Payment]:
        result = await self.db.execute(select(Fine).where(Fine.id == fine_id))
        fine = result.scalar_one_or_none()
        if not fine:
            raise ValueError("Fine not found")
        if fine.is_paid:
            raise ValueError("Fine already paid")

        payment = Payment(
            fine_id=fine.id,
            amount=fine.amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            payment_date=datetime.now(timezone.utc),
            received_by=received_by,
        )
        self.db.add(payment)

        fine.is_paid = True
        fine.paid_at = datetime.now(timezone.utc)
        await self.db.flush()
        return fine, payment

    async def get_student_fines(self, student_id: str) -> list[Fine]:
        result = await self.db.execute(
            select(Fine).where(Fine.student_id == student_id).order_by(Fine.created_at.desc())
        )
        return list(result.scalars().all())
