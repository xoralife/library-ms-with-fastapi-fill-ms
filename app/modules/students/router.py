from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.students.crud import StudentCRUD
from app.core.permissions import require_admin, require_librarian, get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/students", tags=["Students"])


def get_crud(db: AsyncSession = Depends(get_db)) -> StudentCRUD:
    return StudentCRUD(db)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    _: User = Depends(require_librarian),
    crud: StudentCRUD = Depends(get_crud),
):
    student = await crud.create(data.model_dump())
    return StudentResponse.model_validate(student)


@router.get("", response_model=PaginatedResponse)
async def list_students(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_librarian),
    crud: StudentCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[StudentResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/my", response_model=StudentResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    crud: StudentCRUD = Depends(get_crud),
):
    student = await crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return StudentResponse.model_validate(student)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    _: User = Depends(require_librarian),
    crud: StudentCRUD = Depends(get_crud),
):
    student = await crud.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    data: StudentUpdate,
    _: User = Depends(require_librarian),
    crud: StudentCRUD = Depends(get_crud),
):
    student = await crud.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    updated = await crud.update(student, data.model_dump(exclude_unset=True))
    return StudentResponse.model_validate(updated)


@router.put("/{student_id}/block", response_model=StudentResponse)
async def toggle_block_student(
    student_id: str,
    _: User = Depends(require_admin),
    crud: StudentCRUD = Depends(get_crud),
):
    student = await crud.toggle_block(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    status_text = "blocked" if student.is_blocked else "unblocked"
    return StudentResponse.model_validate(student)
