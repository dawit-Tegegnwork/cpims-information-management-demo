import csv
import io
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CaseRecord, CaseStatus
from app.schemas import CaseRecordCreate, CaseRecordUpdate


def get_case(db: Session, case_id: int) -> CaseRecord | None:
    return db.query(CaseRecord).filter(CaseRecord.id == case_id).first()


def get_case_by_number(db: Session, case_number: str) -> CaseRecord | None:
    return db.query(CaseRecord).filter(CaseRecord.case_number == case_number).first()


def list_cases(
    db: Session,
    *,
    status: CaseStatus | None = None,
    county: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[CaseRecord]:
    query = db.query(CaseRecord)
    if status:
        query = query.filter(CaseRecord.status == status)
    if county:
        query = query.filter(CaseRecord.county.ilike(f"%{county}%"))
    return query.order_by(CaseRecord.id).offset(skip).limit(limit).all()


def create_case(db: Session, payload: CaseRecordCreate) -> CaseRecord:
    record = CaseRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_case(db: Session, record: CaseRecord, payload: CaseRecordUpdate) -> CaseRecord:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


ALLOWED_STATUS_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.DRAFT: {CaseStatus.REGISTERED, CaseStatus.ARCHIVED},
    CaseStatus.REGISTERED: {CaseStatus.UNDER_REVIEW, CaseStatus.ACTIVE, CaseStatus.ARCHIVED},
    CaseStatus.UNDER_REVIEW: {CaseStatus.ACTIVE, CaseStatus.CLOSED, CaseStatus.ARCHIVED},
    CaseStatus.ACTIVE: {CaseStatus.CLOSED, CaseStatus.ARCHIVED},
    CaseStatus.CLOSED: {CaseStatus.ARCHIVED},
    CaseStatus.ARCHIVED: set(),
}


def update_status(db: Session, record: CaseRecord, status: CaseStatus) -> CaseRecord:
    allowed = ALLOWED_STATUS_TRANSITIONS.get(record.status, set())
    if status not in allowed and status != record.status:
        raise ValueError(f"Cannot transition from {record.status.value} to {status.value}")
    record.status = status
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


CSV_COLUMNS = [
    "case_number",
    "child_first_name",
    "child_last_name",
    "child_date_of_birth",
    "guardian_name",
    "guardian_phone",
    "guardian_email",
    "referral_source",
    "county",
    "assigned_worker",
    "status",
    "intake_date",
    "notes",
]


def export_cases_csv(db: Session) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for record in db.query(CaseRecord).order_by(CaseRecord.id):
        writer.writerow(
            {
                "case_number": record.case_number,
                "child_first_name": record.child_first_name,
                "child_last_name": record.child_last_name,
                "child_date_of_birth": record.child_date_of_birth.isoformat()
                if record.child_date_of_birth
                else "",
                "guardian_name": record.guardian_name or "",
                "guardian_phone": record.guardian_phone or "",
                "guardian_email": record.guardian_email or "",
                "referral_source": record.referral_source or "",
                "county": record.county or "",
                "assigned_worker": record.assigned_worker or "",
                "status": record.status.value,
                "intake_date": record.intake_date.isoformat() if record.intake_date else "",
                "notes": record.notes or "",
            }
        )
    return output.getvalue()


def import_cases_csv(db: Session, csv_content: str) -> tuple[int, list[str]]:
    reader = csv.DictReader(io.StringIO(csv_content))
    created = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        case_number = (row.get("case_number") or "").strip()
        if not case_number:
            errors.append(f"Row {row_num}: missing case_number")
            continue
        if get_case_by_number(db, case_number):
            errors.append(f"Row {row_num}: duplicate case_number {case_number}")
            continue

        try:
            status_raw = (row.get("status") or "draft").strip().lower()
            status = CaseStatus(status_raw)
        except ValueError:
            errors.append(f"Row {row_num}: invalid status '{row.get('status')}'")
            continue

        def parse_date(value: str | None):
            if not value or not value.strip():
                return None
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()

        payload = CaseRecordCreate(
            case_number=case_number,
            child_first_name=row["child_first_name"].strip(),
            child_last_name=row["child_last_name"].strip(),
            child_date_of_birth=parse_date(row.get("child_date_of_birth")),
            guardian_name=(row.get("guardian_name") or "").strip() or None,
            guardian_phone=(row.get("guardian_phone") or "").strip() or None,
            guardian_email=(row.get("guardian_email") or "").strip() or None,
            referral_source=(row.get("referral_source") or "").strip() or None,
            county=(row.get("county") or "").strip() or None,
            assigned_worker=(row.get("assigned_worker") or "").strip() or None,
            status=status,
            intake_date=parse_date(row.get("intake_date")),
            notes=(row.get("notes") or "").strip() or None,
        )
        create_case(db, payload)
        created += 1

    return created, errors
