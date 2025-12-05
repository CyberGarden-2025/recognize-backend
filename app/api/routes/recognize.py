from typing import Optional
import io

from fastapi import status, HTTPException, APIRouter, File, UploadFile
from PIL import Image

from app.services.classify_garbage import classify_garbage, GarbageCategory

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/recognize", tags=["Recognize"])


@router.post("/")
async def recognize(
    file: UploadFile = File(..., description="Изображение для распознавания"),
) -> GarbageCategory:
    content = io.BytesIO(await file.read())

    if len(content.getvalue()) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    try:
        image = Image.open(content)
        image.verify()
    except Exception as img_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректный файл изображения: {str(img_error)}",
        )

    return classify_garbage(content)
