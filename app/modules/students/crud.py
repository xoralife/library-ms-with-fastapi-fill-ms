from typing import Optional, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import Student
from app.models.user import User, UserRole
from app.core.auth import create_user


class StudentCRUD:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Student:
        user = await create_user(
            db=self.db,
            email=data.pop("email"),
            username=data.pop("username"),
            password=data.pop("password"),
            full_name=data.pop("full_name"),
            role=UserRole.STUDENT,
        )
        student = Student(user_id=user.id, **data)
        self.db.add(student)
        await self.db.flush()
        return student

    async def get_by_id(self, student_id: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> Tuple[list[Student], int]:
        query = select(Student)
        count_query = select(func.count(Student.id))
        if search:
            query = query.join(User).where(
                (User.full_name.ilike(f"%{search}%"))
                | (Student.student_card_number.ilike(f"%{search}%"))
                | (Student.department.ilike(f"%{search}%"))
            )
            count_query = count_query.join(User).where(
                (User.full_name.ilike(f"%{search}%"))
                | (Student.student_card_number.ilike(f"%{search}%"))
                | (Student.department.ilike(f"%{search}%"))
            )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Student.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, student: Student, data: dict) -> Student:
        for key, value in data.items():
            if value is not None:
                setattr(student, key, value)
        await self.db.flush()
        return student

    async def delete(self, student_id: str) -> bool:
        result = await self.db.execute(delete(Student).where(Student.id == student_id))
        return result.rowcount > 0

    async def toggle_block(self, student_id: str) -> Optional[Student]:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if student:
            student.is_blocked = not student.is_blocked
            await self.db.flush()
        return student
