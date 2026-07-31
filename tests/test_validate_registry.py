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


class RegistryValidatorTests(unittest.TestCase):
    def test_immutable_source_accepts_pins_and_rejects_mutable_refs(self) -> None:
        self.assertTrue(validator.is_immutable_source({"commit": "a" * 40}))
        self.assertTrue(validator.is_immutable_source({"digest": "sha256:" + "b" * 64}))
        self.assertTrue(validator.is_immutable_source({"version": "v1.2.3"}))
        self.assertFalse(validator.is_immutable_source({"version": "main"}))
        self.assertFalse(validator.is_immutable_source({"version": "latest"}))

    def test_elevated_authority_requires_high_risk_controls(self) -> None:
        record = {
            "source": {"commit": "a" * 40},
            "owner": {},
            "permissions": {
                "shell": "execute",
                "filesystem": "none",
                "secrets": "none",
                "network": {"egress": "none"},
            },
            "risk": {"tier": "medium", "humanApprovalRequired": False},
            "governance": {"status": "pending", "approvedBy": []},
            "runtime": {
                "sandboxRequired": False,
                "monitoringRequired": False,
                "auditLoggingRequired": False,
            },
        }

        errors = validator.policy_errors(record, date(2026, 7, 31))

        self.assertTrue(any("risk.tier" in error for error in errors))
        self.assertTrue(any("humanApprovalRequired" in error for error in errors))
        self.assertTrue(any("sandboxRequired" in error for error in errors))
        self.assertTrue(any("monitoringRequired" in error for error in errors))
        self.assertTrue(any("auditLoggingRequired" in error for error in errors))

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
            catalog_path.write_text(
                json.dumps({"entries": [entry, entry]}),
                encoding="utf-8",
            )

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
