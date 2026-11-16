from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_catalog_governance_links.py"
SPEC = importlib.util.spec_from_file_location("check_catalog_governance_links", SCRIPT_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class CatalogGovernanceLinkTests(unittest.TestCase):
    def make_fixture(
        self,
        *,
        catalog_identifier: str = "urn:air:example.org:skill:review",
        record_identifier: str = "urn:air:example.org:skill:review",
        record_status: str = "approved",
        approval_status: str = "approved",
        record_ref: str = "registry/resources/review.json",
    ) -> tuple[Path, Path, tempfile.TemporaryDirectory[str]]:
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        record_path = root / "registry/resources/review.json"
        record_path.parent.mkdir(parents=True)
        record_path.write_text(
            json.dumps(
                {
                    "resource": {"identifier": record_identifier},
                    "governance": {"status": record_status},
                }
            ),
            encoding="utf-8",
        )
        catalog_path = root / "catalog/ai-catalog.json"
        catalog_path.parent.mkdir(parents=True)
        catalog_path.write_text(
            json.dumps(
                {
                    "entries": [
                        {
                            "identifier": catalog_identifier,
                            "metadata": {
                                "governanceRecord": record_ref,
                                "approvalStatus": approval_status,
                            },
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return root, catalog_path, directory

    def test_matching_approved_record_passes(self) -> None:
        root, catalog_path, directory = self.make_fixture()
        self.addCleanup(directory.cleanup)
        self.assertEqual(checker.validate(catalog_path, root), [])

    def test_identifier_mismatch_fails(self) -> None:
        root, catalog_path, directory = self.make_fixture(record_identifier="urn:air:example.org:skill:other")
        self.addCleanup(directory.cleanup)
        errors = checker.validate(catalog_path, root)
        self.assertTrue(any("identifier does not match" in error for error in errors))

    def test_non_approved_record_fails(self) -> None:
        root, catalog_path, directory = self.make_fixture(record_status="pending")
        self.addCleanup(directory.cleanup)
        errors = checker.validate(catalog_path, root)
        self.assertTrue(any("only link to an approved record" in error for error in errors))

    def test_missing_record_fails_without_echoing_path_content(self) -> None:
        root, catalog_path, directory = self.make_fixture(record_ref="registry/resources/missing.json")
        self.addCleanup(directory.cleanup)
        errors = checker.validate(catalog_path, root)
        self.assertTrue(any("referenced record does not exist" in error for error in errors))

    def test_non_approved_catalog_metadata_fails(self) -> None:
        root, catalog_path, directory = self.make_fixture(approval_status="pending")
        self.addCleanup(directory.cleanup)
        errors = checker.validate(catalog_path, root)
        self.assertTrue(any("published catalog status must be approved" in error for error in errors))


    def test_unvalidated_record_locations_are_rejected(self) -> None:
        # These files look approved but are never scanned by validate_registry.py.
        for record_ref in (
            "docs/forged-approval.json",
            "registry/resources/nested/review.json",
            "registry/resources/review.txt",
        ):
            with self.subTest(record_ref=record_ref):
                root, catalog_path, directory = self.make_fixture(record_ref=record_ref)
                self.addCleanup(directory.cleanup)
                untracked = root / record_ref
                untracked.parent.mkdir(parents=True, exist_ok=True)
                untracked.write_text(
                    (root / "registry/resources/review.json").read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

                errors = checker.validate(catalog_path, root)
                self.assertTrue(any("direct .json file" in error for error in errors), errors)
                self.assertNotIn(record_ref, " ".join(errors))

    def test_registry_symlink_to_unvalidated_document_is_rejected(self) -> None:
        root, catalog_path, directory = self.make_fixture(record_ref="registry/resources/alias.json")
        self.addCleanup(directory.cleanup)
        fake_record = root / "docs/forged-approval.json"
        fake_record.parent.mkdir(parents=True)
        fake_record.write_text(
            (root / "registry/resources/review.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "registry/resources/alias.json").symlink_to(fake_record)

        errors = checker.validate(catalog_path, root)
        self.assertTrue(any("must resolve to a direct .json file" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
