#!/usr/bin/env python3
"""Validate repository-local Markdown links and images without network access."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

INLINE_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _clean_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        target = target.split(None, 1)[0]
    return target.strip()


def _is_local_target(target: str) -> bool:
    if not target or target.startswith(("#", "//")):
        return False
    return not urlsplit(target).scheme


def _resolve_target(root: Path, source: Path, target: str) -> Path:
    path_text = unquote(urlsplit(target).path)
    if path_text.startswith("/"):
        return root / path_text.lstrip("/")
    return source.parent / path_text


def _inside_root(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError:
        return False
    return True


def repository_markdown_files(root: Path) -> list[Path]:
    """Return tracked Markdown files, with a filesystem fallback outside Git."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return sorted(
            path
            for path in root.rglob("*.md")
            if path.is_file() and ".git" not in path.parts
        )

    return sorted(
        root / raw.decode("utf-8")
        for raw in result.stdout.split(b"\0")
        if raw
    )


def links_in_markdown(path: Path) -> list[tuple[int, str]]:
    links: list[tuple[int, str]] = []
    in_fence = False

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        links.extend((line_number, match.group(1)) for match in INLINE_LINK_RE.finditer(line))
        reference_match = REFERENCE_LINK_RE.match(line)
        if reference_match:
            links.append((line_number, reference_match.group(1)))

    return links


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    for markdown_file in repository_markdown_files(root):
        for line_number, raw_target in links_in_markdown(markdown_file):
            target = _clean_target(raw_target)
            if not _is_local_target(target):
                continue

            resolved = _resolve_target(root, markdown_file, target)
            relative_source = markdown_file.relative_to(root)
            if not _inside_root(root, resolved):
                errors.append(
                    f"{relative_source}:{line_number}: local target escapes repository root '{target}'"
                )
                continue
            if not resolved.exists():
                errors.append(f"{relative_source}:{line_number}: missing local target '{target}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to scan")
    args = parser.parse_args()

    errors = validate(Path(args.root))
    if errors:
        print("Markdown link/image validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Markdown local links and images are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
