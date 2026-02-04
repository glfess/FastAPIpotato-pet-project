from datetime import datetime
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = Column(Integer, primary_key=True)

    title: Mapped[str] = Column(String(255), nullable=False)

    is_completed: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    description: Mapped[str] = Column(String(255), nullable=False)

    is_deleted: Mapped[bool] = mapped_column(server_default="false", nullable=False, default=False)