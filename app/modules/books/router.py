import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.schemas.common import MessageResponse
from app.modules.books.crud import BookCRUD
from app.utils.csv_handler import parse_csv_to_books, generate_csv_headers
from app.core.permissions import require_admin, require_librarian
from app.models.user import User, UserRole

router = APIRouter(prefix="/books", tags=["Books"])


def get_crud(db: AsyncSession = Depends(get_db)) -> BookCRUD:
    return BookCRUD(db)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    _: User = Depends(require_librarian),
    crud: BookCRUD = Depends(get_crud),
):
    existing = await crud.get_by_isbn(data.isbn)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN already exists")
    book = await crud.create(data.model_dump())
    return BookResponse.model_validate(book)


@router.get("", response_model=BookListResponse)
async def list_books(
    search: str = Query(None),
    category_id: str = Query(None),
    author_id: str = Query(None),
    language: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    crud: BookCRUD = Depends(get_crud),
):
    items, total = await crud.get_all(
        search=search,
        category_id=category_id,
        author_id=author_id,
        language=language,
        page=page,
        page_size=page_size,
    )
    return BookListResponse(
        items=[BookResponse.model_validate(b) for b in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    crud: BookCRUD = Depends(get_crud),
):
    book = await crud.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return BookResponse.model_validate(book)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    data: BookUpdate,
    _: User = Depends(require_librarian),
    crud: BookCRUD = Depends(get_crud),
):
    book = await crud.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update(book, update_data)
    return BookResponse.model_validate(updated)


@router.delete("/{book_id}", response_model=MessageResponse)
async def delete_book(
    book_id: str,
    _: User = Depends(require_admin),
    crud: BookCRUD = Depends(get_crud),
):
    deleted = await crud.delete(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return MessageResponse(message="Book deleted successfully")


@router.post("/import-csv", response_model=MessageResponse)
async def import_books_csv(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    crud: BookCRUD = Depends(get_crud),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
    content = await file.read()
    decoded = content.decode("utf-8-sig")
    books_data, errors = await parse_csv_to_books(decoded)
    if errors:
        return MessageResponse(message=f"Import completed with errors: {'; '.join(errors[:5])}")
    await crud.bulk_create(books_data)
    return MessageResponse(message=f"Successfully imported {len(books_data)} books")


@router.get("/export/csv")
async def export_books_csv(
    crud: BookCRUD = Depends(get_crud),
    _: User = Depends(require_librarian),
):
    items, _ = await crud.get_all(page=1, page_size=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(generate_csv_headers())
    for book in items:
        writer.writerow([
            book.title, book.isbn, book.author_id or "", book.publisher_id or "",
            book.category_id or "", book.language, book.edition or "",
            book.publish_year or "", book.page_count or "",
            book.shelf_location or "", book.total_copies, book.description or "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_export.csv"},
    )
