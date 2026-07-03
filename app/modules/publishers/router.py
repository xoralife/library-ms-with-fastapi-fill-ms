from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.publisher import PublisherCreate, PublisherUpdate, PublisherResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.publishers.crud import PublisherCRUD
from app.core.permissions import require_admin, require_librarian
from app.models.user import User

router = APIRouter(prefix="/publishers", tags=["Publishers"])


def get_crud(db: AsyncSession = Depends(get_db)) -> PublisherCRUD:
    return PublisherCRUD(db)


@router.post("", response_model=PublisherResponse, status_code=status.HTTP_201_CREATED)
async def create_publisher(
    data: PublisherCreate,
    _: User = Depends(require_librarian),
    crud: PublisherCRUD = Depends(get_crud),
):
    return await crud.create(data.model_dump())


@router.get("", response_model=PaginatedResponse)
async def list_publishers(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    crud: PublisherCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[PublisherResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{publisher_id}", response_model=PublisherResponse)
async def get_publisher(
    publisher_id: str,
    crud: PublisherCRUD = Depends(get_crud),
):
    publisher = await crud.get_by_id(publisher_id)
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    return PublisherResponse.model_validate(publisher)


@router.put("/{publisher_id}", response_model=PublisherResponse)
async def update_publisher(
    publisher_id: str,
    data: PublisherUpdate,
    _: User = Depends(require_librarian),
    crud: PublisherCRUD = Depends(get_crud),
):
    publisher = await crud.get_by_id(publisher_id)
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    updated = await crud.update(publisher, data.model_dump())
    return PublisherResponse.model_validate(updated)


@router.delete("/{publisher_id}", response_model=MessageResponse)
async def delete_publisher(
    publisher_id: str,
    _: User = Depends(require_admin),
    crud: PublisherCRUD = Depends(get_crud),
):
    deleted = await crud.delete(publisher_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
    return MessageResponse(message="Publisher deleted successfully")
