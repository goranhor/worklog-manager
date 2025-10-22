"""Utility script to bump the Worklog Manager version across project files."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / "settings.json"

# Files updated via simple string replacement of the current version string.
REPLACEMENT_FILES = (
    "README.md",
    "CHANGELOG.md",
    "DOCUMENTATION_SUMMARY.md",
    "PROJECT_OVERVIEW.md",
    "requirements.txt",
    "start_worklog.py",
    "start_worklog.sh",
    "start_worklog.bat",
    "main.py",
    "gui/main_window.py",
    "gui/system_tray.py",
    "docs/TECHNICAL_SPECIFICATION.md",
    "docs/COMPLETION_SUMMARY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
)


@dataclass
class UpdateResult:
    path: Path
    updated: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump project version strings")
    parser.add_argument("new_version", help="New semantic version, e.g. 1.8.0")
    parser.add_argument(
        "--current",
        dest="current_version",
        help="Override detected current version",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned updates without writing files",
    )
    parser.add_argument(
        "--skip-roadmap",
        action="store_true",
        help="Do not adjust roadmap version sections",
    )
    return parser.parse_args()


def load_current_version(override: str | None) -> str:
    if override:
        return override
    with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["version"]


def write_file(path: Path, content: str, *, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(content, encoding="utf-8")


def replace_version(path: Path, current: str, new: str, *, dry_run: bool) -> UpdateResult:
    text = path.read_text(encoding="utf-8")
    if current not in text:
        return UpdateResult(path, False)
    updated = text.replace(current, new)
    write_file(path, updated, dry_run=dry_run)
    return UpdateResult(path, True)


def bump_minor(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{int(major)}.{int(minor) + 1}.{int(patch)}"


def update_roadmap(current: str, new: str, *, dry_run: bool) -> UpdateResult:
    roadmap_path = PROJECT_ROOT / "ROADMAP.md"
    text = roadmap_path.read_text(encoding="utf-8")

    old_collab = bump_minor(current)
    old_integration = bump_minor(old_collab)
    new_collab = bump_minor(new)
    new_integration = bump_minor(new_collab)

    replacements = {
        f"## Version {current} - CURRENT ✅": f"## Version {new} - CURRENT ✅",
        f"## Version {current} - Data Management (Planned)": f"## Version {new} - Data Management (Planned)",
        f"## Version {old_collab} - Collaboration Features (Under Consideration)": f"## Version {new_collab} - Collaboration Features (Under Consideration)",
        f"## Version {old_integration} - Integration & Automation (Future)": f"## Version {new_integration} - Integration & Automation (Future)",
        f"planned for v{current}": f"planned for v{new}",
        f"for v{old_collab}": f"for v{new_collab}",
    }

    updated = text
    changed = False
    for old, new_value in replacements.items():
        if old in updated:
            updated = updated.replace(old, new_value)
            changed = True

    if changed:
        write_file(roadmap_path, updated, dry_run=dry_run)
    return UpdateResult(roadmap_path, changed)


def update_files(paths: Iterable[str], current: str, new: str, *, dry_run: bool) -> list[UpdateResult]:
    results: list[UpdateResult] = []
    for relative in paths:
        path = PROJECT_ROOT / relative
        results.append(replace_version(path, current, new, dry_run=dry_run))
    return results


def main() -> None:
    args = parse_args()
    current_version = load_current_version(args.current_version)
    new_version = args.new_version

    if current_version == new_version:
        print(f"Version already set to {new_version}")
        return

    results = update_files(REPLACEMENT_FILES, current_version, new_version, dry_run=args.dry_run)

    if not args.skip_roadmap:
        results.append(update_roadmap(current_version, new_version, dry_run=args.dry_run))

    touched = [res for res in results if res.updated]
    missing = [res for res in results if not res.updated]

    for res in touched:
        print(f"Updated {res.path.relative_to(PROJECT_ROOT)}")
    for res in missing:
        print(f"Skipped {res.path.relative_to(PROJECT_ROOT)} (no '{current_version}' found)")

    if args.dry_run:
        print("Dry-run complete; no files were modified.")
    else:
        # Update settings.json explicitly to keep the JSON value in sync even if
        # the replacement list omitted it for some reason.
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        settings["version"] = new_version
        write_file(
            SETTINGS_PATH,
            json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
            dry_run=False,
        )
        print(f"Bumped version {current_version} -> {new_version}")


if __name__ == "__main__":
    main()
