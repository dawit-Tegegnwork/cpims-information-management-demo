# Data Quality Rules

This document defines the completeness scoring, validation, and duplicate detection rules implemented in the CPIMS demo.

## Completeness scoring

Each case record receives a score from **0 to 100** based on required and recommended fields.

### Required fields (80% weight)

| Field | Rule |
|-------|------|
| `child_first_name` | Non-empty string |
| `child_last_name` | Non-empty string |
| `child_date_of_birth` | Valid date |
| `guardian_name` | Non-empty string |
| `guardian_phone` | Non-empty string |
| `referral_source` | Non-empty string |
| `county` | Non-empty string |
| `assigned_worker` | Non-empty string |
| `intake_date` | Valid date |

**Required portion score** = `(populated_required / 9) × 80`

### Recommended fields (20% weight)

| Field | Rule |
|-------|------|
| `guardian_email` | Present and non-empty |
| `notes` | Present and non-empty |

**Recommended portion score** = `(populated_recommended / 2) × 20`

### Registration complete threshold

A case is considered **registration complete** when:

- All required fields are populated, **and**
- Total score ≥ **80**

Cases below threshold should remain in `draft` or `under_review` status until corrected.

## Validation rules

| Rule | Enforcement |
|------|-------------|
| Unique case number | API returns HTTP 409 on duplicate `case_number` |
| Valid status enum | Must be one of: draft, registered, under_review, active, closed, archived |
| CSV date format | ISO 8601 (`YYYY-MM-DD`) |
| CSV import duplicates | Skipped with row-level error message |

## Duplicate detection (conceptual)

Duplicate detection is a **candidate surfacing** tool, not an automatic merge. Reviewers must confirm matches before consolidation.

### Matching logic

| Confidence | Criteria |
|------------|----------|
| **High** | Name similarity ≥ 85% **and** identical date of birth |
| **Medium** | Name similarity ≥ 85% **and** same county |
| **Medium** | Name similarity ≥ 95% (near-identical names) |

Name similarity uses normalized lowercase strings and sequence matching.

### Review workflow

1. Run `GET /api/v1/duplicates` or review the data quality report
2. Compare intake dates, referral sources, and guardian contact
3. Mark one record as primary; update or close the duplicate
4. Document the decision in case notes

## Data quality report metrics

The CLI and API report include:

- Total, complete, and incomplete case counts
- Average completeness score
- Duplicate candidate count
- Status breakdown
- Per-field null rates

Use null rate trends to prioritize training or form redesign.

## Example scenarios (synthetic)

| Case | Scenario | Expected outcome |
|------|----------|------------------|
| DEMO-2024-001 | Fully populated active case | Score 100, no duplicates flagged alone |
| DEMO-2024-002 | Same child name/DOB as 001 | High-confidence duplicate candidate |
| DEMO-2024-004 | Missing guardian and DOB | Low score, listed in incomplete count |

## Extending rules

Production CPIMS systems typically add:

- Cross-system identifier matching ( Medicaid ID, school ID )
- Address normalization
- Phonetic name matching
- Supervisor approval before status promotion

This demo intentionally keeps rules transparent and auditable for portfolio review.
