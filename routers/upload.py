"""
File upload API endpoints.
Handles image and file uploads to cloud storage.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import User
from schemas import UploadResponse
from auth import get_current_user
from storage import storage_service
from config import settings

router = APIRouter(prefix="/upload", tags=["Uploads"])


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an image file.
    Accepts multipart/form-data. Returns the public URL.
    """
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum size of {settings.MAX_IMAGE_SIZE_MB}MB",
        )

    # Upload to storage
    url, _ = await storage_service.upload_file(content, file.filename or "image.jpg", file.content_type)

    return UploadResponse(
        url=url,
        name=file.filename or "image.jpg",
        type="image",
        size_bytes=len(content),
    )


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a general file.
    Accepts multipart/form-data. Returns the public URL.
    """
    # Read file content
    content = await file.read()

    # Validate file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Determine type
    file_type = "image" if file.content_type and file.content_type.startswith("image/") else "file"

    # Upload to storage
    url, _ = await storage_service.upload_file(content, file.filename or "file", file.content_type or "application/octet-stream")

    return UploadResponse(
        url=url,
        name=file.filename or "file",
        type=file_type,
        size_bytes=len(content),
    )
