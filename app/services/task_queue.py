import asyncio
import queue
from typing import Dict, Coroutine, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(Enum):
    CREATED = "CREATED"
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELED = "CANCELED"


class Task(BaseModel):
    id: int
    status: TaskStatus = TaskStatus.CREATED
    message: str | None = None
    result: Any | None = None
    func: Any = Field(exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AsyncTaskManager:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.free_ids = queue.Queue()
        self.max_id = -1

    def add_task(self, func: Coroutine):
        task_id = self._generate_task_id()
        self.tasks[task_id] = Task(id=task_id, func=func)

        self.tasks[task_id].status = TaskStatus.IN_QUEUE

        asyncio.create_task(self._process_task(task_id=task_id))

        return self.tasks[task_id]

    def get_task(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id, None)

    def _generate_task_id(self) -> int:
        if self.free_ids.empty():
            self.max_id += 1
            return self.max_id

        return self.free_ids.get()

    async def _free_task_id(self, task_id: int, delay: float):
        await asyncio.sleep(delay)

        if task_id not in self.tasks:
            return

        del self.tasks[task_id]
        self.free_ids.put(task_id)

    async def _process_task(self, task_id):
        task = self.get_task(task_id=task_id)

        if task_id is None:
            return

        task.status = TaskStatus.IN_PROGRESS
        try:
            task.result = await task.func
        except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
            task.status = TaskStatus.CANCELED
            task.message = "Task interrupted by system"
            raise
        except Exception as e:
            task.status = TaskStatus.CANCELED
            task.message = str(e)
        else:
            task.status = TaskStatus.DONE

        asyncio.create_task(self._free_task_id(task_id=task_id, delay=300))


task_manager = AsyncTaskManager()
