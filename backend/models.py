import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Enum as SAEnum, DateTime
from database import Base


class StatusEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    # Python 3.14 호환을 위해 Mapped 어노테이션 대신 Column 스타일 사용
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(StatusEnum), default=StatusEnum.todo, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, nullable=False)
