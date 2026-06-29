import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"
    REGISTERED = "registered"
    UNDER_REVIEW = "under_review"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseRecord(Base):
    __tablename__ = "case_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    child_first_name: Mapped[str] = mapped_column(String(100))
    child_last_name: Mapped[str] = mapped_column(String(100))
    child_date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    guardian_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    guardian_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    referral_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_worker: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), default=CaseStatus.DRAFT, index=True
    )
    intake_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
