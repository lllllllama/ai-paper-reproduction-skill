#!/usr/bin/env python3
"""Minimal orchestration for README-first reproduction scaffolding.

This script wires together the repository scan, README command extraction,
optional execution of the selected documented command, and standardized
output generation. It is intentionally conservative and lightweight.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def is_chinese(user_language: str) -> bool:
    return user_language.lower().startswith("zh")


def human_text(en: str, zh: str, user_language: str) -> str:
    return zh if is_chinese(user_language) else en


def run_json(script: Path, args: List[str]) -> Dict[str, Any]:
    """Run a helper script and parse its JSON stdout."""
    command = [sys.executable, str(script), *args]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def command_score(command: Dict[str, Any]) -> int:
    """Score commands so README-first execution prefers runnable entrypoints over setup steps."""
    text = str(command.get("command", "")).lower()
    kind = command.get("kind", "run")
    score = 0

    kind_score = {
        "run": 40,
        "smoke": 30,
        "asset": 10,
        "setup": 0,
    }
    score += kind_score.get(kind, 0)

    if any(token in text for token in ["python ", "python3 ", "./", "whisper "]):
        score += 8
    if any(token in text for token in ["txt2img", "img2img", "amg.py", "transcribe", "infer", "eval"]):
        score += 8
    if "<" in text and ">" in text:
        score -= 10
    if text.startswith(("pip install", "conda install", "conda env create", "conda activate", "git clone", "cd ")):
        score -= 12
    return score


def choose_goal(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Choose the highest-priority documented command."""
    priority = ["inference", "evaluation", "training", "other"]
    for category in priority:
        candidates = [item for item in commands if item.get("category") == category]
        if not candidates:
            continue
        best = max(candidates, key=command_score)
        return {
            "selected_goal": category,
            "goal_priority": category,
            "documented_command": best.get("command", ""),
            "command_source": best.get("source", "readme"),
            "documented_command_kind": best.get("kind", "run"),
            "documented_command_section": best.get("section"),
        }

    return {
        "selected_goal": "repo-intake-only",
        "goal_priority": "other",
        "documented_command": "",
        "command_source": "none",
        "documented_command_kind": "none",
        "documented_command_section": None,
    }


def maybe_run_command(
    repo_path: Path,
    command: str,
    timeout: int,
    user_language: str,
) -> Dict[str, Any]:
    """Optionally execute the selected command in a conservative way."""
    if not command:
        return {
            "status": "not_run",
            "documented_command_status": "not_run",
            "execution_log": [],
            "main_blocker": human_text(
                "No documented command was extracted from README.",
                "未从 README 中提取到已文档化命令。",
                user_language,
            ),
        }

    try:
        result = subprocess.run(
            shlex.split(command, posix=False),
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "status": "blocked",
            "documented_command_status": "blocked",
            "execution_log": [f"Command failed before launch: {exc}"],
            "main_blocker": human_text(
                f"Executable not found for documented command: {exc}",
                f"已文档化命令缺少可执行程序：{exc}",
                user_language,
            ),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "partial",
            "documented_command_status": "partial",
            "execution_log": [f"Command timed out after {timeout} seconds."],
            "main_blocker": human_text(
                f"Selected documented command did not finish within {timeout} seconds.",
                f"选定的已文档化命令未在 {timeout} 秒内完成。",
                user_language,
            ),
        }

    combined = []
    if result.stdout.strip():
        combined.append("STDOUT:\n" + result.stdout.strip())
    if result.stderr.strip():
        combined.append("STDERR:\n" + result.stderr.strip())

    return_code = result.returncode
    if return_code == 0:
        status = "success"
        cmd_status = "success"
        blocker = human_text("None.", "无。", user_language)
    else:
        status = "partial"
        cmd_status = "partial"
        blocker = human_text(
            f"Selected documented command exited with code {return_code}.",
            f"选定的已文档化命令以退出码 {return_code} 结束。",
            user_language,
        )

    return {
        "status": status,
        "documented_command_status": cmd_status,
        "execution_log": combined,
        "main_blocker": blocker,
    }


