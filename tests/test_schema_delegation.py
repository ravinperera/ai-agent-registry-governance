from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "schemas" / "governance-resource.schema.json"
EXAMPLE_PATH = ROOT / "registry" / "resources" / "approved-terraform-review-skill.json"


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def errors_for(record: dict[str, object]) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(record)]


class DelegationSchemaTests(unittest.TestCase):
    def test_enabled_delegation_requires_explicit_delegate_allowlist(self) -> None:
        record = load_json(EXAMPLE_PATH)
        record["delegation"] = {
            "allowed": True,
            "maxHops": 2,
            "scopeNarrowingRequired": True,
            "allowedDelegates": [],
        }

        errors = errors_for(record)

        self.assertTrue(any("should be non-empty" in error or "too short" in error for error in errors))

    def test_enabled_delegation_accepts_named_delegate(self) -> None:
        record = load_json(EXAMPLE_PATH)
        record["delegation"] = {
            "allowed": True,
            "maxHops": 2,
            "scopeNarrowingRequired": True,
            "allowedDelegates": ["security-analysis-agent"],
        }

        errors = errors_for(record)
        delegation_errors = [error for error in errors if "allowedDelegates" in error]

        self.assertEqual(delegation_errors, [])

    def test_no_oversight_cannot_allow_delegated_approval(self) -> None:
        record = load_json(EXAMPLE_PATH)
        record["humanOversight"]["delegatedApprovalAllowed"] = True

        errors = errors_for(record)

        self.assertTrue(any("False was expected" in error for error in errors))

    def test_no_egress_requires_empty_destination_allowlist(self) -> None:
        record = load_json(EXAMPLE_PATH)
        record["permissions"]["network"] = {
            "egress": "none",
            "allowedDestinations": ["api.example.org"],
        }

        errors = errors_for(record)
        self.assertTrue(any("expected to be empty" in error or "too long" in error for error in errors))

        record["permissions"]["network"]["allowedDestinations"] = []
        valid_errors = errors_for(record)
        self.assertEqual(valid_errors, [])


if __name__ == "__main__":
    unittest.main()
