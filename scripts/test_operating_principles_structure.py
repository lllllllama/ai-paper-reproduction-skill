#!/usr/bin/env python3
"""Check shared operating-principle wiring and main skill concision."""

from __future__ import annotations

import json
from pathlib import Path


PUBLIC_PRINCIPLES_REF = "../../references/agent-operating-principles.md"
MAIN_SKILL_LIMITS = {
    "ai-research-reproduction": 130,
    "ai-research-explore": 125,
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    registry = json.loads((repo_root / "references" / "skill-registry.json").read_text(encoding="utf-8"))
    public_names = [item["name"] for item in registry["skills"] if item.get("tier") == "public"]

    failures: list[str] = []

    principles = (repo_root / "references" / "agent-operating-principles.md").read_text(encoding="utf-8")
    for phrase in [
        "Think before acting",
        "Keep the solution small",
        "Change only what is necessary",
        "Work toward verifiable goals",
        "Apply freedom at the right level",
    ]:
        if phrase not in principles:
            failures.append(f"agent-operating-principles.md missing `{phrase}`")

    for name in public_names:
        skill_text = (repo_root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        if PUBLIC_PRINCIPLES_REF not in skill_text:
            failures.append(f"{name} does not link to the shared operating principles")

    for name, limit in MAIN_SKILL_LIMITS.items():
        skill_text = (repo_root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        line_count = len(skill_text.splitlines())
        if line_count > limit:
            failures.append(f"{name} has {line_count} lines, expected <= {limit}")

    explore_text = (repo_root / "skills" / "ai-research-explore" / "SKILL.md").read_text(encoding="utf-8")
    for overfit_heading in ["## Variant Spec Hints", "## Ranking Semantics"]:
        if overfit_heading in explore_text:
            failures.append(f"ai-research-explore should not expose `{overfit_heading}` in the entrypoint")

    campaign_text = (
        repo_root / "skills" / "ai-research-explore" / "references" / "research-campaign-spec.md"
    ).read_text(encoding="utf-8")
    for phrase in ["advanced reference", "Durable Core Fields", "Optional Guidance Fields"]:
        if phrase not in campaign_text:
            failures.append(f"research-campaign-spec.md missing `{phrase}`")
    if "not fields the agent must invent on every run" not in campaign_text:
        failures.append("research_campaign optional fields are not clearly downgraded from required")

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    if "Lifecycle View" not in readme or "agent-operating-principles.md" not in readme:
        failures.append("README.md must describe lifecycle routing and shared principles")

    print(f"ok: {not failures}")
    print(f"public_skills: {len(public_names)}")
    print(f"failures: {len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

