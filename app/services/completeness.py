"""Completeness scoring for case registration records."""

REQUIRED_FIELDS = [
    "child_first_name",
    "child_last_name",
    "child_date_of_birth",
    "guardian_name",
    "guardian_phone",
    "referral_source",
    "county",
    "assigned_worker",
    "intake_date",
]

RECOMMENDED_FIELDS = [
    "guardian_email",
    "notes",
]


def _field_value(record: object, field: str) -> object:
    return getattr(record, field, None)


def assess_completeness(record: object) -> tuple[float, list[str]]:
    """Return completeness score (0–100) and list of missing required fields."""
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = _field_value(record, field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    required_score = (len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS) * 80

    recommended_present = sum(
        1
        for field in RECOMMENDED_FIELDS
        if _field_value(record, field) not in (None, "")
    )
    recommended_score = recommended_present / len(RECOMMENDED_FIELDS) * 20

    score = round(required_score + recommended_score, 1)
    return score, missing


def is_registration_complete(record: object) -> bool:
    score, missing = assess_completeness(record)
    return len(missing) == 0 and score >= 80
