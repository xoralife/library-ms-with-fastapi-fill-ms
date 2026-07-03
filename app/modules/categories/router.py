from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.modules.categories.crud import CategoryCRUD
from app.core.permissions import require_admin, require_librarian
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_crud(db: AsyncSession = Depends(get_db)) -> CategoryCRUD:
    return CategoryCRUD(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    _: User = Depends(require_librarian),
    crud: CategoryCRUD = Depends(get_crud),
):
    return await crud.create(data.model_dump())


@router.get("", response_model=PaginatedResponse)
async def list_categories(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    crud: CategoryCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(search=search, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[CategoryResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    crud: CategoryCRUD = Depends(get_crud),
):
    category = await crud.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    _: User = Depends(require_librarian),
    crud: CategoryCRUD = Depends(get_crud),
):
    category = await crud.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    updated = await crud.update(category, data.model_dump())
    return CategoryResponse.model_validate(updated)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: str,
    _: User = Depends(require_admin),
    crud: CategoryCRUD = Depends(get_crud),
):
    book_count = await crud.count_books(category_id)
    if book_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {book_count} book(s) assigned",
        )
    deleted = await crud.delete(category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return MessageResponse(message="Category deleted successfully")
