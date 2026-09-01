#!/usr/bin/env python3
"""Validate governance records and an optional ARD catalog schema."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MUTABLE_REFS = {"latest", "main", "master", "develop", "development", "head", "trunk"}
SEMVER_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting ambiguous duplicate keys."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle, object_pairs_hook=reject_duplicate_keys)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{path}: cannot read valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return value


def format_path(parts: list[Any]) -> str:
    return ".".join(str(part) for part in parts) or "$"


def schema_errors(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"schema {format_path(list(error.absolute_path))}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]


def parse_date(value: Any, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"policy {field}: must be an ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"policy {field}: must be an ISO date")
        return None


def is_immutable_source(source: dict[str, Any]) -> bool:
    if source.get("commit") or source.get("digest"):
        return True
    version = str(source.get("version", "")).strip().lower()
    return bool(version and version not in MUTABLE_REFS and SEMVER_RE.fullmatch(version))


def policy_errors(record: dict[str, Any], today: date) -> list[str]:
    errors: list[str] = []
    source = record.get("source", {})
    owner = record.get("owner", {})
    permissions = record.get("permissions", {})
    network = permissions.get("network", {})
    delegation = record.get("delegation", {})
    oversight = record.get("humanOversight", {})
    provenance = record.get("provenance", {})
    risk = record.get("risk", {})
    governance = record.get("governance", {})
    runtime = record.get("runtime", {})

    if not is_immutable_source(source):
        errors.append("policy source: use a full commit SHA, sha256 digest or immutable semantic version")

    status = governance.get("status")
    tier = risk.get("tier")
    shell = permissions.get("shell")
    filesystem = permissions.get("filesystem")
    secrets = permissions.get("secrets")
    egress = network.get("egress")

    elevated_authority = any(
        [
            shell == "execute",
            filesystem == "write",
            secrets == "read",
            egress == "unrestricted",
        ]
    )
    delegation_allowed = delegation.get("allowed") is True
    consequential = elevated_authority or tier in {"high", "critical"}

    if elevated_authority and tier not in {"high", "critical"}:
        errors.append("policy risk.tier: write, shell, secrets or unrestricted egress requires high or critical risk")

    if delegation_allowed and tier == "low":
        errors.append("policy risk.tier: any authority delegation requires at least medium risk")

    if delegation_allowed:
        if delegation.get("scopeNarrowingRequired") is not True:
            errors.append("policy delegation.scopeNarrowingRequired: delegated authority must only narrow, never expand")
        if provenance.get("required") is not True:
            errors.append("policy provenance.required: delegated authority requires provenance evidence")
        if provenance.get("tamperEvident") is not True:
            errors.append("policy provenance.tamperEvident: delegation evidence must be tamper-evident")
        if provenance.get("recordsOriginatingHuman") is not True:
            errors.append("policy provenance.recordsOriginatingHuman: delegation must retain the originating human")
        if provenance.get("recordsDelegationChain") is not True:
            errors.append("policy provenance.recordsDelegationChain: delegation must retain the full delegation chain")
        if runtime.get("auditLoggingRequired") is not True:
            errors.append("policy runtime.auditLoggingRequired: delegation requires audit logging")

    if consequential:
        if oversight.get("mode") not in {"per-consequential-action", "always"}:
            errors.append("policy humanOversight.mode: high-risk or elevated authority requires action-level human oversight")
        if not oversight.get("approvalRequiredFor"):
            errors.append("policy humanOversight.approvalRequiredFor: consequential actions must be named explicitly")
        if oversight.get("approvalProvenanceRequired") is not True:
            errors.append("policy humanOversight.approvalProvenanceRequired: consequential actions require approval provenance")
        if oversight.get("delegatedApprovalAllowed") is True:
            errors.append("policy humanOversight.delegatedApprovalAllowed: baseline policy forbids delegated approval for high-risk authority")
        if provenance.get("required") is not True:
            errors.append("policy provenance.required: consequential authority requires provenance evidence")
        if provenance.get("tamperEvident") is not True:
            errors.append("policy provenance.tamperEvident: consequential authority requires tamper-evident evidence")
        if provenance.get("recordsOriginatingHuman") is not True:
            errors.append("policy provenance.recordsOriginatingHuman: consequential authority must identify the originating human")
        if runtime.get("sandboxRequired") is not True:
            errors.append("policy runtime.sandboxRequired: elevated authority requires a sandbox")
        if runtime.get("monitoringRequired") is not True:
            errors.append("policy runtime.monitoringRequired: elevated authority requires monitoring")
        if runtime.get("auditLoggingRequired") is not True:
            errors.append("policy runtime.auditLoggingRequired: elevated authority requires audit logging")

    if egress == "unrestricted" and status == "approved":
        errors.append("policy permissions.network.egress: unrestricted egress cannot be approved by the baseline policy")

    if egress == "restricted":
        destinations = network.get("allowedDestinations", [])
        if not destinations or "*" in destinations:
            errors.append("policy permissions.network.allowedDestinations: restricted egress needs an explicit allowlist")

    if status == "approved":
        for field in ("team", "serviceOwner", "securityContact"):
            if not str(owner.get(field, "")).strip():
                errors.append(f"policy owner.{field}: approved resources require accountable ownership")

        review_by = parse_date(governance.get("reviewBy"), "governance.reviewBy", errors)
        if review_by is not None and review_by <= today:
            errors.append("policy governance.reviewBy: approval is expired or expires today")

        approvers = governance.get("approvedBy", [])
        if tier in {"high", "critical"} and len(approvers) < 2:
            errors.append("policy governance.approvedBy: high-risk approval requires at least two named approving groups")

        if not governance.get("evidence"):
            errors.append("policy governance.evidence: approved resources require retained evidence")

    if status == "pending":
        for field in ("approvedBy", "approvedAt", "reviewBy"):
            if field in governance:
                errors.append(f"policy governance.{field}: pending resources must not carry approval metadata")

    return errors


def register_identifier(
    path: Path,
    record: dict[str, Any],
    seen_identifiers: dict[str, Path],
) -> str | None:
    identifier = record["resource"]["identifier"]
    first_path = seen_identifiers.get(identifier)
    if first_path is not None:
        return (
            f"registry resource.identifier: duplicate identifier {identifier}; "
            f"first declared in {first_path}"
        )
    seen_identifiers[identifier] = path
    return None


def validate_record(path: Path, schema: dict[str, Any], today: date) -> list[str]:
    try:
        record = load_json(path)
    except ValueError as exc:
        return [str(exc)]
    return schema_errors(record, schema) + policy_errors(record, today)


def validate_catalog(
    catalog_path: Path,
    approved_records: dict[str, dict[str, Any]],
    ard_schema_path: Path | None,
) -> list[str]:
    errors: list[str] = []
    try:
        catalog = load_json(catalog_path)
    except ValueError as exc:
        return [str(exc)]

    if ard_schema_path is not None:
        try:
            ard_schema = load_json(ard_schema_path)
        except ValueError as exc:
            return [str(exc)]
        errors.extend(schema_errors(catalog, ard_schema))

    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        return errors + ["catalog entries: must be an array"]

    catalog_ids: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"catalog entries[{index}]: must be an object")
            continue
        identifier = entry.get("identifier")
        if not isinstance(identifier, str):
            errors.append(f"catalog entries[{index}].identifier: missing string identifier")
            continue
        if identifier in catalog_ids:
            errors.append(f"catalog entries[{index}].identifier: duplicate identifier {identifier}")
        else:
            catalog_ids.add(identifier)
        if identifier not in approved_records:
            errors.append(f"catalog {identifier}: only approved governance records may be published")
        if bool(entry.get("url")) == bool(entry.get("data")):
            errors.append(f"catalog {identifier}: provide exactly one of url or data")
        queries = entry.get("representativeQueries", [])
        if queries and not 2 <= len(queries) <= 5:
            errors.append(f"catalog {identifier}: representativeQueries should contain 2 to 5 examples")

    missing = set(approved_records) - catalog_ids
    for identifier in sorted(missing):
        errors.append(f"catalog {identifier}: approved resource is missing from the catalog")

    return errors


def print_errors(path: Path, errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR {path}: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "schemas/governance-resource.schema.json")
    parser.add_argument("--records-dir", type=Path, default=ROOT / "registry/resources")
    parser.add_argument("--catalog", type=Path, default=ROOT / "catalog/ai-catalog.json")
    parser.add_argument("--ard-schema", type=Path, default=None)
    parser.add_argument("--rejected-dir", type=Path, default=ROOT / "examples/rejected")
    args = parser.parse_args()

    today = date.today()
    try:
        schema = load_json(args.schema)
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1

    failures = 0
    approved_records: dict[str, dict[str, Any]] = {}
    seen_identifiers: dict[str, Path] = {}
    record_paths = sorted(args.records_dir.glob("*.json"))
    if not record_paths:
        print(f"ERROR {args.records_dir}: no governance records found")
        return 1

    for path in record_paths:
        errors = validate_record(path, schema, today)
        if errors:
            failures += 1
            print_errors(path, errors)
            continue
        record = load_json(path)
        duplicate_error = register_identifier(path, record, seen_identifiers)
        if duplicate_error:
            failures += 1
            print_errors(path, [duplicate_error])
            continue
        if record["governance"]["status"] == "approved":
            approved_records[record["resource"]["identifier"]] = record
        print(f"PASS  {path}")

    catalog_errors = validate_catalog(args.catalog, approved_records, args.ard_schema)
    if catalog_errors:
        failures += 1
        print_errors(args.catalog, catalog_errors)
    else:
        print(f"PASS  {args.catalog}")

    rejected_paths = sorted(args.rejected_dir.glob("*.json"))
    for path in rejected_paths:
        errors = validate_record(path, schema, today)
        if not errors:
            failures += 1
            print(f"ERROR {path}: rejected example unexpectedly passed validation")
        else:
            print(f"PASS  {path}: rejected as expected ({len(errors)} findings)")

    if failures:
        print(f"\nValidation failed in {failures} area(s).")
        return 1

    print("\nAll registry, catalog and negative-example checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
