# User Guide

A practical guide for using the CPIMS Information Management Demo API and CLI.

## Audience

This guide is written for **case workers**, **data quality analysts**, and **technical reviewers** evaluating the portfolio project. All examples use synthetic data.

## Getting started

1. Start the API server (see [README](../README.md))
2. Open the Swagger UI at `/docs`
3. Review seeded cases via `GET /api/v1/cases`

## Registering a new case

### Minimum required for creation

Only `case_number`, `child_first_name`, and `child_last_name` are required at creation. Additional fields can be added later via `PATCH`.

### Recommended workflow

1. **Create draft** — capture initial referral information
2. **Complete required fields** — guardian, DOB, county, worker assignment
3. **Run completeness check** — `GET /api/v1/cases/{id}/completeness`
4. **Promote status** — `PATCH /api/v1/cases/{id}/status?status=registered`
5. **Activate case** — move to `active` when services begin

### Status lifecycle

```
draft → registered → under_review → active → closed → archived
```

| Status | When to use |
|--------|-------------|
| `draft` | Initial intake, missing key fields |
| `registered` | Minimum data captured, pending assignment |
| `under_review` | Supervisor or QA review in progress |
| `active` | Services and documentation ongoing |
| `closed` | Case objectives met |
| `archived` | Retained for reporting, no active work |

## Checking data completeness

Before closing an intake task, verify completeness:

```bash
curl http://127.0.0.1:8000/api/v1/cases/4/completeness
```

Response fields:

- `completeness_score` — 0–100 weighted score
- `missing_fields` — list of required fields still empty
- `is_complete` — boolean against the 80% threshold

Address every field in `missing_fields` before promoting to `registered`.

## Reviewing duplicate candidates

After bulk imports or high-volume intake days:

```bash
curl http://127.0.0.1:8000/api/v1/duplicates
```

For each candidate:

1. Open both cases side by side
2. Confirm whether they represent the same child
3. If duplicate: update the secondary record's status to `closed` with a note referencing the primary case number
4. If not duplicate: add a note explaining the distinction (e.g., siblings, common name)

## CSV import and export

### Export all cases

```bash
curl -o cases.csv http://127.0.0.1:8000/api/v1/export/csv
```

Or use the CLI:

```bash
python -m app.cli export -o cases_export.csv
```

### Import new cases

Prepare a CSV with headers matching the export format. Upload via Swagger (`POST /api/v1/import/csv`) or:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/import/csv \
  -F "file=@new_cases.csv"
```

Review the response `errors` array for skipped rows.

## Generating data quality reports

### API

```bash
curl http://127.0.0.1:8000/api/v1/reports/data-quality
```

### CLI

```bash
python -m app.cli report
python -m app.cli report --format json -o weekly_dq.json
```

Share reports with supervisors to prioritize incomplete registrations and duplicate reviews.

## Tips for portfolio reviewers

When demonstrating this project:

1. Show the seeded duplicate pair (DEMO-2024-001 and DEMO-2024-002)
2. Walk through completeness on DEMO-2024-004 (incomplete draft)
3. Export CSV, modify a row, re-import
4. Run the CLI report and explain null rate metrics

## Support

This is a self-contained demo. For questions about the implementation, see the source code under `app/services/` and the [Data Quality Rules](data-quality-rules.md) document.
