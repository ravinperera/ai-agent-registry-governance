#!/usr/bin/env python3
"""Validate catalog metadata links to local approved governance records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def validate(catalog_path: Path, root: Path = ROOT) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    try:
        catalog = load_object(catalog_path)
    except ValueError as exc:
        return [f"catalog: {exc}"]

    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        return ["catalog entries: must be an array"]

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entries[{index}]: must be an object")
            continue

        identifier = entry.get("identifier")
        metadata = entry.get("metadata")
        if not isinstance(metadata, dict):
            errors.append(f"entries[{index}].metadata: governance metadata is required")
            continue

        record_ref = metadata.get("governanceRecord")
        if not isinstance(record_ref, str) or not record_ref.strip():
            errors.append(f"entries[{index}].metadata.governanceRecord: local record path is required")
            continue

        record_path = (root / record_ref).resolve()
        try:
            record_path.relative_to(root)
        except ValueError:
            errors.append(f"entries[{index}].metadata.governanceRecord: path escapes repository root")
            continue

        if not record_path.is_file():
            errors.append(f"entries[{index}].metadata.governanceRecord: referenced record does not exist")
            continue

        try:
            record = load_object(record_path)
        except ValueError as exc:
            errors.append(f"entries[{index}].metadata.governanceRecord: {exc}")
            continue

        record_identifier = record.get("resource", {}).get("identifier")
        if record_identifier != identifier:
            errors.append(
                f"entries[{index}].metadata.governanceRecord: record identifier does not match catalog identifier"
            )

        record_status = record.get("governance", {}).get("status")
        if record_status != "approved":
            errors.append(
                f"entries[{index}].metadata.governanceRecord: catalog may only link to an approved record"
            )

        approval_status = metadata.get("approvalStatus")
        if approval_status is not None and approval_status != "approved":
            errors.append(
                f"entries[{index}].metadata.approvalStatus: published catalog status must be approved"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "catalog",
        nargs="?",
        type=Path,
        default=ROOT / "catalog/ai-catalog.json",
        help="catalog file to validate",
    )
    args = parser.parse_args()

    errors = validate(args.catalog)
    if errors:
        print("Catalog governance-link validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Catalog governance metadata links to approved local records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
