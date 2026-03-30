#!/usr/bin/env python3
"""Write standardized reproduction outputs from a context JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def is_chinese(user_language: str) -> bool:
    return user_language.lower().startswith("zh")


def tr(user_language: str, en: str, zh: str) -> str:
    return zh if is_chinese(user_language) else en


def bullets(items: Iterable[str], user_language: str = "en") -> str:
    values = [item for item in items if item]
    if not values:
        return f"- {tr(user_language, 'None.', '无。')}"
    return "\n".join(f"- {item}" for item in values)


def command_block(items: Iterable[Any], user_language: str) -> str:
    values = [item for item in items if item]
    if not values:
        return tr(user_language, "# No command recorded.", "# 未记录命令。")

    rendered: List[str] = []
    for item in values:
        if isinstance(item, dict):
            label = item.get("label", "inferred")
            command = item.get("command", "")
            rendered.append(f"# [{label}]")
            rendered.append(str(command))
        else:
            rendered.append(str(item))
    return "\n".join(rendered)


def load_context(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_summary(output_dir: Path, context: Dict[str, Any]) -> None:
    user_language = context.get("user_language", "en")
    lines = [
        tr(user_language, "# Reproduction Summary", "# 复现摘要"),
        "",
        f"- {tr(user_language, 'Target repo', '目标仓库')}: `{context['target_repo']}`",
        f"- {tr(user_language, 'Selected goal', '已选目标')}: `{context['selected_goal']}`",
        f"- {tr(user_language, 'Goal priority', '目标优先级')}: `{context['goal_priority']}`",
        f"- {tr(user_language, 'Overall status', '整体状态')}: `{context['status']}`",
        f"- README-first: `{context['readme_first']}`",
        f"- {tr(user_language, 'Main documented command', '主要已文档化命令')}: `{context['documented_command']}`",
        "",
        tr(user_language, "## Result", "## 结果"),
        "",
        context["result_summary"],
        "",
        tr(user_language, "## Main blocker", "## 主要阻塞"),
        "",
        context["main_blocker"],
        "",
        tr(user_language, "## Next action", "## 下一步"),
        "",
        context["next_action"],
        "",
    ]
    (output_dir / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def write_commands(output_dir: Path, context: Dict[str, Any]) -> None:
    user_language = context.get("user_language", "en")
    lines = [
        tr(user_language, "# Commands", "# 命令"),
        "",
        tr(user_language, "## Setup", "## 环境准备"),
        "",
        "```bash",
        command_block(context.get("setup_commands", []), user_language),
        "```",
        "",
        tr(user_language, "## Assets", "## 资源"),
        "",
        "```bash",
        command_block(context.get("asset_commands", []), user_language),
        "```",
        "",
        tr(user_language, "## Main run", "## 主运行命令"),
        "",
        "```bash",
        command_block(context.get("run_commands", []), user_language),
        "```",
        "",
        tr(user_language, "## Verification", "## 验证"),
        "",
        "```bash",
        command_block(context.get("verification_commands", []), user_language),
        "```",
        "",
        tr(user_language, "## Notes", "## 说明"),
        "",
        bullets(context.get("command_notes", []), user_language),
        "",
    ]
    (output_dir / "COMMANDS.md").write_text("\n".join(lines), encoding="utf-8")


def write_log(output_dir: Path, context: Dict[str, Any]) -> None:
    user_language = context.get("user_language", "en")
    lines = [
        tr(user_language, "# Reproduction Log", "# 复现日志"),
        "",
        tr(user_language, "## Context", "## 上下文"),
        "",
        f"- {tr(user_language, 'Target repo', '目标仓库')}: `{context['target_repo']}`",
        f"- {tr(user_language, 'Selected goal', '已选目标')}: `{context['selected_goal']}`",
        f"- {tr(user_language, 'User language', '用户语言')}: `{context['user_language']}`",
        "",
        tr(user_language, "## Timeline", "## 时间线"),
        "",
        bullets(context.get("timeline", []), user_language),
        "",
        tr(user_language, "## Assumptions", "## 假设"),
        "",
        bullets(context.get("assumptions", []), user_language),
        "",
        tr(user_language, "## Evidence", "## 证据"),
        "",
        bullets(context.get("evidence", []), user_language),
        "",
        tr(user_language, "## Failures or blockers", "## 失败或阻塞"),
        "",
        bullets(context.get("blockers", []), user_language),
        "",
    ]
    (output_dir / "LOG.md").write_text("\n".join(lines), encoding="utf-8")


def write_status(output_dir: Path, context: Dict[str, Any]) -> None:
    payload = {
        "schema_version": context.get("schema_version", "1.0"),
        "generated_at": context.get("generated_at"),
        "user_language": context.get("user_language", "en"),
        "target_repo": context.get("target_repo"),
        "readme_first": context.get("readme_first", True),
        "selected_goal": context.get("selected_goal", "unknown"),
        "goal_priority": context.get("goal_priority", "other"),
        "status": context.get("status", "not_run"),
        "documented_command_status": context.get("documented_command_status", "not_run"),
        "patches_applied": context.get("patches_applied", False),
        "outputs": {
            "summary": "repro_outputs/SUMMARY.md",
            "commands": "repro_outputs/COMMANDS.md",
            "log": "repro_outputs/LOG.md",
            "status": "repro_outputs/status.json",
            "patches": "repro_outputs/PATCHES.md" if context.get("patches_applied") else None,
        },
        "notes": context.get("notes", []),
    }
    (output_dir / "status.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_patches(output_dir: Path, context: Dict[str, Any]) -> None:
    if not context.get("patches_applied"):
        return
    user_language = context.get("user_language", "en")

    commit_lines: List[str] = []
    for item in context.get("verified_commits", []):
        commit_lines.append(
            f"- `{item.get('commit', 'unknown')}`: {item.get('summary', 'No summary provided.')}"
        )

    lines = [
        tr(user_language, "# Patch Record", "# Patch 记录"),
        "",
        f"- {tr(user_language, 'Patch branch', 'Patch 分支')}: `{context.get('patch_branch', '')}`",
        f"- {tr(user_language, 'README fidelity impact', 'README 忠实度影响')}: `{context.get('readme_fidelity', 'preserved')}`",
        "",
        tr(user_language, "## Verified commits", "## 已验证提交"),
        "",
        "\n".join(commit_lines) if commit_lines else f"- {tr(user_language, 'None.', '无。')}",
        "",
        tr(user_language, "## Validation summary", "## 验证摘要"),
        "",
        context.get(
            "validation_summary",
            tr(user_language, "No validation summary recorded.", "未记录验证摘要。"),
        ),
        "",
        tr(user_language, "## Notes", "## 说明"),
        "",
        bullets(context.get("patch_notes", []), user_language),
        "",
    ]
    (output_dir / "PATCHES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Write standardized reproduction outputs.")
    parser.add_argument("--context-json", required=True, help="Path to a context JSON file.")
    parser.add_argument(
        "--output-dir",
        default="repro_outputs",
        help="Directory where output files will be written.",
    )
    args = parser.parse_args()

    context = load_context(Path(args.context_json).resolve())
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    write_summary(output_dir, context)
    write_commands(output_dir, context)
    write_log(output_dir, context)
    write_status(output_dir, context)
    write_patches(output_dir, context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
