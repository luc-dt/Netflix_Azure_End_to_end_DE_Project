"""
validate_project.py
-------------------
Validates the repository structure for the Netflix DE portfolio project.
Run by GitHub Actions on every push to main.

Checks:
  - All expected notebooks are present
  - Config files exist
  - Key documentation files exist
  - Dashboard assets exist
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_NOTEBOOKS = [
    "notebooks/01_Autoloader.ipynb",
    "notebooks/02_Silver_Titles.ipynb",
    "notebooks/03_Lookup_Ingestion.ipynb",
    "notebooks/04_Silver_Transformation.ipynb",
    "notebooks/05_Gold_Notebook.ipynb",
    "notebooks/05_Gold_Top_Genres.ipynb",
]

REQUIRED_FILES = [
    "README.md",
    "pyproject.toml",
    "config/dev.example.yml",
    "docs/runbook.md",
    "dashboard/netflix_dashboard.png",
]

def check_files(label: str, paths: list[str]) -> list[str]:
    errors = []
    for rel_path in paths:
        full_path = ROOT / rel_path
        if not full_path.exists():
            errors.append(f"  MISSING: {rel_path}")
        else:
            print(f"  OK: {rel_path}")
    return errors


def main() -> None:
    print("\n=== Netflix DE Project — Structure Validation ===\n")

    all_errors: list[str] = []

    print("Checking notebooks...")
    all_errors += check_files("notebooks", REQUIRED_NOTEBOOKS)

    print("\nChecking core files...")
    all_errors += check_files("core", REQUIRED_FILES)

    print()
    if all_errors:
        print("VALIDATION FAILED — missing files:")
        for err in all_errors:
            print(err)
        sys.exit(1)
    else:
        print("All checks passed. Repository structure is valid.")


if __name__ == "__main__":
    main()
