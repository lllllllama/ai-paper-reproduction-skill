#!/usr/bin/env python3
"""Create a conservative environment setup plan for a research repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


ENV_FILES = [
    "environment.yml",
    "environment.yaml",
    "conda.yml",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
]


def find_first(repo: Path, candidates: List[str]) -> Optional[Path]:
    for name in candidates:
        path = repo / name
        if path.exists():
            return path
    return None


def parse_env_name(path: Path) -> Optional[str]:
    if path.suffix not in {".yml", ".yaml"}:
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^\s*name:\s*([A-Za-z0-9._-]+)\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def build_setup_commands(repo: Path) -> Dict[str, object]:
    setup_commands: List[Dict[str, str]] = []
    notes: List[str] = []
    unresolved: List[str] = []

    env_file = find_first(repo, ENV_FILES)
    env_name = parse_env_name(env_file) if env_file else None

    if env_file is None:
        unresolved.append("No top-level environment specification file was found.")
        setup_commands.extend(
            [
                {"label": "inferred", "command": "python -m venv .venv"},
                {"label": "inferred", "command": ". .venv/Scripts/activate"},
            ]
        )
        notes.append("Defaulted to a virtualenv fallback because no environment file was detected.")
        return {
            "environment_file": None,
            "environment_name": None,
            "setup_commands": setup_commands,
            "setup_notes": notes,
            "unresolved_setup_risks": unresolved,
        }

    rel_env_file = env_file.relative_to(repo).as_posix()
    notes.append(f"Detected environment file `{rel_env_file}`.")
    if env_name:
        notes.append(f"Detected conda environment name `{env_name}`.")

    if env_file.name in {"environment.yml", "environment.yaml", "conda.yml"}:
        setup_commands.append({"label": "documented", "command": f"conda env create -f {rel_env_file}"})
        setup_commands.append(
            {
                "label": "adapted",
                "command": f"conda activate {env_name}" if env_name else "conda activate <env-name>",
            }
        )
        if not env_name:
            unresolved.append("The conda environment name was not declared and still needs confirmation.")
    elif env_file.name == "requirements.txt":
        setup_commands.extend(
            [
                {"label": "adapted", "command": "python -m venv .venv"},
                {"label": "adapted", "command": ". .venv/Scripts/activate"},
                {"label": "documented", "command": f"python -m pip install -r {rel_env_file}"},
            ]
        )
        notes.append("Fell back to a virtualenv plus requirements installation plan.")
    elif env_file.name == "pyproject.toml":
        setup_commands.extend(
            [
                {"label": "adapted", "command": "python -m venv .venv"},
                {"label": "adapted", "command": ". .venv/Scripts/activate"},
                {"label": "documented", "command": "python -m pip install -e ."},
            ]
        )
        notes.append("Detected a pyproject-based installation flow.")
    elif env_file.name == "setup.py":
        setup_commands.extend(
            [
                {"label": "adapted", "command": "python -m venv .venv"},
                {"label": "adapted", "command": ". .venv/Scripts/activate"},
                {"label": "documented", "command": "python -m pip install -e ."},
            ]
        )
        notes.append("Detected a setup.py-based editable install flow.")

    return {
        "environment_file": rel_env_file,
        "environment_name": env_name,
        "setup_commands": setup_commands,
        "setup_notes": notes,
        "unresolved_setup_risks": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a conservative environment setup plan.")
    parser.add_argument("--repo", required=True, help="Path to the target repository.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    payload = build_setup_commands(repo)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
