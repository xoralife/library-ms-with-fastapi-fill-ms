from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.reservation import ReserveRequest, ReservationResponse, ReservationListResponse
from app.schemas.common import MessageResponse
from app.modules.reservations.crud import ReservationCRUD
from app.core.permissions import require_admin, require_librarian, get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/reservations", tags=["Reservations"])


def get_crud(db: AsyncSession = Depends(get_db)) -> ReservationCRUD:
    return ReservationCRUD(db)


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def reserve_book(
    data: ReserveRequest,
    current_user: User = Depends(get_current_user),
    crud: ReservationCRUD = Depends(get_crud),
):
    from app.modules.students.crud import StudentCRUD
    student_crud = StudentCRUD(crud.db)
    student = await student_crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile not found")
    reservation = await crud.create(book_id=data.book_id, student_id=student.id, notes=data.notes)
    return ReservationResponse.model_validate(reservation)


@router.get("", response_model=ReservationListResponse)
async def list_reservations(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_librarian),
    crud: ReservationCRUD = Depends(get_crud),
):
    from app.models.reservation import ReservationStatus
    res_status = ReservationStatus(status) if status else None
    items, total = await crud.get_all(status=res_status, page=page, page_size=page_size)
    return ReservationListResponse(
        items=[ReservationResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/my", response_model=list[ReservationResponse])
async def my_reservations(
    current_user: User = Depends(get_current_user),
    crud: ReservationCRUD = Depends(get_crud),
):
    from app.modules.students.crud import StudentCRUD
    student_crud = StudentCRUD(crud.db)
    student = await student_crud.get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    reservations = await crud.get_student_reservations(student.id)
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.delete("/{reservation_id}", response_model=MessageResponse)
async def cancel_reservation(
    reservation_id: str,
    current_user: User = Depends(get_current_user),
    crud: ReservationCRUD = Depends(get_crud),
):
    reservation = await crud.get_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    if current_user.role == UserRole.STUDENT:
        from app.modules.students.crud import StudentCRUD
        student_crud = StudentCRUD(crud.db)
        student = await student_crud.get_by_user_id(current_user.id)
        if not student or student.id != reservation.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your reservation")
    result = await crud.cancel(reservation_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel reservation")
    return MessageResponse(message="Reservation cancelled")


@router.put("/{reservation_id}/approve", response_model=ReservationResponse)
async def approve_reservation(
    reservation_id: str,
    _: User = Depends(require_librarian),
    crud: ReservationCRUD = Depends(get_crud),
):
    reservation = await crud.approve(reservation_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot approve reservation")
    return ReservationResponse.model_validate(reservation)


@router.put("/{reservation_id}/reject", response_model=ReservationResponse)
async def reject_reservation(
    reservation_id: str,
    _: User = Depends(require_librarian),
    crud: ReservationCRUD = Depends(get_crud),
):
    reservation = await crud.reject(reservation_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reject reservation")
    return ReservationResponse.model_validate(reservation)
