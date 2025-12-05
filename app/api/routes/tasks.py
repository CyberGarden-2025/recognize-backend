from fastapi import APIRouter
from app.services.task_queue import task_manager

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/async/{task_id}")
async def get_by_task_id(task_id: int):
    return task_manager.get_task(task_id)
