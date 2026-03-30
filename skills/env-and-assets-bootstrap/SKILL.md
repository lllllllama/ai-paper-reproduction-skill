---
name: env-and-assets-bootstrap
description: Prepare a conservative conda-first environment and asset layout for AI repo reproduction by reading README-first evidence, resolving checkpoints and dataset paths, and avoiding unsafe or speculative setup steps.
---

# env-and-assets-bootstrap

## When to apply

- After repo intake identifies a credible reproduction target.
- When environment creation or asset path preparation is needed before running commands.
- When the repo depends on checkpoints, datasets, or cache directories.

## When not to apply

- When the repository already ships a ready-to-run environment that does not need translation.
- When the task is only to scan and plan.
- When the task is only to report results from commands that already ran.

## Clear boundaries

- This skill prepares environment and asset assumptions.
- It does not own target selection.
- It does not own final reporting.
- It does not perform paper lookup except by forwarding gaps to the optional paper resolver.

## Input expectations

- target repo path
- selected reproduction goal
- relevant README setup steps
- any known OS or package constraints

## Output expectations

- conservative environment setup notes
- candidate conda commands
- asset path plan
- checkpoint and dataset source notes
- unresolved dependency or asset risks

## Notes

Use `references/env-policy.md`, `references/assets-policy.md`, `scripts/bootstrap_env.sh`, and `scripts/prepare_assets.py`.
