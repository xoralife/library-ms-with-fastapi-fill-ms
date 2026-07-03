from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.author import AuthorCreate, AuthorUpdate, AuthorResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.authors.crud import AuthorCRUD
from app.core.permissions import require_admin, require_librarian
from app.models.user import User

router = APIRouter(prefix="/authors", tags=["Authors"])


def get_crud(db: AsyncSession = Depends(get_db)) -> AuthorCRUD:
    return AuthorCRUD(db)


@router.post("", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: AuthorCreate,
    _: User = Depends(require_librarian),
    crud: AuthorCRUD = Depends(get_crud),
):
    return await crud.create(data.model_dump())


@router.get("", response_model=PaginatedResponse)
async def list_authors(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    crud: AuthorCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[AuthorResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: str,
    crud: AuthorCRUD = Depends(get_crud),
):
    author = await crud.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return AuthorResponse.model_validate(author)


@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: str,
    data: AuthorUpdate,
    _: User = Depends(require_librarian),
    crud: AuthorCRUD = Depends(get_crud),
):
    author = await crud.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    updated = await crud.update(author, data.model_dump())
    return AuthorResponse.model_validate(updated)


@router.delete("/{author_id}", response_model=MessageResponse)
async def delete_author(
    author_id: str,
    _: User = Depends(require_admin),
    crud: AuthorCRUD = Depends(get_crud),
):
    deleted = await crud.delete(author_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return MessageResponse(message="Author deleted successfully")
