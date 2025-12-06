from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, JSON, DateTime, select, func, update
from typing import List

from app.schemas.gatbage import GarbageData


class Base(DeclarativeBase):
    pass


class PackagingRecord(Base):
    __tablename__ = "packaging_records"

    # EAN / QR / product code
    code: Mapped[str] = mapped_column(String, primary_key=True)

    # JSONB: list[GarbageData]
    items: Mapped[list] = mapped_column(JSON, nullable=False)

    # manual / openfoodfacts / ai / mixed
    source: Mapped[str] = mapped_column(String, default="unknown")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get_items(self) -> List[GarbageData]:
        return [GarbageData(**item) for item in self.items]

    def set_items(self, items: List[GarbageData]):
        self.items = [item.model_dump() for item in items]

    @classmethod
    async def get_many(
        cls, session: AsyncSession, offset: int = 0, limit: int = 50
    ) -> list["PackagingRecord"]:
        stmt = select(cls).offset(offset).limit(limit)
        result = await session.execute(stmt)
        items = [row[0] for row in result.fetchall()]

        return items

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        count_stmt = select(func.count()).select_from(PackagingRecord)
        data = await session.execute(count_stmt)
        return data.scalar_one()

    @classmethod
    async def get(cls, code: str, session: AsyncSession):
        return await session.get(PackagingRecord, code)

    @classmethod
    async def update(
        cls,
        code: str,
        items: list[GarbageData],
        source: str,
        session: AsyncSession,
    ):
        stmt = (
            update(PackagingRecord)
            .where(PackagingRecord.code == code)
            .values(source=source, items=items)
            .returning(PackagingRecord)
        )

        result = await session.execute(stmt)
        updated = result.fetchone()

        if not updated:
            return None

        await session.commit()
        return updated[0]
