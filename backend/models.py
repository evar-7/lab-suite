from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class DarkmodeState(Base):
    __tablename__ = "darkmode_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(300), nullable=False, unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin: Mapped[Optional[str]] = mapped_column(String(300), nullable=True, index=True)
    extension_version: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    anonymous_user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class FeedbackRequest(BaseModel):
    feedback_type: str = Field(..., pattern="^(like|dislike)$")
    comment: Optional[str] = Field(default=None, max_length=500)
    origin: Optional[str] = Field(default=None, max_length=300)
    extension_version: Optional[str] = Field(default=None, max_length=40)
    anonymous_user_id: str = Field(..., min_length=8, max_length=128)
    timestamp: Optional[str] = None


class DarkmodeStateRequest(BaseModel):
    origin: str = Field(..., min_length=4, max_length=300)
    enabled: bool


def parse_event_time(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)

    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="timestamp invalido") from exc