def build_context(
    repo_path: Path,
    scan_data: Dict[str, Any],
    command_data: Dict[str, Any],
    run_data: Dict[str, Any],
    user_language: str,
    run_selected: bool,
) -> Dict[str, Any]:
    """Build a single context object for output generation."""
    chosen = choose_goal(command_data.get("commands", []))
    status = run_data["status"] if run_selected else "not_run"
    documented_status = (
        run_data["documented_command_status"]
        if run_selected
        else ("not_run" if not chosen["documented_command"] else "documented")
    )

    structure = scan_data.get("structure", {})
    notes = []
    notes.extend(scan_data.get("warnings", []))
    notes.extend(command_data.get("warnings", []))
    notes.extend(run_data.get("execution_log", []))

    result_summary = (
        human_text(
            f"Selected goal `{chosen['selected_goal']}` from README evidence.",
            f"已根据 README 证据选择目标 `{chosen['selected_goal']}`。",
            user_language,
        )
        if chosen["documented_command"]
        else human_text(
            "No documented runnable command was extracted. Repo intake was completed.",
            "未提取到可运行的已文档化命令。仓库 intake 已完成。",
            user_language,
        )
    )

    if run_selected and status == "success":
        result_summary = human_text(
            "Selected documented command finished successfully.",
            "选定的已文档化命令已成功完成。",
            user_language,
        )
    elif run_selected and status == "partial":
        result_summary = human_text(
            "Selected documented command started but did not complete cleanly.",
            "选定的已文档化命令已启动，但未干净完成。",
            user_language,
        )
    elif run_selected and status == "blocked":
        result_summary = human_text(
            "Selected documented command could not be launched.",
            "选定的已文档化命令无法启动。",
            user_language,
        )

    section = chosen.get("documented_command_section")
    command_notes = [
        human_text(
            f"README path: {scan_data.get('readme_path') or 'not found'}",
            f"README 路径：{scan_data.get('readme_path') or 'not found'}",
            user_language,
        ),
        human_text(
            f"Detected top-level entries: {', '.join(structure.get('top_level', [])) or 'none'}",
            f"检测到的顶层条目：{', '.join(structure.get('top_level', [])) or 'none'}",
            user_language,
        ),
    ]
    if chosen["documented_command"]:
        command_notes.append(
            human_text(
                f"Main run label: documented from README ({chosen.get('command_source', 'readme')})"
                + (f", section `{section}`" if section else ""),
                f"主运行标签：来自 README 的 documented（{chosen.get('command_source', 'readme')}）"
                + (f"，章节 `{section}`" if section else ""),
                user_language,
            )
        )

    return {
        "schema_version": "1.0",
        "generated_at": scan_data.get("generated_at"),
        "user_language": user_language,
        "target_repo": str(repo_path.resolve()),
        "readme_first": True,
        "selected_goal": chosen["selected_goal"],
        "goal_priority": chosen["goal_priority"],
        "status": status,
        "documented_command_status": documented_status,
        "documented_command": chosen["documented_command"] or "None extracted",
        "documented_command_kind": chosen.get("documented_command_kind", "none"),
        "documented_command_source": chosen.get("command_source", "none"),
        "documented_command_section": chosen.get("documented_command_section"),
        "result_summary": result_summary,
        "main_blocker": run_data.get(
            "main_blocker",
            human_text("No blocker recorded.", "未记录阻塞项。", user_language),
        ),
        "next_action": (
            human_text(
                "Prepare environment and assets, then retry the documented command.",
                "先准备环境与资源，再重试该已文档化命令。",
                user_language,
            )
            if status in {"partial", "blocked", "not_run"}
            else human_text(
                "Review outputs and continue with the next documented verification step.",
                "检查输出后继续下一步已文档化验证。",
                user_language,
            )
        ),
        "setup_commands": [
            {"label": "adapted", "command": "conda env create -f environment.yml"},
            {"label": "adapted", "command": "conda activate <env-name>"},
        ],
        "asset_commands": [
            {
                "label": "inferred",
                "command": "# Add README-documented dataset and checkpoint preparation commands here.",
            },
        ],
        "run_commands": (
            [{"label": "documented", "command": chosen["documented_command"]}]
            if chosen["documented_command"]
            else []
        ),
        "verification_commands": [
            {
                "label": "inferred",
                "command": "# Add metric check, artifact check, or smoke verification command here.",
            },
        ],
        "command_notes": command_notes,
        "timeline": [
            human_text(
                "Scanned repository structure and key metadata files.",
                "已扫描仓库结构和关键元数据文件。",
                user_language,
            ),
            human_text(
                "Extracted README code blocks and shell-like commands.",
                "已提取 README 中的代码块和 shell 风格命令。",
                user_language,
            ),
            human_text(
                f"Selected `{chosen['selected_goal']}` as the smallest trustworthy target.",
                f"已将 `{chosen['selected_goal']}` 选为最小可信目标。",
                user_language,
            ),
            human_text(
                "Execution step was skipped." if not run_selected else "Attempted the selected documented command.",
                "已跳过执行步骤。" if not run_selected else "已尝试选定的已文档化命令。",
                user_language,
            ),
        ],
        "assumptions": [
            human_text(
                "README remains the primary source of truth.",
                "README 仍是主要事实来源。",
                user_language,
            ),
            human_text(
                "Environment creation should prefer conda-style isolation.",
                "环境创建应优先采用 conda 式隔离。",
                user_language,
            ),
        ],
        "evidence": [
            human_text(
                f"Detected files: {', '.join(scan_data.get('detected_files', [])) or 'none'}",
                f"检测到的文件：{', '.join(scan_data.get('detected_files', [])) or 'none'}",
                user_language,
            ),
            human_text(
                f"Command categories: {json.dumps(command_data.get('counts', {}), ensure_ascii=False)}",
                f"命令分类：{json.dumps(command_data.get('counts', {}), ensure_ascii=False)}",
                user_language,
            ),
            human_text(
                f"Selected command kind: {chosen.get('documented_command_kind', 'none')}",
                f"已选命令类型：{chosen.get('documented_command_kind', 'none')}",
                user_language,
            ),
        ],
        "blockers": [
            run_data.get("main_blocker", human_text("None.", "无。", user_language))
        ],
        "notes": notes,
        "patches_applied": False,
        "patch_branch": "",
        "verified_commits": [],
        "validation_summary": "",
        "patch_notes": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal README-first reproduction orchestration.")
    parser.add_argument("--repo", required=True, help="Path to the target repository.")
    parser.add_argument(
        "--output-dir",
        default="repro_outputs",
        help="Directory to write the standardized outputs into.",
    )
    parser.add_argument(
        "--user-language",
        default="en",
        help="Language tag for human-readable reports.",
    )
    parser.add_argument(
        "--run-selected",
        action="store_true",
        help="Execute the first selected documented command.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Execution timeout in seconds for --run-selected.",
    )
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    base_dir = Path(__file__).resolve().parents[2]
    scan_script = base_dir / "repo-intake-and-plan" / "scripts" / "scan_repo.py"
    extract_script = base_dir / "repo-intake-and-plan" / "scripts" / "extract_commands.py"
    write_script = base_dir / "minimal-run-and-audit" / "scripts" / "write_outputs.py"

    scan_data = run_json(scan_script, ["--repo", str(repo_path), "--json"])
    readme_path = scan_data.get("readme_path")
    command_data = {"commands": [], "counts": {}, "warnings": []}
    if readme_path:
        command_data = run_json(extract_script, ["--readme", readme_path, "--json"])

    chosen = choose_goal(command_data.get("commands", []))
    run_data = {
        "status": "not_run",
        "documented_command_status": "not_run",
        "execution_log": [],
        "main_blocker": human_text(
            "Execution was not requested.",
            "未请求执行。",
            args.user_language,
        ),
    }
    if args.run_selected:
        run_data = maybe_run_command(repo_path, chosen["documented_command"], args.timeout, args.user_language)

    context = build_context(
        repo_path=repo_path,
        scan_data=scan_data,
        command_data=command_data,
        run_data=run_data,
        user_language=args.user_language,
        run_selected=args.run_selected,
    )

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    context_path = output_dir / ".repro_context.json"
    context_path.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(write_script),
            "--context-json",
            str(context_path),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
    )

    print(json.dumps(context, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
