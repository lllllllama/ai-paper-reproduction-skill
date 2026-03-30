---
name: minimal-run-and-audit
description: Sub-skill for the execution and reporting phase of README-first AI repo reproduction. Use when the task is specifically to run the selected smoke test or documented inference or evaluation command, capture evidence, and write standardized `repro_outputs/` files including patch notes when repository files changed. Do not use for initial repo intake, generic environment setup, paper lookup, or end-to-end orchestration by itself.
---

# minimal-run-and-audit

## When to apply

- After a reproduction target and setup plan exist.
- When the main skill needs execution evidence and normalized outputs.
- When a smoke test, documented inference run, documented evaluation run, or training startup verification is appropriate.

## When not to apply

- During initial repo scanning.
- When environment or assets are still undefined enough to make execution meaningless.
- When the task is a literature lookup rather than repository execution.

## Clear boundaries

- This skill executes and reports.
- It does not choose the overall target on its own.
- It does not perform broad paper analysis.
- It should not normalize risky code edits into acceptable practice.

## Input expectations

- selected reproduction goal
- runnable commands or smoke commands
- environment and asset assumptions
- optional patch metadata

## Output expectations

- execution result summary
- standardized `repro_outputs/` files
- clear distinction between verified, partial, and blocked states
- `PATCHES.md` when repo files changed

## Notes

Use `references/reporting-policy.md` and `scripts/write_outputs.py`.
