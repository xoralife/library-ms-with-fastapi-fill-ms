import csv
import io
from typing import Optional
from pydantic import ValidationError
from app.schemas.book import BookCreate


async def parse_csv_to_books(file_content: str) -> tuple[list[dict], list[str]]:
    reader = csv.DictReader(io.StringIO(file_content))
    books_data = []
    errors = []
    row_num = 1
    for row in reader:
        row_num += 1
        try:
            book_data = {
                "title": row.get("title", "").strip(),
                "isbn": row.get("isbn", "").strip(),
                "author_id": row.get("author_id", "").strip() or None,
                "publisher_id": row.get("publisher_id", "").strip() or None,
                "category_id": row.get("category_id", "").strip() or None,
                "language": row.get("language", "English").strip(),
                "edition": row.get("edition", "").strip() or None,
                "publish_year": int(row["publish_year"]) if row.get("publish_year", "").strip() else None,
                "page_count": int(row["page_count"]) if row.get("page_count", "").strip() else None,
                "shelf_location": row.get("shelf_location", "").strip() or None,
                "total_copies": int(row.get("total_copies", "1").strip()),
                "description": row.get("description", "").strip() or None,
            }
            BookCreate(**book_data)
            books_data.append(book_data)
        except (ValidationError, ValueError, KeyError) as e:
            errors.append(f"Row {row_num}: {str(e)}")
    return books_data, errors


def generate_csv_headers() -> list[str]:
    return [
        "title", "isbn", "author_id", "publisher_id", "category_id",
        "language", "edition", "publish_year", "page_count",
        "shelf_location", "total_copies", "description",
    ]
