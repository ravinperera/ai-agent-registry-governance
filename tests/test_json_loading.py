from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry_json_loading", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class JsonLoadingTests(unittest.TestCase):
    def test_load_json_rejects_duplicate_object_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"governance": {"status": "pending", "status": "approved"}}', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate object key: status"):
                validator.load_json(path)

    def test_load_json_accepts_unambiguous_objects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text('{"governance": {"status": "pending"}}', encoding="utf-8")

            self.assertEqual(
                validator.load_json(path),
                {"governance": {"status": "pending"}},
            )


if __name__ == "__main__":
    unittest.main()
