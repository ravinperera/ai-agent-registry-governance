from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_approval_dates.py"
SPEC = importlib.util.spec_from_file_location("check_approval_dates", SCRIPT_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def approved_record(approved_at: str, review_by: str) -> dict[str, object]:
    return {
        "governance": {
            "status": "approved",
            "approvedAt": approved_at,
            "reviewBy": review_by,
        }
    }


class ApprovalDateTests(unittest.TestCase):
    def test_valid_approval_window_passes(self) -> None:
        errors = checker.approval_date_errors(
            approved_record("2026-08-01", "2026-09-01"),
            date(2026, 8, 29),
        )
        self.assertEqual(errors, [])

    def test_future_approval_date_is_rejected(self) -> None:
        errors = checker.approval_date_errors(
            approved_record("2026-08-30", "2026-09-30"),
            date(2026, 8, 29),
        )
        self.assertIn(
            "governance.approvedAt: approval date cannot be in the future",
            errors,
        )

    def test_review_date_must_follow_approval_date(self) -> None:
        same_day = checker.approval_date_errors(
            approved_record("2026-08-20", "2026-08-20"),
            date(2026, 8, 29),
        )
        earlier = checker.approval_date_errors(
            approved_record("2026-08-20", "2026-08-19"),
            date(2026, 8, 29),
        )

        expected = "governance.reviewBy: review date must be later than approval date"
        self.assertIn(expected, same_day)
        self.assertIn(expected, earlier)

    def test_pending_resource_is_not_treated_as_approved(self) -> None:
        record = {
            "governance": {
                "status": "pending",
                "approvedAt": "2099-01-01",
                "reviewBy": "2099-01-01",
            }
        }
        self.assertEqual(checker.approval_date_errors(record, date(2026, 8, 29)), [])


if __name__ == "__main__":
    unittest.main()
