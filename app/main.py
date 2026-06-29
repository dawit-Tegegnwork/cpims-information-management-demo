from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import CaseRecord, CaseStatus
from app.routes import router


def seed_synthetic_data() -> None:
    db = SessionLocal()
    try:
        if db.query(CaseRecord).count() > 0:
            return
        samples = [
            CaseRecord(
                case_number="DEMO-2024-001",
                child_first_name="Alex",
                child_last_name="Rivera",
                child_date_of_birth=date(2016, 3, 14),
                guardian_name="Maria Rivera",
                guardian_phone="555-0101",
                guardian_email="maria.rivera@example.com",
                referral_source="School counselor",
                county="Oakridge",
                assigned_worker="Jordan Lee",
                status=CaseStatus.ACTIVE,
                intake_date=date(2024, 1, 8),
                notes="Synthetic demo case — reunification plan in progress.",
            ),
            CaseRecord(
                case_number="DEMO-2024-002",
                child_first_name="Alex",
                child_last_name="Rivera",
                child_date_of_birth=date(2016, 3, 14),
                guardian_name="M. Rivera",
                guardian_phone="555-0101",
                referral_source="Hotline",
                county="Oakridge",
                assigned_worker=None,
                status=CaseStatus.DRAFT,
                intake_date=date(2024, 2, 1),
                notes="Potential duplicate intake — pending review.",
            ),
            CaseRecord(
                case_number="DEMO-2024-003",
                child_first_name="Sam",
                child_last_name="Chen",
                child_date_of_birth=date(2019, 7, 22),
                guardian_name="Pat Chen",
                guardian_phone="555-0202",
                referral_source="Pediatric clinic",
                county="Maple",
                assigned_worker="Taylor Brooks",
                status=CaseStatus.UNDER_REVIEW,
                intake_date=date(2024, 3, 15),
            ),
            CaseRecord(
                case_number="DEMO-2024-004",
                child_first_name="Jordan",
                child_last_name="Nguyen",
                child_date_of_birth=None,
                guardian_name=None,
                guardian_phone=None,
                referral_source="Community partner",
                county="Pine",
                assigned_worker=None,
                status=CaseStatus.DRAFT,
                intake_date=None,
                notes="Incomplete registration — missing guardian and DOB.",
            ),
        ]
        db.add_all(samples)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_synthetic_data()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Portfolio demonstration of child protection information management concepts. "
        "All records are synthetic and for educational purposes only."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
