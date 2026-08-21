from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_markdown_links.py"
SPEC = importlib.util.spec_from_file_location("check_markdown_links", MODULE_PATH)
assert SPEC and SPEC.loader
check_markdown_links = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_markdown_links)


class MarkdownLinkValidationTests(unittest.TestCase):
    def test_accepts_existing_local_links_and_ignores_external_and_anchor_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir()
            (root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Guide](docs/guide.md#section)\n"
                "[External](https://example.com)\n"
                "[Anchor](#local-heading)\n",
                encoding="utf-8",
            )

            self.assertEqual(check_markdown_links.validate(root), [])

    def test_reports_missing_local_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")

            errors = check_markdown_links.validate(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing local target 'docs/missing.md'", errors[0])

    def test_reports_missing_local_image_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "![Architecture](docs/missing.png)\n",
                encoding="utf-8",
            )

            errors = check_markdown_links.validate(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing local target 'docs/missing.png'", errors[0])

    def test_accepts_existing_local_image_and_ignores_external_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir()
            (root / "docs" / "diagram.png").write_bytes(b"not-a-real-png")
            (root / "README.md").write_text(
                "![Architecture](docs/diagram.png)\n"
                "![External](https://example.com/diagram.png)\n",
                encoding="utf-8",
            )

            self.assertEqual(check_markdown_links.validate(root), [])

    def test_rejects_repository_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            root.mkdir()
            (root / "README.md").write_text("[Outside](../outside.md)\n", encoding="utf-8")

            errors = check_markdown_links.validate(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("escapes repository root '../outside.md'", errors[0])

    def test_ignores_links_inside_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "```markdown\n[Example](not-a-real-file.md)\n```\n",
                encoding="utf-8",
            )

            self.assertEqual(check_markdown_links.validate(root), [])

    def test_ignores_untracked_markdown_inside_git_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            (root / "README.md").write_text("# Tracked\n", encoding="utf-8")
            (root / "scratch.md").write_text(
                "[Missing](docs/not-present.md)\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

            self.assertEqual(check_markdown_links.validate(root), [])


if __name__ == "__main__":
    unittest.main()
