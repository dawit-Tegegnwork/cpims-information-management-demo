#!/usr/bin/env python3
"""CLI for data quality reporting and CSV operations."""

import argparse
import json
import sys
from pathlib import Path

from app.database import SessionLocal, init_db
from app import crud
from app.services.data_quality import generate_data_quality_report


def cmd_report(args: argparse.Namespace) -> int:
    init_db()
    db = SessionLocal()
    try:
        report = generate_data_quality_report(db)
        data = report.model_dump(mode="json")
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print("CPIMS Data Quality Report")
            print("=" * 40)
            print(f"Generated:     {data['generated_at']}")
            print(f"Total cases:   {data['total_cases']}")
            print(f"Complete:      {data['complete_cases']}")
            print(f"Incomplete:    {data['incomplete_cases']}")
            print(f"Duplicates:    {data['duplicate_candidates']}")
            print(f"Avg score:     {data['completeness_average']}%")
            print("\nStatus breakdown:")
            for status, count in sorted(data["status_breakdown"].items()):
                print(f"  {status:20s} {count}")
            print("\nField null rates:")
            for field, rate in sorted(data["field_null_rates"].items(), key=lambda x: -x[1]):
                print(f"  {field:25s} {rate * 100:5.1f}%")
        if args.output:
            Path(args.output).write_text(json.dumps(data, indent=2))
            print(f"\nReport saved to {args.output}", file=sys.stderr)
        return 0
    finally:
        db.close()


def cmd_export(args: argparse.Namespace) -> int:
    init_db()
    db = SessionLocal()
    try:
        csv_data = crud.export_cases_csv(db)
        Path(args.output).write_text(csv_data)
        print(f"Exported cases to {args.output}")
        return 0
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CPIMS demo CLI — data quality and export utilities"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report", help="Generate data quality report")
    report.add_argument("--format", choices=["text", "json"], default="text")
    report.add_argument("-o", "--output", help="Save JSON report to file")
    report.set_defaults(func=cmd_report)

    export = sub.add_parser("export", help="Export cases to CSV")
    export.add_argument("-o", "--output", default="cases_export.csv")
    export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
