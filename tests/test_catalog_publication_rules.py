from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry_catalog_rules", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

IDENTIFIER = "urn:air:example.org:skill:review"


def validate(entries: list[dict[str, object]], approved: dict[str, dict[str, object]] | None = None) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        catalog_path = Path(directory) / "ai-catalog.json"
        catalog_path.write_text(json.dumps({"entries": entries}), encoding="utf-8")
        return validator.validate_catalog(
            catalog_path,
            approved if approved is not None else {IDENTIFIER: {}},
            None,
        )


class CatalogPublicationRuleTests(unittest.TestCase):
    def test_entry_requires_exactly_one_of_url_or_data(self) -> None:
        base = {
            "identifier": IDENTIFIER,
            "representativeQueries": ["Review this", "Check this"],
        }

        both_errors = validate([{**base, "url": "https://example.org/review", "data": {"name": "review"}}])
        neither_errors = validate([base])

        self.assertTrue(any("exactly one of url or data" in error for error in both_errors))
        self.assertTrue(any("exactly one of url or data" in error for error in neither_errors))

    def test_representative_queries_enforce_two_to_five_examples_when_present(self) -> None:
        one_query = {
            "identifier": IDENTIFIER,
            "url": "https://example.org/review",
            "representativeQueries": ["Review this"],
        }
        six_queries = {
            "identifier": IDENTIFIER,
            "url": "https://example.org/review",
            "representativeQueries": [f"Query {index}" for index in range(6)],
        }

        self.assertTrue(any("2 to 5 examples" in error for error in validate([one_query])))
        self.assertTrue(any("2 to 5 examples" in error for error in validate([six_queries])))

    def test_approved_resource_must_be_published(self) -> None:
        errors = validate([], {IDENTIFIER: {}})

        self.assertEqual(
            errors,
            [f"catalog {IDENTIFIER}: approved resource is missing from the catalog"],
        )


if __name__ == "__main__":
    unittest.main()
