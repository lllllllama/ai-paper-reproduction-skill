#!/usr/bin/env python3
"""Regression checks for conservative environment setup planning."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    planner = repo_root / "skills" / "env-and-assets-bootstrap" / "scripts" / "plan_setup.py"

    temp_root = Path(tempfile.mkdtemp(prefix="codex-setup-plan-", dir=repo_root))
    try:
        sample_repo = temp_root / "sample_repo"
        sample_repo.mkdir()
        (sample_repo / "environment.yml").write_text("name: demo-env\ndependencies:\n  - python=3.10\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(planner), "--repo", str(sample_repo), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)

        if payload["environment_file"] != "environment.yml":
            raise AssertionError("setup planner failed to detect environment.yml")
        if payload["environment_name"] != "demo-env":
            raise AssertionError("setup planner failed to detect the conda environment name")
        if payload["setup_commands"][0]["command"] != "conda env create -f environment.yml":
            raise AssertionError("setup planner failed to emit the expected conda create command")
        if payload["setup_commands"][1]["command"] != "conda activate demo-env":
            raise AssertionError("setup planner failed to emit the expected conda activate command")

        print("ok: True")
        print("checks: 4")
        print("failures: 0")
        return 0
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


if __name__ == "__main__":
    raise SystemExit(main())
