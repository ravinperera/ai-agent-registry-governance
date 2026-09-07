from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry_rejected_metadata", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def rejected_record() -> dict[str, object]:
    return {
        "source": {"commit": "a" * 40},
        "owner": {},
        "permissions": {
            "shell": "none",
            "filesystem": "read",
            "secrets": "none",
            "network": {"egress": "none"},
        },
        "delegation": {"allowed": False},
        "humanOversight": {},
        "provenance": {},
        "risk": {"tier": "low"},
        "governance": {
            "status": "rejected",
            "rejectionReason": "The requested authority is not justified.",
        },
        "runtime": {},
    }


class RejectedStatusMetadataTests(unittest.TestCase):
    def test_rejected_resource_rejects_approval_only_metadata(self) -> None:
        record = rejected_record()
        governance = record["governance"]
        governance["approvedBy"] = ["platform-engineering"]
        governance["approvedAt"] = "2026-08-01"
        governance["reviewBy"] = "2026-09-01"

        errors = validator.policy_errors(record, date(2026, 8, 9))

        self.assertEqual(
            [error for error in errors if "rejected resources must not carry approval metadata" in error],
            [
                "policy governance.approvedBy: rejected resources must not carry approval metadata",
                "policy governance.approvedAt: rejected resources must not carry approval metadata",
                "policy governance.reviewBy: rejected resources must not carry approval metadata",
            ],
        )

    def test_clean_rejected_resource_has_no_approval_metadata_error(self) -> None:
        errors = validator.policy_errors(rejected_record(), date(2026, 8, 9))
        self.assertFalse(
            any("rejected resources must not carry approval metadata" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
