from datetime import date


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_get_case(client):
    payload = {
        "case_number": "TEST-001",
        "child_first_name": "Casey",
        "child_last_name": "Demo",
        "child_date_of_birth": "2015-06-01",
        "guardian_name": "Jamie Demo",
        "guardian_phone": "555-9999",
        "referral_source": "Hotline",
        "county": "Demo County",
        "assigned_worker": "Worker A",
        "status": "registered",
        "intake_date": "2024-05-01",
    }
    create = client.post("/api/v1/cases", json=payload)
    assert create.status_code == 201
    case_id = create.json()["id"]

    get = client.get(f"/api/v1/cases/{case_id}")
    assert get.status_code == 200
    assert get.json()["case_number"] == "TEST-001"


def test_duplicate_case_number_rejected(client):
    payload = {
        "case_number": "TEST-DUP",
        "child_first_name": "A",
        "child_last_name": "B",
    }
    assert client.post("/api/v1/cases", json=payload).status_code == 201
    assert client.post("/api/v1/cases", json=payload).status_code == 409


def test_status_update(client):
    payload = {
        "case_number": "TEST-STATUS",
        "child_first_name": "Riley",
        "child_last_name": "Test",
    }
    case_id = client.post("/api/v1/cases", json=payload).json()["id"]
    response = client.patch(f"/api/v1/cases/{case_id}/status?status=active")
    assert response.status_code == 200
    assert response.json()["status"] == "active"
