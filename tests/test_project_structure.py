"""
test_project_structure.py
--------------------------
Basic sanity checks for the Netflix DE portfolio project.
Ensures key files exist and the YAML config template is parseable.
"""

import pytest
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── File existence tests ──────────────────────────────────────────────────────

EXPECTED_NOTEBOOKS = [
    "notebooks/01_Autoloader.ipynb",
    "notebooks/02_Silver_Titles.ipynb",
    "notebooks/03_Lookup_Ingestion.ipynb",
    "notebooks/04_Silver_Transformation.ipynb",
    "notebooks/05_Gold_Notebook.ipynb",
    "notebooks/05_Gold_Top_Genres.ipynb",
]

@pytest.mark.parametrize("notebook_path", EXPECTED_NOTEBOOKS)
def test_notebook_exists(notebook_path: str) -> None:
    """Every expected notebook must be present in the repo."""
    assert (ROOT / notebook_path).exists(), f"Missing notebook: {notebook_path}"


def test_readme_exists() -> None:
    assert (ROOT / "README.md").exists()


def test_runbook_exists() -> None:
    assert (ROOT / "docs" / "runbook.md").exists()


def test_dashboard_screenshot_exists() -> None:
    assert (ROOT / "dashboard" / "netflix_dashboard.png").exists()


# ── Config template tests ─────────────────────────────────────────────────────

def test_dev_example_yml_is_valid_yaml() -> None:
    """The example config must be valid YAML so users can copy it safely."""
    config_path = ROOT / "config" / "dev.example.yml"
    assert config_path.exists(), "dev.example.yml is missing"
    with open(config_path) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "dev.example.yml did not parse to a dict"


def test_dev_example_yml_has_required_keys() -> None:
    """The example config must contain the expected top-level sections."""
    config_path = ROOT / "config" / "dev.example.yml"
    with open(config_path) as f:
        data = yaml.safe_load(f)
    for key in ("environment", "pipeline", "quality_rules"):
        assert key in data, f"dev.example.yml is missing key: '{key}'"
