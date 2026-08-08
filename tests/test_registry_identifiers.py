from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class RegistryIdentifierTests(unittest.TestCase):
    def test_duplicate_registry_identifier_reports_first_file(self) -> None:
        identifier = "urn:air:example.org:skill:review"
        record = {"resource": {"identifier": identifier}}
        seen: dict[str, Path] = {}
        first = Path("registry/resources/first.json")
        duplicate = Path("registry/resources/duplicate.json")

        self.assertIsNone(validator.register_identifier(first, record, seen))
        error = validator.register_identifier(duplicate, record, seen)

        self.assertIsNotNone(error)
        assert error is not None
        self.assertIn(f"duplicate identifier {identifier}", error)
        self.assertIn(str(first), error)

    def test_unique_registry_identifiers_are_accepted(self) -> None:
        seen: dict[str, Path] = {}

        first = validator.register_identifier(
            Path("registry/resources/first.json"),
            {"resource": {"identifier": "urn:air:example.org:skill:first"}},
            seen,
        )
        second = validator.register_identifier(
            Path("registry/resources/second.json"),
            {"resource": {"identifier": "urn:air:example.org:skill:second"}},
            seen,
        )

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertEqual(len(seen), 2)


if __name__ == "__main__":
    unittest.main()
