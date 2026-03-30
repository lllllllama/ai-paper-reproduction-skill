#!/usr/bin/env python3
"""Run lightweight trigger boundary and negative-case checks for the skill set.

This script does not emulate Codex's exact trigger mechanism. Instead, it provides
an auditable local test harness that checks whether skill descriptions are narrow
enough to separate positive, boundary, and negative prompts with a simple lexical
router. If the simple router shows overlap, the front matter likely needs tightening.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.IGNORECASE)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "do", "for", "from",
    "if", "in", "into", "is", "it", "of", "on", "only", "or", "that", "the", "this",
    "to", "use", "user", "when", "with", "without", "not", "main", "skill", "sub",
    "repo", "repository", "ai", "paper", "README-first".lower(),
}
HIGH_SIGNAL_TOKENS = {
    "repro_outputs", "documented", "inference", "evaluation", "training", "scan",
    "extract", "commands", "classify", "conda", "checkpoint", "dataset", "cache",
    "smoke", "execute", "run", "audit", "summary", "protocol", "split", "readme",
}
SKILL_NAME_BOOST = 100.0


@dataclass
class SkillInfo:
    name: str
    description: str


def parse_front_matter(skill_md: Path) -> Dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{skill_md} is missing YAML front matter.")
    _, front_matter, _ = text.split("---", 2)
    data: Dict[str, str] = {}
    for raw_line in front_matter.splitlines():
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def normalize_tokens(text: str) -> List[str]:
    raw = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in raw if token not in STOPWORDS and len(token) > 2]


def score_prompt(prompt: str, skill: SkillInfo) -> float:
    prompt_tokens = normalize_tokens(prompt)
    description_tokens = normalize_tokens(skill.description)
    if not prompt_tokens or not description_tokens:
        return 0.0

    prompt_text = prompt.lower()
    if skill.name in prompt_text:
        return SKILL_NAME_BOOST

    desc_set = set(description_tokens)
    overlap = 0.0
    for token in prompt_tokens:
        if token in desc_set:
            overlap += 2.0 if token in HIGH_SIGNAL_TOKENS else 1.0

    bigrams = set(zip(prompt_tokens, prompt_tokens[1:]))
    skill_bigrams = set(zip(description_tokens, description_tokens[1:]))
    overlap += 1.5 * len(bigrams & skill_bigrams)

    exclusion_penalty = 0.0
    if "do not use for" in skill.description.lower():
        exclusion_text = skill.description.lower().split("do not use for", 1)[1]
        exclusion_tokens = set(normalize_tokens(exclusion_text))
        for token in prompt_tokens:
            if token in exclusion_tokens:
                exclusion_penalty += 1.0
    if "do not use" in skill.description.lower() and any(word in prompt_text for word in ["summary", "novelty", "related work"]):
        if skill.name in {"ai-paper-reproduction", "paper-context-resolver"}:
            exclusion_penalty += 2.0

    gated = apply_skill_gates(skill.name, prompt_text, overlap - exclusion_penalty)
    return max(gated, 0.0)


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def apply_skill_gates(skill_name: str, prompt_text: str, base_score: float) -> float:
    """Apply skill-specific routing gates to reduce false overlap."""
    if base_score <= 0:
        return 0.0

    has_repo_context = contains_any(prompt_text, ["repo", "repository", "readme", "仓库", "复现"])
    asks_scan = contains_any(prompt_text, ["scan", "read the readme", "extract documented", "classify", "tell me the documented", "do not run", "不要运行", "先读"])
    asks_setup = contains_any(prompt_text, ["conda", "environment", "env ", "checkpoint", "dataset", "cache", "asset", "before any run", "before we execute"])
    asks_run = contains_any(prompt_text, ["run ", "execute", "smoke", "write summary.md", "write standardized outputs", "输出 repro_outputs", "运行"])
    forbids_run = contains_any(prompt_text, ["do not run", "don't run", "before we execute anything", "不要运行", "不要执行"])
    asks_paper_gap = contains_any(prompt_text, ["linked paper", "paper", "arxiv", "openreview", "README is missing", "README is ambiguous", "gap", "conflict", "论文", "缺少", "歧义"])
    negates_summary = contains_any(prompt_text, ["do not summarize", "don't summarize", "not summarize", "不要总结"])
    asks_general_paper_summary = (not negates_summary) and contains_any(prompt_text, ["summarize", "novelty", "related work", "overview", "总结论文", "相关工作"])

    if skill_name == "ai-paper-reproduction":
        if not has_repo_context:
            return 0.0
        if contains_any(prompt_text, ["reproduce", "reproduction", "复现", "end-to-end", "orchestrate"]):
            base_score += 6.0
        if asks_paper_gap and not asks_run and "repro_outputs" not in prompt_text and not contains_any(prompt_text, ["reproduce", "reproduction", "复现", "orchestrate", "end-to-end"]):
            base_score -= 7.0
        if asks_scan and not asks_run and not asks_setup and "repro_outputs" not in prompt_text:
            base_score -= 4.0
        if asks_general_paper_summary:
            base_score = 0.0
        return base_score

    if skill_name == "repo-intake-and-plan":
        if not (has_repo_context and asks_scan):
            return 0.0 if base_score < 3 else base_score - 3.0
        if asks_run and not forbids_run:
            base_score -= 3.0
        if asks_setup and not asks_scan:
            base_score -= 3.0
        if asks_general_paper_summary:
            base_score = 0.0
        return base_score

    if skill_name == "env-and-assets-bootstrap":
        setup_anchor = contains_any(prompt_text, ["conda", "environment", "env ", "asset plan", "setup", "prepare", "before any run", "before we execute"])
        if not has_repo_context:
            return 0.0
        if not asks_setup or not setup_anchor:
            return 0.0 if base_score < 3 else base_score - 3.0
        if contains_any(prompt_text, ["environment", "conda", "checkpoint", "dataset", "cache", "asset"]):
            base_score += 4.0
        if asks_paper_gap and not contains_any(prompt_text, ["conda", "environment", "cache", "asset plan", "setup", "prepare"]):
            base_score -= 4.0
        if asks_run:
            base_score -= 2.0
        return base_score

    if skill_name == "minimal-run-and-audit":
        if forbids_run:
            return 0.0
        if not asks_run:
            return 0.0 if base_score < 3 else base_score - 3.0
        if asks_scan and not asks_run:
            base_score = 0.0
        return base_score + 3.0

    if skill_name == "paper-context-resolver":
        narrow_detail = contains_any(prompt_text, ["split", "protocol", "preprocessing", "checkpoint", "runtime assumption", "evaluation", "dataset version", "数据集", "评测"])
        if asks_general_paper_summary:
            return 0.0
        if not (asks_paper_gap and narrow_detail):
            return 0.0 if base_score < 4 else base_score - 4.0
        if asks_setup and not asks_paper_gap:
            base_score -= 4.0
        return base_score + 4.0

    return base_score


def explicitly_named_skills(prompt: str, skills: Iterable[SkillInfo]) -> List[str]:
    prompt_text = prompt.lower()
    return [skill.name for skill in skills if skill.name in prompt_text]


def load_skills(repo_root: Path) -> List[SkillInfo]:
    skills: List[SkillInfo] = []
    skills_root = repo_root / "skills"
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_front_matter(skill_md)
        skills.append(SkillInfo(name=fm["name"], description=fm["description"]))
    return skills


def rank_skills(prompt: str, skills: Iterable[SkillInfo]) -> List[Tuple[str, float]]:
    ranked = [(skill.name, score_prompt(prompt, skill)) for skill in skills]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return ranked


def evaluate_case(case: Dict[str, object], skills: List[SkillInfo], threshold: float) -> Dict[str, object]:
    prompt = str(case["prompt"])
    ranked = rank_skills(prompt, skills)
    named = explicitly_named_skills(prompt, skills)
    triggered = [name for name, score in ranked if score >= threshold]
    if named:
        triggered = [name for name in triggered if name in named]
    expected_any = list(case.get("expected_any", []))
    forbidden = set(case.get("forbidden", []))
    expected_top = case.get("expected_top")

    failures: List[str] = []
    if expected_any:
        if not any(name in triggered for name in expected_any):
            failures.append(f"Expected one of {expected_any}, got {triggered or 'none'}")
    else:
        if triggered:
            failures.append(f"Expected no trigger, got {triggered}")

    if expected_top is not None:
        top_name = ranked[0][0] if ranked else None
        if top_name != expected_top:
            failures.append(f"Expected top skill `{expected_top}`, got `{top_name}`")

    forbidden_hits = [name for name in triggered if name in forbidden]
    if forbidden_hits:
        failures.append(f"Forbidden skills triggered: {forbidden_hits}")

    return {
        "id": case["id"],
        "type": case["type"],
        "ok": not failures,
        "triggered": triggered,
        "ranked": ranked,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run boundary and negative trigger tests for skills.")
    parser.add_argument(
        "--cases",
        default="tests/trigger_cases.json",
        help="Path to the trigger case JSON file.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        help="Score threshold required to count as triggered.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    skills = load_skills(repo_root)
    case_payload = json.loads((repo_root / args.cases).read_text(encoding="utf-8"))
    results = [evaluate_case(case, skills, args.threshold) for case in case_payload["cases"]]
    failures = [item for item in results if not item["ok"]]

    payload = {
        "ok": not failures,
        "threshold": args.threshold,
        "skill_count": len(skills),
        "case_count": len(results),
        "failures": failures,
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"ok: {payload['ok']}")
        print(f"cases: {payload['case_count']}")
        print(f"failures: {len(failures)}")
        for result in results:
            status = "PASS" if result["ok"] else "FAIL"
            print(f"{status}: {result['id']} -> {result['triggered']}")
            if not result["ok"]:
                for failure in result["failures"]:
                    print(f"  - {failure}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
