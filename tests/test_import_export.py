def test_csv_export_import_roundtrip(client):
    client.post(
        "/api/v1/cases",
        json={
            "case_number": "CSV-001",
            "child_first_name": "Export",
            "child_last_name": "Test",
            "county": "Demo",
        },
    )
    export = client.get("/api/v1/export/csv")
    assert export.status_code == 200
    assert "CSV-001" in export.text

    csv_body = (
        "case_number,child_first_name,child_last_name,child_date_of_birth,"
        "guardian_name,guardian_phone,guardian_email,referral_source,county,"
        "assigned_worker,status,intake_date,notes\n"
        "CSV-002,Import,User,,,,,,Demo,,draft,,\n"
    )
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("import.csv", csv_body, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["created"] == 1

    listed = client.get("/api/v1/cases")
    numbers = [c["case_number"] for c in listed.json()]
    assert "CSV-002" in numbers


def test_data_quality_report(client):
    response = client.get("/api/v1/reports/data-quality")
    assert response.status_code == 200
    body = response.json()
    assert "total_cases" in body
    assert "completeness_average" in body
