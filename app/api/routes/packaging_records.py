from fastapi import APIRouter, Depends

from app.api.schemas.packaging import (
    PackagingRecordCreate,
    PackagingRecordRead,
    PackagingRecordUpdate,
)
from app.api.schemas.response import ListResponse, MetaModel
from app.models.packaging_record import PackagingRecord
from app.services.database import get_async_session, AsyncSession
from app.settings import SETTINGS

router = APIRouter(prefix="/packagings", tags=["Packagings"])


@router.post("/")
async def add_packaging(
    data: PackagingRecordCreate,
    session: AsyncSession = Depends(get_async_session),
) -> PackagingRecordRead:
    record = PackagingRecord(
        code=data.code,
        source=data.source,
    )
    record.set_items(data.items)

    session.add(record)
    await session.commit()
    await session.refresh(record)

    return record


@router.get("/{code}")
async def get_packaging(
    code: str,
    session: AsyncSession = Depends(get_async_session),
) -> PackagingRecordRead | None:
    return await PackagingRecord.get(code, session)


@router.put("/")
async def update_packaging(
    data: PackagingRecordUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> PackagingRecordRead | None:
    record = await PackagingRecord.update(**data.model_dump(), session=session)
    return record


@router.get("/")
async def get_packagings(
    page: int = 1,
    limit: int = 10,
    session: AsyncSession = Depends(get_async_session),
) -> ListResponse[PackagingRecordRead]:
    offset = (page - 1) * limit

    packagings: list[PackagingRecord] = await PackagingRecord.get_many(
        offset=offset, limit=limit, session=session
    )

    total = await PackagingRecord.count(session)

    result: list = []
    for packaging in packagings:
        result.append(
            PackagingRecordRead(
                code=packaging.code,
                source=packaging.source,
                updated_at=packaging.updated_at,
                items=packaging.get_items(),
            )
        )

    return ListResponse[PackagingRecordRead](
        data=result,
        meta=MetaModel(offset=offset, limit=limit, returned=len(result), total=total),
    )
