from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def approved_record(review_by: str) -> dict[str, object]:
    return {
        "source": {"commit": "a" * 40},
        "owner": {
            "team": "platform-engineering",
            "serviceOwner": "service-owner",
            "securityContact": "security@example.org",
        },
        "permissions": {
            "shell": "none",
            "filesystem": "read",
            "secrets": "none",
            "network": {"egress": "none"},
        },
        "delegation": {
            "allowed": False,
            "maxHops": 0,
            "scopeNarrowingRequired": True,
            "allowedDelegates": [],
        },
        "humanOversight": {
            "mode": "none",
            "approvalRequiredFor": [],
            "delegatedApprovalAllowed": False,
            "approvalProvenanceRequired": False,
        },
        "provenance": {
            "required": False,
            "mechanism": "none",
            "tamperEvident": False,
            "recordsOriginatingHuman": False,
            "recordsDelegationChain": False,
        },
        "risk": {"tier": "low"},
        "governance": {
            "status": "approved",
            "reviewBy": review_by,
            "approvedBy": ["platform-engineering"],
            "evidence": "fictional-review-record",
        },
        "runtime": {
            "sandboxRequired": False,
            "monitoringRequired": False,
            "auditLoggingRequired": False,
        },
    }


class RegistryValidatorTests(unittest.TestCase):
    def test_immutable_source_accepts_pins_and_rejects_mutable_refs(self) -> None:
        self.assertTrue(validator.is_immutable_source({"commit": "a" * 40}))
        self.assertTrue(validator.is_immutable_source({"digest": "sha256:" + "b" * 64}))
        self.assertTrue(validator.is_immutable_source({"version": "v1.2.3"}))
        self.assertFalse(validator.is_immutable_source({"version": "main"}))
        self.assertFalse(validator.is_immutable_source({"version": "latest"}))

    def test_elevated_authority_requires_high_risk_action_controls(self) -> None:
        record = {
            "source": {"commit": "a" * 40},
            "owner": {},
            "permissions": {
                "shell": "execute",
                "filesystem": "none",
                "secrets": "none",
                "network": {"egress": "none"},
            },
            "delegation": {"allowed": False},
            "humanOversight": {
                "mode": "session",
                "approvalRequiredFor": [],
                "delegatedApprovalAllowed": True,
                "approvalProvenanceRequired": False,
            },
            "provenance": {
                "required": False,
                "tamperEvident": False,
                "recordsOriginatingHuman": False,
                "recordsDelegationChain": False,
            },
            "risk": {"tier": "medium"},
            "governance": {"status": "pending", "approvedBy": []},
            "runtime": {
                "sandboxRequired": False,
                "monitoringRequired": False,
                "auditLoggingRequired": False,
            },
        }

        errors = validator.policy_errors(record, date(2026, 7, 31))

        self.assertTrue(any("risk.tier" in error for error in errors))
        self.assertTrue(any("humanOversight.mode" in error for error in errors))
        self.assertTrue(any("approvalRequiredFor" in error for error in errors))
        self.assertTrue(any("approvalProvenanceRequired" in error for error in errors))
        self.assertTrue(any("delegatedApprovalAllowed" in error for error in errors))
        self.assertTrue(any("provenance.required" in error for error in errors))
        self.assertTrue(any("sandboxRequired" in error for error in errors))
        self.assertTrue(any("monitoringRequired" in error for error in errors))
        self.assertTrue(any("auditLoggingRequired" in error for error in errors))

    def test_delegation_requires_medium_risk_scope_narrowing_and_provenance(self) -> None:
        record = approved_record("2026-08-10")
        record["delegation"] = {
            "allowed": True,
            "maxHops": 2,
            "scopeNarrowingRequired": False,
            "allowedDelegates": ["review-agent"],
        }

        errors = validator.policy_errors(record, date(2026, 8, 9))

        self.assertTrue(any("risk.tier" in error for error in errors))
        self.assertTrue(any("scopeNarrowingRequired" in error for error in errors))
        self.assertTrue(any("provenance.required" in error for error in errors))
        self.assertTrue(any("provenance.tamperEvident" in error for error in errors))
        self.assertTrue(any("recordsOriginatingHuman" in error for error in errors))
        self.assertTrue(any("recordsDelegationChain" in error for error in errors))
        self.assertTrue(any("auditLoggingRequired" in error for error in errors))

    def test_well_controlled_delegation_passes_delegation_policy(self) -> None:
        record = approved_record("2026-08-10")
        record["risk"] = {"tier": "medium"}
        record["delegation"] = {
            "allowed": True,
            "maxHops": 2,
            "scopeNarrowingRequired": True,
            "allowedDelegates": ["review-agent"],
        }
        record["provenance"] = {
            "required": True,
            "mechanism": "signed-delegation-chain",
            "tamperEvident": True,
            "recordsOriginatingHuman": True,
            "recordsDelegationChain": True,
        }
        record["runtime"]["auditLoggingRequired"] = True

        errors = validator.policy_errors(record, date(2026, 8, 9))
        delegation_errors = [
            error
            for error in errors
            if "delegation." in error or "provenance." in error or "auditLoggingRequired" in error
        ]

        self.assertEqual(delegation_errors, [])

    def test_approved_resource_review_expires_on_review_date(self) -> None:
        today = date(2026, 8, 9)

        errors = validator.policy_errors(approved_record("2026-08-09"), today)
        future_errors = validator.policy_errors(approved_record("2026-08-10"), today)

        self.assertTrue(any("governance.reviewBy" in error for error in errors))
        self.assertFalse(any("governance.reviewBy" in error for error in future_errors))

    def test_pending_resource_rejects_approval_only_metadata(self) -> None:
        record = approved_record("2026-08-10")
        record["governance"]["status"] = "pending"
        record["governance"]["approvedAt"] = "2026-08-01"

        errors = validator.policy_errors(record, date(2026, 8, 9))
        pending_errors = [error for error in errors if "pending resources must not carry approval metadata" in error]

        self.assertEqual(
            pending_errors,
            [
                "policy governance.approvedBy: pending resources must not carry approval metadata",
                "policy governance.approvedAt: pending resources must not carry approval metadata",
                "policy governance.reviewBy: pending resources must not carry approval metadata",
            ],
        )

        for field in ("approvedBy", "approvedAt", "reviewBy"):
            record["governance"].pop(field, None)
        clean_errors = validator.policy_errors(record, date(2026, 8, 9))
        self.assertFalse(any("pending resources must not carry approval metadata" in error for error in clean_errors))

    def test_restricted_egress_requires_explicit_non_wildcard_allowlist(self) -> None:
        record = approved_record("2026-08-10")
        network = record["permissions"]["network"]
        network["egress"] = "restricted"
        network["allowedDestinations"] = ["api.example.org"]

        errors = validator.policy_errors(record, date(2026, 8, 9))
        self.assertFalse(any("allowedDestinations" in error for error in errors))

        network["allowedDestinations"] = ["*"]
        wildcard_errors = validator.policy_errors(record, date(2026, 8, 9))
        self.assertTrue(any("allowedDestinations" in error for error in wildcard_errors))

        network["allowedDestinations"] = []
        empty_errors = validator.policy_errors(record, date(2026, 8, 9))
        self.assertTrue(any("allowedDestinations" in error for error in empty_errors))

    def test_approved_resource_rejects_unrestricted_egress(self) -> None:
        record = approved_record("2026-08-10")
        record["permissions"]["network"] = {"egress": "unrestricted"}
        record["risk"] = {"tier": "high"}
        record["humanOversight"] = {
            "mode": "per-consequential-action",
            "approvalRequiredFor": ["network-access"],
            "delegatedApprovalAllowed": False,
            "approvalProvenanceRequired": True,
        }
        record["provenance"] = {
            "required": True,
            "mechanism": "signed-approval",
            "tamperEvident": True,
            "recordsOriginatingHuman": True,
            "recordsDelegationChain": False,
        }
        record["governance"]["approvedBy"] = ["platform-engineering", "security"]
        record["runtime"] = {
            "sandboxRequired": True,
            "monitoringRequired": True,
            "auditLoggingRequired": True,
        }

        errors = validator.policy_errors(record, date(2026, 8, 9))

        self.assertEqual(
            [error for error in errors if "permissions.network.egress" in error],
            ["policy permissions.network.egress: unrestricted egress cannot be approved by the baseline policy"],
        )

    def test_catalog_rejects_resources_without_approved_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "ai-catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "identifier": "urn:air:example.org:skill:review",
                                "url": "https://example.org/review",
                                "representativeQueries": ["Review this", "Check this"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            errors = validator.validate_catalog(catalog_path, {}, None)

        self.assertTrue(any("only approved governance records" in error for error in errors))

    def test_catalog_rejects_duplicate_identifiers(self) -> None:
        identifier = "urn:air:example.org:skill:review"
        entry = {
            "identifier": identifier,
            "url": "https://example.org/review",
            "representativeQueries": ["Review this", "Check this"],
        }
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "ai-catalog.json"
            catalog_path.write_text(json.dumps({"entries": [entry, entry]}), encoding="utf-8")

            errors = validator.validate_catalog(catalog_path, {identifier: {}}, None)

        duplicate_errors = [error for error in errors if "duplicate identifier" in error]
        self.assertEqual(
            duplicate_errors,
            [f"catalog entries[1].identifier: duplicate identifier {identifier}"],
        )

    def test_catalog_accepts_one_published_approved_resource(self) -> None:
        identifier = "urn:air:example.org:skill:review"
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "ai-catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "identifier": identifier,
                                "url": "https://example.org/review",
                                "representativeQueries": ["Review this", "Check this"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            errors = validator.validate_catalog(catalog_path, {identifier: {}}, None)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
