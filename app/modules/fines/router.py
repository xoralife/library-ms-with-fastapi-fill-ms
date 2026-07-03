from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.fine import FineResponse, FineListResponse, PayFineRequest
from app.schemas.common import MessageResponse
from app.modules.fines.crud import FineCRUD
from app.core.permissions import require_admin, get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/fines", tags=["Fines"])


def get_crud(db: AsyncSession = Depends(get_db)) -> FineCRUD:
    return FineCRUD(db)


@router.get("", response_model=FineListResponse)
async def list_fines(
    is_paid: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    crud: FineCRUD = Depends(get_crud),
):
    student_id = None
    if current_user.role == UserRole.STUDENT:
        from app.modules.students.crud import StudentCRUD
        student_crud = StudentCRUD(crud.db)
        student = await student_crud.get_by_user_id(current_user.id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
        student_id = student.id
    items, total = await crud.get_all(student_id=student_id, is_paid=is_paid, page=page, page_size=page_size)
    return FineListResponse(
        items=[FineResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/my", response_model=list[FineResponse])
async def my_fines(
    current_user: User = Depends(get_current_user),
    crud: FineCRUD = Depends(get_crud),
):
    from app.modules.students.crud import StudentCRUD
    student_crud = StudentCRUD(crud.db)
    student = await student_crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    fines = await crud.get_student_fines(student.id)
    return [FineResponse.model_validate(f) for f in fines]


@router.get("/{fine_id}", response_model=FineResponse)
async def get_fine(
    fine_id: str,
    current_user: User = Depends(get_current_user),
    crud: FineCRUD = Depends(get_crud),
):
    fine = await crud.get_by_id(fine_id)
    if not fine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fine not found")
    return FineResponse.model_validate(fine)


@router.post("/{fine_id}/pay", response_model=MessageResponse)
async def pay_fine(
    fine_id: str,
    data: PayFineRequest,
    current_user: User = Depends(get_current_user),
    crud: FineCRUD = Depends(get_crud),
):
    try:
        received_by = None
        if current_user.role in [UserRole.ADMIN, UserRole.LIBRARIAN]:
            from app.modules.librarians.crud import LibrarianCRUD
            lib_crud = LibrarianCRUD(crud.db)
            librarian = await lib_crud.get_by_user_id(current_user.id)
            if librarian:
                received_by = librarian.id
        _, _ = await crud.pay_fine(
            fine_id, data.payment_method, data.transaction_id, received_by
        )
        return MessageResponse(message="Fine paid successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
