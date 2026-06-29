"""Duplicate detection concept — fuzzy matching on synthetic identifiers."""

from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models import CaseRecord
from app.schemas import DuplicateCandidate


def _normalize_name(first: str, last: str) -> str:
    return f"{first.strip().lower()} {last.strip().lower()}"


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_duplicate_candidates(db: Session, threshold: float = 0.85) -> list[DuplicateCandidate]:
    """Identify potential duplicate registrations using name and DOB proximity."""
    records = db.query(CaseRecord).order_by(CaseRecord.id).all()
    candidates: list[DuplicateCandidate] = []
    seen_pairs: set[tuple[int, int]] = set()

    for i, record in enumerate(records):
        name_a = _normalize_name(record.child_first_name, record.child_last_name)
        for other in records[i + 1 :]:
            pair = (record.id, other.id)
            if pair in seen_pairs:
                continue

            name_b = _normalize_name(other.child_first_name, other.child_last_name)
            name_sim = _similarity(name_a, name_b)

            same_dob = (
                record.child_date_of_birth is not None
                and record.child_date_of_birth == other.child_date_of_birth
            )
            same_county = (
                record.county
                and other.county
                and record.county.lower() == other.county.lower()
            )

            if name_sim >= threshold and same_dob:
                confidence = "high"
                reason = "Matching child name and date of birth"
            elif name_sim >= threshold and same_county:
                confidence = "medium"
                reason = "Similar child name in same county"
            elif name_sim >= 0.95:
                confidence = "medium"
                reason = "Near-identical child name"
            else:
                continue

            seen_pairs.add(pair)
            candidates.append(
                DuplicateCandidate(
                    case_id=record.id,
                    case_number=record.case_number,
                    matched_case_id=other.id,
                    matched_case_number=other.case_number,
                    match_reason=reason,
                    confidence=confidence,
                )
            )

    return candidates
