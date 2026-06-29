from datetime import date

from app.models import CaseRecord, CaseStatus
from app.services.completeness import assess_completeness, is_registration_complete


def test_complete_record_scores_high():
    record = CaseRecord(
        case_number="C-1",
        child_first_name="Alex",
        child_last_name="Demo",
        child_date_of_birth=date(2016, 1, 1),
        guardian_name="Guardian",
        guardian_phone="555-0000",
        referral_source="School",
        county="Demo",
        assigned_worker="Worker",
        status=CaseStatus.REGISTERED,
        intake_date=date(2024, 1, 1),
        guardian_email="g@example.com",
        notes="Complete",
    )
    score, missing = assess_completeness(record)
    assert score == 100.0
    assert missing == []
    assert is_registration_complete(record)


def test_incomplete_record_lists_missing():
    record = CaseRecord(
        case_number="C-2",
        child_first_name="Alex",
        child_last_name="Demo",
        status=CaseStatus.DRAFT,
    )
    score, missing = assess_completeness(record)
    assert score < 80
    assert "guardian_name" in missing
    assert "child_date_of_birth" in missing


def test_completeness_api(client):
    payload = {
        "case_number": "COMP-001",
        "child_first_name": "Partial",
        "child_last_name": "Record",
    }
    case_id = client.post("/api/v1/cases", json=payload).json()["id"]
    response = client.get(f"/api/v1/cases/{case_id}/completeness")
    assert response.status_code == 200
    body = response.json()
    assert body["is_complete"] is False
    assert len(body["missing_fields"]) > 0
