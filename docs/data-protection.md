# Data Protection & Privacy

This document describes how the CPIMS Information Management Demo handles data responsibly in a portfolio context.

## Synthetic data only

All case records in this application are **fabricated**. Names, phone numbers, email addresses, and counties are invented for demonstration purposes. No real child, guardian, or caseworker identities are used.

On first startup, the application seeds four sample records illustrating common data quality scenarios (complete case, potential duplicate, under review, incomplete draft).

## No production credentials

This repository must never contain:

- Production database connection strings
- API keys or authentication secrets
- Exports from real case management systems
- Screenshots or documents from employer environments

Use `.env` for local overrides and keep it out of version control (see `.gitignore`).

## Data minimization

The demo model collects only fields needed to illustrate CPIMS-style workflows:

- Child identifiers (synthetic name, date of birth)
- Guardian contact (synthetic)
- Referral and assignment metadata
- Case status and intake dates

Sensitive categories (medical details, legal findings, addresses) are intentionally omitted.

## Access control (demo scope)

This portfolio project does **not** implement production-grade authentication. In a real CPIMS deployment you would expect:

| Control | Production expectation |
|---------|------------------------|
| Authentication | SSO / MFA for all users |
| Authorization | Role-based access (intake, supervisor, admin) |
| Audit logging | Immutable log of all record access and changes |
| Encryption | TLS in transit, encryption at rest |
| Retention | Policy-driven archival and secure deletion |

Document these expectations in your organization's security baseline; this demo focuses on data quality mechanics rather than identity management.

## CSV import/export

Exported CSV files may contain synthetic personal data. Treat exports as you would any local dataset:

1. Store in access-controlled directories
2. Delete when no longer needed for testing
3. Do not share exports outside your portfolio review context

## Reporting to third parties

If you deploy this demo publicly, add a banner stating that all data is synthetic and that the system is not connected to any government or agency database.

## Contact

For portfolio review questions, refer to the repository owner listed in the GitHub profile. This project is not affiliated with any government child welfare agency.
