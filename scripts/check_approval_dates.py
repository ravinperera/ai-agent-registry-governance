#!/usr/bin/env python3
"""Validate temporal consistency of approved governance records."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "registry/resources"


def load_record(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def parse_iso_date(value: Any, field: str) -> tuple[date | None, list[str]]:
    if not isinstance(value, str):
        return None, [f"{field}: must be an ISO date"]
    try:
        return date.fromisoformat(value), []
    except ValueError:
        return None, [f"{field}: must be an ISO date"]


def approval_date_errors(record: dict[str, Any], today: date) -> list[str]:
    governance = record.get("governance", {})
    if governance.get("status") != "approved":
        return []

    errors: list[str] = []
    approved_at, approved_errors = parse_iso_date(governance.get("approvedAt"), "governance.approvedAt")
    review_by, review_errors = parse_iso_date(governance.get("reviewBy"), "governance.reviewBy")
    errors.extend(approved_errors)
    errors.extend(review_errors)

    if approved_at is not None and approved_at > today:
        errors.append("governance.approvedAt: approval date cannot be in the future")

    if approved_at is not None and review_by is not None and review_by <= approved_at:
        errors.append("governance.reviewBy: review date must be later than approval date")

    return errors


def main() -> int:
    failures = 0
    paths = sorted(RECORDS_DIR.glob("*.json"))
    if not paths:
        print(f"ERROR {RECORDS_DIR}: no governance records found")
        return 1

    today = date.today()
    for path in paths:
        try:
            record = load_record(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"ERROR {path}: cannot read valid JSON: {exc}")
            failures += 1
            continue

        errors = approval_date_errors(record, today)
        if errors:
            failures += 1
            for error in errors:
                print(f"ERROR {path}: {error}")
        else:
            print(f"PASS  {path}")

    if failures:
        print(f"\nApproval date validation failed in {failures} record(s).")
        return 1

    print("\nAll approved-resource dates are temporally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
