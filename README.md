# CPIMS Information Management Demo

A portfolio-quality demonstration of **Child Protection Information Management System (CPIMS)** concepts: case registration, data completeness scoring, duplicate detection, status tracking, CSV import/export, and data quality reporting.

[![Tests](https://github.com/dawit-Tegegnwork/cpims-information-management-demo/actions/workflows/test.yml/badge.svg)](https://github.com/dawit-Tegegnwork/cpims-information-management-demo/actions/workflows/test.yml)

**Requirements:** Python 3.12+

## Demo scenario (3–5 minutes)

1. `uvicorn app.main:app --reload` or `docker compose up --build`
2. Open http://127.0.0.1:8000/dashboard — case list + completeness
3. `GET /api/v1/reports/data-quality` — duplicate and completeness metrics
4. `GET /api/v1/duplicates` — review duplicate candidates

## Screenshot

![OpenAPI docs](docs/screenshots/swagger.png)

> **Important:** All data in this repository is **synthetic**. No real individuals, cases, or employer systems are represented. This project is designed for recruiters and hiring managers to evaluate information management and data quality engineering skills.

## Highlights

| Capability | Description |
|------------|-------------|
| Case registration | REST API for creating and updating synthetic case records |
| Completeness checks | Weighted scoring against required and recommended fields |
| Duplicate detection | Conceptual fuzzy matching on name, DOB, and county |
| Status tracking | Lifecycle states from draft through archived |
| CSV import/export | Bulk data exchange for reporting pipelines |
| Data quality CLI | Command-line report generation (text or JSON) |
| Documentation | User guide, data protection, quality rules, reporting |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API explorer. Four synthetic cases are seeded on first startup.

### CLI data quality report

```bash
python -m app.cli report
python -m app.cli report --format json -o report.json
python -m app.cli export -o cases_export.csv
```

### Run tests

```bash
pytest -v
```

## Architecture

```
app/
├── main.py          # FastAPI application + synthetic seed data
├── routes.py        # REST endpoints
├── crud.py          # Database operations + CSV I/O
├── models.py        # SQLAlchemy case record model
├── schemas.py       # Pydantic request/response models
├── cli.py           # Data quality report CLI
└── services/
    ├── completeness.py   # Field-level scoring rules
    ├── duplicates.py     # Duplicate candidate detection
    └── data_quality.py   # Aggregated quality report
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CPIMS_DATABASE_URL` | `sqlite:///./cpims_demo.db` | SQLAlchemy connection string |
| `CPIMS_DEBUG` | `false` | Enable debug mode |

PostgreSQL is supported by setting `CPIMS_DATABASE_URL=postgresql://user:pass@host/db`.

## Docker (optional)

```bash
docker compose up --build
```

## Documentation

- [User Guide](docs/user-guide.md) — day-to-day workflows for case workers
- [Data Quality Rules](docs/data-quality-rules.md) — completeness and validation logic
- [Data Protection](docs/data-protection.md) — privacy and synthetic-data policy
- [Reporting](docs/reporting.md) — exports, CLI reports, and integration patterns

## Sample API flows

**Register a case**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "DEMO-2025-010",
    "child_first_name": "Taylor",
    "child_last_name": "Morgan",
    "county": "Riverview"
  }'
```

**Check completeness**

```bash
curl http://127.0.0.1:8000/api/v1/cases/1/completeness
```

**List duplicate candidates**

```bash
curl http://127.0.0.1:8000/api/v1/duplicates
```

## License

MIT — portfolio demonstration project.
