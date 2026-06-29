# Reporting Guide

How to produce and use reports from the CPIMS Information Management Demo.

## Report types

| Report | Endpoint / Command | Format | Primary audience |
|--------|-------------------|--------|------------------|
| Data quality summary | `GET /api/v1/reports/data-quality` | JSON | Analysts, supervisors |
| Data quality CLI | `python -m app.cli report` | Text / JSON | Operations, cron jobs |
| Case export | `GET /api/v1/export/csv` | CSV | BI tools, spreadsheets |
| Duplicate candidates | `GET /api/v1/duplicates` | JSON | Intake QA team |
| Per-case completeness | `GET /api/v1/cases/{id}/completeness` | JSON | Case workers |

## Data quality report fields

```json
{
  "generated_at": "2024-06-15T10:30:00",
  "total_cases": 42,
  "complete_cases": 35,
  "incomplete_cases": 7,
  "duplicate_candidates": 2,
  "status_breakdown": { "active": 20, "draft": 5 },
  "field_null_rates": { "guardian_email": 0.45 },
  "completeness_average": 87.3
}
```

### Interpreting metrics

- **completeness_average** — Overall registry health; target ≥ 90% in production
- **field_null_rates** — Identify fields that need form redesign or training
- **duplicate_candidates** — Queue length for intake QA review
- **status_breakdown** — Workload distribution across lifecycle stages

## Scheduled reporting (example)

Add a cron entry for weekly JSON reports:

```cron
0 6 * * 1 cd /path/to/cpims-information-management-demo && \
  .venv/bin/python -m app.cli report --format json -o reports/weekly_$(date +\%Y-\%m-\%d).json
```

## Integration patterns

### Spreadsheet analysis

1. Export CSV via API or CLI
2. Open in Excel / Google Sheets
3. Pivot on `county`, `status`, and `assigned_worker`

### BI dashboard

Point a BI tool at:

- **Batch:** nightly CSV export to object storage
- **Live:** PostgreSQL read replica (when using `CPIMS_DATABASE_URL`)

Suggested dashboard tiles:

- Cases by status (bar chart)
- Average completeness by county (heatmap)
- Duplicate candidates open > 7 days (table)
- Top 5 fields by null rate (horizontal bar)

### Alerting thresholds (example)

| Metric | Warning | Critical |
|--------|---------|----------|
| Incomplete cases | > 15% of total | > 25% of total |
| Duplicate candidates | > 5 open | > 15 open |
| `child_date_of_birth` null rate | > 10% | > 20% |

Implement alerts in your scheduler or observability stack; this demo provides the metrics source only.

## Sample CLI output

```
CPIMS Data Quality Report
========================================
Generated:     2024-06-15T10:30:00
Total cases:   4
Complete:      2
Incomplete:    2
Duplicates:    1
Avg score:     72.5%

Status breakdown:
  active               1
  draft                2
  under_review         1

Field null rates:
  assigned_worker            25.0%
  child_date_of_birth        25.0%
  ...
```

## Privacy reminder

Reports contain synthetic personal data. Apply the same handling described in [Data Protection](data-protection.md) when storing or sharing exports.
