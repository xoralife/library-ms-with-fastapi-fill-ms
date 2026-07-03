from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.librarian import LibrarianCreate, LibrarianUpdate, LibrarianResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.librarians.crud import LibrarianCRUD
from app.core.permissions import require_admin
from app.models.user import User

router = APIRouter(prefix="/librarians", tags=["Librarians"])


def get_crud(db: AsyncSession = Depends(get_db)) -> LibrarianCRUD:
    return LibrarianCRUD(db)


@router.post("", response_model=LibrarianResponse, status_code=status.HTTP_201_CREATED)
async def create_librarian(
    data: LibrarianCreate,
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    librarian = await crud.create(data.model_dump())
    return LibrarianResponse.model_validate(librarian)


@router.get("", response_model=PaginatedResponse)
async def list_librarians(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[LibrarianResponse.model_validate(l) for l in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{librarian_id}", response_model=LibrarianResponse)
async def get_librarian(
    librarian_id: str,
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    librarian = await crud.get_by_id(librarian_id)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian not found")
    return LibrarianResponse.model_validate(librarian)


@router.put("/{librarian_id}", response_model=LibrarianResponse)
async def update_librarian(
    librarian_id: str,
    data: LibrarianUpdate,
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    librarian = await crud.get_by_id(librarian_id)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian not found")
    updated = await crud.update(librarian, data.model_dump(exclude_unset=True))
    return LibrarianResponse.model_validate(updated)


@router.delete("/{librarian_id}", response_model=MessageResponse)
async def delete_librarian(
    librarian_id: str,
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    deleted = await crud.delete(librarian_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian not found")
    return MessageResponse(message="Librarian deleted successfully")


@router.put("/{librarian_id}/toggle", response_model=LibrarianResponse)
async def toggle_librarian_active(
    librarian_id: str,
    _: User = Depends(require_admin),
    crud: LibrarianCRUD = Depends(get_crud),
):
    librarian = await crud.toggle_active(librarian_id)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian not found")
    return LibrarianResponse.model_validate(librarian)
