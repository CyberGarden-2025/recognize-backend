import io
import uuid
import asyncio
from pathlib import Path

from fastapi import status, HTTPException, APIRouter, File, UploadFile, Depends
from PIL import Image

from app.services.llm_garbage_classifier import garbage_classifier
from app.services.task_queue import task_manager, Task
from app.services.s3_client import s3_client
from app.services.database import get_async_session, AsyncSession
from app.services.qr_code import scan_codes
from app.api.schemas.recognize import RecognizeResponce
from app.models.packaging_record import PackagingRecord
from app.schemas.gatbage import GarbageData
from app.settings import SETTINGS

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/recognize", tags=["Recognize"])


@router.post("/")
async def add_recognize_task(
    file: UploadFile = File(..., description="Изображение для распознавания"),
    session: AsyncSession = Depends(get_async_session),
) -> RecognizeResponce:
    contents = io.BytesIO(await file.read())

    # Проверка на размер
    if len(contents.getvalue()) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    # Проверка на корректность фото
    try:
        image = Image.open(contents)
        image.verify()
    except Exception as img_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректный файл изображения: {str(img_error)}",
        )

    image_data = contents.getvalue()

    # Сохранение фото в S3
    ext = Path(file.filename).suffix
    asyncio.create_task(
        s3_client.upload_bytes(
            data=image_data,
            bucket_name=SETTINGS.S3_BUCKET_NAME,
            object_name=f"{uuid.uuid4().hex}{ext}",
        )
    )

    qr_codes = scan_codes(contents)
    packaging_records: list[list[GarbageData]] = []
    for code in qr_codes:
        record = await PackagingRecord.get(code=code.data, session=session)
        if record and record.items:
            packaging_records.append(record.get_items())

    if not packaging_records:
        # Задача на обработку фото без известных qr кодов
        task = task_manager.add_task(garbage_classifier.classify(image_data))
    else:
        # Задача на обработку фото с известными qr кодами
        task = task_manager.add_task(
            garbage_classifier.classify_with_advice(image_data, packaging_records)
        )

    return RecognizeResponce(task_id=task.id)


@router.get("/{task_id}")
async def get_by_task_id(task_id: int) -> Task | None:
    return task_manager.get_task(task_id)
