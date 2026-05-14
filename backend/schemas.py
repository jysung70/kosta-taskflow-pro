from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models import StatusEnum


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.todo
    due_at: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    due_at: Optional[datetime] = None


class TaskListResponse(BaseModel):
    # description 제외 — 목록 응답 전용
    id: int
    title: str
    status: StatusEnum
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
