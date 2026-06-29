from datetime import date

from app.models import CaseRecord, CaseStatus
from app.services.duplicates import find_duplicate_candidates


def test_finds_name_and_dob_duplicate(db_session):
    a = CaseRecord(
        case_number="DUP-A",
        child_first_name="Alex",
        child_last_name="Rivera",
        child_date_of_birth=date(2016, 3, 14),
        county="Oakridge",
        status=CaseStatus.DRAFT,
    )
    b = CaseRecord(
        case_number="DUP-B",
        child_first_name="Alex",
        child_last_name="Rivera",
        child_date_of_birth=date(2016, 3, 14),
        county="Oakridge",
        status=CaseStatus.DRAFT,
    )
    db_session.add_all([a, b])
    db_session.commit()

    candidates = find_duplicate_candidates(db_session)
    assert len(candidates) >= 1
    assert candidates[0].confidence == "high"


def test_duplicates_api(client):
    for i, suffix in enumerate(["X", "Y"]):
        client.post(
            "/api/v1/cases",
            json={
                "case_number": f"DAPI-{suffix}",
                "child_first_name": "Sam",
                "child_last_name": "Match",
                "child_date_of_birth": "2018-01-01",
                "county": "Test",
            },
        )
    response = client.get("/api/v1/duplicates")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
