from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.borrow import (
    IssueBookRequest, ReturnBookRequest, RenewBookRequest,
    LostDamagedRequest, BorrowRecordResponse, BorrowListResponse,
)
from app.schemas.common import MessageResponse
from app.modules.borrowing.crud import BorrowCRUD
from app.core.permissions import require_admin, require_librarian, get_current_user
from app.models.user import User, UserRole
from app.models.borrow import BorrowStatus

router = APIRouter(prefix="/borrow", tags=["Borrowing"])


def get_crud(db: AsyncSession = Depends(get_db)) -> BorrowCRUD:
    return BorrowCRUD(db)


@router.post("/issue", response_model=BorrowRecordResponse, status_code=status.HTTP_201_CREATED)
async def issue_book(
    data: IssueBookRequest,
    current_user: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    try:
        from app.modules.librarians.crud import LibrarianCRUD
        lib_crud = LibrarianCRUD(crud.db)
        librarian = await lib_crud.get_by_user_id(current_user.id)
        if not librarian:
            raise ValueError("Librarian profile not found")

        record = await crud.issue_book(
            book_id=data.book_id,
            student_id=data.student_id,
            librarian_id=librarian.id,
            notes=data.notes,
        )
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/return", response_model=BorrowRecordResponse)
async def return_book(
    data: ReturnBookRequest,
    _: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    try:
        record = await crud.return_book(data.borrow_record_id, data.notes)
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/renew", response_model=BorrowRecordResponse)
async def renew_book(
    data: RenewBookRequest,
    current_user: User = Depends(get_current_user),
    crud: BorrowCRUD = Depends(get_crud),
):
    try:
        record = await crud.get_by_id(data.borrow_record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        if current_user.role == UserRole.STUDENT:
            from app.modules.students.crud import StudentCRUD
            student_crud = StudentCRUD(crud.db)
            student = await student_crud.get_by_user_id(current_user.id)
            if not student or student.id != record.student_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your borrow record")
        record = await crud.renew_book(data.borrow_record_id)
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/lost", response_model=BorrowRecordResponse)
async def mark_lost(
    data: LostDamagedRequest,
    _: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    try:
        record = await crud.mark_lost_or_damaged(data.borrow_record_id, BorrowStatus.LOST, data.notes)
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/damaged", response_model=BorrowRecordResponse)
async def mark_damaged(
    data: LostDamagedRequest,
    _: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    try:
        record = await crud.mark_lost_or_damaged(data.borrow_record_id, BorrowStatus.DAMAGED, data.notes)
        return BorrowRecordResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/records", response_model=BorrowListResponse)
async def list_borrow_records(
    status: str = Query(None),
    student_id: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    borrow_status = BorrowStatus(status) if status else None
    items, total = await crud.get_all(
        status=borrow_status, student_id=student_id, page=page, page_size=page_size
    )
    return BorrowListResponse(
        items=[BorrowRecordResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/records/{record_id}", response_model=BorrowRecordResponse)
async def get_borrow_record(
    record_id: str,
    _: User = Depends(require_librarian),
    crud: BorrowCRUD = Depends(get_crud),
):
    record = await crud.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found")
    return BorrowRecordResponse.model_validate(record)


@router.get("/my-current", response_model=list[BorrowRecordResponse])
async def my_current_borrows(
    current_user: User = Depends(get_current_user),
    crud: BorrowCRUD = Depends(get_crud),
):
    from app.modules.students.crud import StudentCRUD
    student_crud = StudentCRUD(crud.db)
    student = await student_crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    records = await crud.get_student_current(student.id)
    return [BorrowRecordResponse.model_validate(r) for r in records]


@router.get("/history", response_model=BorrowListResponse)
async def my_borrow_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    crud: BorrowCRUD = Depends(get_crud),
):
    from app.modules.students.crud import StudentCRUD
    student_crud = StudentCRUD(crud.db)
    student = await student_crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    items, total = await crud.get_student_history(student.id, page, page_size)
    return BorrowListResponse(
        items=[BorrowRecordResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
