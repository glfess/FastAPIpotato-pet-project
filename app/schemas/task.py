from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    class Config:
        arbitrary_types_allowed = True

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool
    created_at: datetime
    description: str | None

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., max_length=255)
    is_completed: Optional[bool] = False
