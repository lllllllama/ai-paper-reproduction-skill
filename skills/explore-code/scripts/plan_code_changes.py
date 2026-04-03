#!/usr/bin/env python3
"""Build a conservative exploratory code-change plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


SKIP_PARTS = {
    "__pycache__",
    ".git",
    "repro_outputs",
    "train_outputs",
    "analysis_outputs",
    "debug_outputs",
    "explore_outputs",
    "tmp",
}

CODE_SUFFIXES = {".py", ".yaml", ".yml", ".json", ".toml", ".ini"}
MODEL_PATTERN = re.compile(r"(model|network|backbone|encoder|decoder|adapter|lora|head|loss)", re.IGNORECASE)
TRAIN_PATTERN = re.compile(r"(train|trainer|optim|loss|config)", re.IGNORECASE)
TASK_KEYWORDS = {
    "classification": ("class", "imagenet", "knn", "linear", "log_regression"),
    "segmentation": ("seg", "segment", "mask", "ade20k", "m2f", "mask2former"),
    "detection": ("det", "detect", "detr", "coco", "box"),
    "depth": ("depth", "nyu", "dpt", "depther"),
    "text": ("text", "token", "clip", "dinotxt"),
    "pretrain": ("pretrain", "ssl", "teacher", "student", "gram", "distillation"),
}
COMMON_TOKENS = {"py", "yaml", "yml", "json", "toml", "ini", "run", "train", "eval", "config", "configs"}


def load_variant_spec(path: str) -> Dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).resolve().read_text(encoding="utf-8-sig"))


def normalize_task_family(value: Any) -> str:
    return str(value or "").strip().lower()


def focus_tokens(current_research: str, task_family: str) -> List[str]:
    tokens: List[str] = []
    for part in re.split(r"[^a-zA-Z0-9]+", current_research.lower()):
        if part and part not in COMMON_TOKENS and len(part) > 2:
            tokens.append(part)
    if task_family:
        tokens.append(task_family)
        tokens.extend(TASK_KEYWORDS.get(task_family, ()))
    ordered: List[str] = []
    for token in tokens:
        if token not in ordered:
            ordered.append(token)
    return ordered[:20]


def score_path(rel: str, task_family: str, tokens: List[str]) -> int:
    score = 0
    if MODEL_PATTERN.search(rel):
        score += 5
    if TRAIN_PATTERN.search(rel):
        score += 3
    if rel.endswith(".py"):
        score += 1
    lower = rel.lower()
    for token in TASK_KEYWORDS.get(task_family, ()):
        if token in lower:
            score += 4
    for token in tokens:
        if token in lower:
            score += 2
    if current_research_dir(rel, tokens):
        score += 3
    return score


def current_research_dir(rel: str, tokens: List[str]) -> bool:
    lower = rel.lower()
    slash_hits = [token for token in tokens if token in lower]
    return len(slash_hits) >= 2


def collect_candidate_edit_targets(repo: Path, current_research: str, task_family: str) -> List[str]:
    tokens = focus_tokens(current_research, task_family)
    scored: List[tuple[int, str]] = []
    for path in repo.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in CODE_SUFFIXES:
            continue
        rel = path.relative_to(repo).as_posix()
        score = score_path(rel, task_family, tokens)
        if score:
            scored.append((score, rel))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [rel for _, rel in scored[:8]]


def build_code_tracks(spec: Dict[str, Any], targets: List[str], task_family: str, current_research: str) -> List[str]:
    tracks: List[str] = []
    if task_family:
        tracks.append(f"Stay anchored to the `{task_family}` task family while planning exploratory edits.")
    tracks.append(f"Preserve `{current_research}` as the comparison anchor for all code changes.")

    for axis, values in sorted(spec.get("variant_axes", {}).items()):
        shown_values = ", ".join(str(value) for value in values[:3])
        tracks.append(f"Review code touchpoints for `{axis}` variation across: {shown_values}.")

    if targets:
        tracks.append(f"Inspect candidate model files first: {', '.join(targets[:3])}.")

    if spec.get("base_command"):
        tracks.append(f"Keep `{spec['base_command']}` aligned with any exploratory code path changes.")

    tracks.extend(
        [
            "Prefer one reversible module-level adaptation before broader rewrites.",
            "Keep config and entrypoint changes coupled so candidate runs remain attributable.",
        ]
    )
    return tracks[:6]


def build_payload(repo: Path, current_research: str, experiment_branch: str, spec: Dict[str, Any], task_family: str) -> Dict[str, Any]:
    candidate_targets = collect_candidate_edit_targets(repo, current_research, task_family)
    code_tracks = build_code_tracks(spec, candidate_targets, task_family, current_research)
    return {
        "schema_version": "1.0",
        "repo": str(repo.resolve()),
        "current_research": current_research,
        "task_family": task_family or None,
        "experiment_branch": experiment_branch,
        "candidate_edit_targets": candidate_targets,
        "proposed_code_tracks": code_tracks,
        "source_repo_refs": [
            {
                "repo": repo.name,
                "ref": current_research,
                "note": "current_research anchor for exploratory code changes",
            }
        ],
        "notes": [
            "Exploratory code plan only; candidate-level changes should stay isolated from the trusted baseline.",
            "Inspect candidate model files before introducing adapter or head changes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a conservative exploratory code-change plan.")
    parser.add_argument("--repo", required=True, help="Path to the target repository.")
    parser.add_argument("--current-research", required=True, help="Durable identifier for the current research context.")
    parser.add_argument("--experiment-branch", required=True, help="Isolated experiment branch label.")
    parser.add_argument("--variant-spec-json", default="", help="Optional path to the variant-spec JSON file.")
    parser.add_argument("--task-family", default="", help="Optional task-family hint used to focus candidate edit targets.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    payload = build_payload(
        repo,
        args.current_research,
        args.experiment_branch,
        load_variant_spec(args.variant_spec_json),
        normalize_task_family(args.task_family),
    )
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Current research: {payload['current_research']}")
        print(f"Task family: {payload.get('task_family') or 'unspecified'}")
        print(f"Experiment branch: {payload['experiment_branch']}")
        print("Candidate edit targets:", ", ".join(payload["candidate_edit_targets"]) or "none")
        print("Proposed code tracks:")
        for line in payload["proposed_code_tracks"]:
            print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
