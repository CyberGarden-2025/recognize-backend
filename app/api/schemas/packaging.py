from datetime import datetime
from pydantic import BaseModel
from app.schemas.gatbage import GarbageData


class PackagingRecordCreate(BaseModel):
    code: str
    items: list[GarbageData]
    source: str


class PackagingRecordRead(BaseModel):
    code: str
    items: list[GarbageData]
    source: str
    updated_at: datetime


class PackagingRecordUpdate(BaseModel):
    code: str
    items: list[GarbageData]
    source: str
