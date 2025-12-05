from pydantic import BaseModel


class RecognizeResponce(BaseModel):
    task_id: int
