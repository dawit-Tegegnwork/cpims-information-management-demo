"""Data quality reporting aggregation."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CaseRecord
from app.schemas import DataQualityReport
from app.services.completeness import REQUIRED_FIELDS, RECOMMENDED_FIELDS, assess_completeness
from app.services.duplicates import find_duplicate_candidates


def generate_data_quality_report(db: Session) -> DataQualityReport:
    records = db.query(CaseRecord).all()
    total = len(records)

    complete = 0
    scores: list[float] = []
    field_null_counts = {f: 0 for f in REQUIRED_FIELDS + RECOMMENDED_FIELDS}

    for record in records:
        score, _ = assess_completeness(record)
        scores.append(score)
        if score >= 80:
            complete += 1
        for field in field_null_counts:
            value = getattr(record, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                field_null_counts[field] += 1

    status_breakdown: dict[str, int] = {}
    for record in records:
        key = record.status.value if hasattr(record.status, "value") else str(record.status)
        status_breakdown[key] = status_breakdown.get(key, 0) + 1

    null_rates = {
        field: round(count / total, 3) if total else 0.0
        for field, count in field_null_counts.items()
    }

    duplicates = find_duplicate_candidates(db)

    return DataQualityReport(
        generated_at=datetime.utcnow(),
        total_cases=total,
        complete_cases=complete,
        incomplete_cases=total - complete,
        duplicate_candidates=len(duplicates),
        status_breakdown=status_breakdown,
        field_null_rates=null_rates,
        completeness_average=round(sum(scores) / len(scores), 1) if scores else 0.0,
    )
