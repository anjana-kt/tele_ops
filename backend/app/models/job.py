
from datetime import datetime, timezone
from enum import Enum as JobEnum

from sqlalchemy import DateTime, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class JobStates(str, JobEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobModel(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index("ix_jobs_device_state", "device_id", "state"),
    )

    job_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    device_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    state: Mapped[JobStates] = mapped_column(
        Enum(JobStates, native_enum=False, length=20),
        nullable=False,
        default=JobStates.QUEUED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
