from datetime import datetime, date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


Status = Literal["todo", "doing", "done"]

class TaskCreate(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=120)
    description: str|None = None
    status: Status = "todo"
    priority: int = Field(3, ge=1, le=5)
    due_date: date|None = None

    @field_validator("title")
    @classmethod
    def strip_and_not_blank(cls, v:str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v



class TaskPatch(BaseModel):
    user_id: int|None = None
    title: str|None = None
    description: str|None = None
    status: Status|None = None
    priority: int|None = None
    due_date: date|None = None



class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    description: str | None
    status: Status
    priority: int
    due_date: date | None
    created_at: datetime
    updated_at: datetime


class TaskDelete(BaseModel):
    id : int


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    limit: int
    offset: int