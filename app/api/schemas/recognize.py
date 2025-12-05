from app.services.classify_garbage import GarbageCategory
from pydantic import BaseModel


class RecognizeResponce(BaseModel):
    category: GarbageCategory
    task_id: int
