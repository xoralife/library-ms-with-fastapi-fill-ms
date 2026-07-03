import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.config import get_settings

settings = get_settings()
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


async def save_upload(file: UploadFile, subfolder: str = "profiles") -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}",
        )

    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.max_upload_size / 1024 / 1024:.1f}MB limit",
        )

    upload_dir = os.path.join(settings.upload_dir, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return f"/uploads/{subfolder}/{filename}"


async def delete_upload(file_path: str) -> None:
    full_path = os.path.join(settings.upload_dir, file_path.replace("/uploads/", ""))
    if os.path.exists(full_path):
        os.remove(full_path)
