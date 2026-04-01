# ai-paper-reproduction-skills

Codex multi-skill repository for deep learning research workflows with a trusted-lane default.

The current implementation focus is a README-first paper reproduction cluster. The repository is expanding toward a broader research-skills layout with trusted and exploratory lanes while preserving the current public skill names.

The main skill is `ai-paper-reproduction`. Most users should still start there for end-to-end paper reproduction.

## What it optimizes for

- `README-first`
- `inference/eval first`
- `minimal trustworthy changes`
- `auditable patching`
- `trusted by default`
- `explicit exploration only`

## Quick Start

Install the current 5-skill reproduction cluster with the `skills` CLI:

```bash
npx skills add lllllllama/ai-paper-reproduction-skills --all
```

Then start with the main public orchestrator:

```text
Use ai-paper-reproduction on this AI repo. Stay README-first, prefer documented inference or evaluation, avoid unnecessary repo changes, and write outputs to repro_outputs/.
```

## Current layout

The repository currently ships one trusted reproduction cluster:

- `ai-paper-reproduction`
- `repo-intake-and-plan`
- `env-and-assets-bootstrap`
- `minimal-run-and-audit`
- `paper-context-resolver`

Planned trusted-lane additions:

- repository and model analysis
- safe research debugging
- trusted training execution

Planned explore-lane additions:

- exploratory code adaptation
- exploratory experiment running and ranking

Repository-wide routing and safety rules live under [references/](references/).

## Installation note

- Default install for this repository:

```bash
npx skills add lllllllama/ai-paper-reproduction-skills --all
```

- If you only want the main skill:

```bash
npx skills add lllllllama/ai-paper-reproduction-skills --skill ai-paper-reproduction
```

- The repository keeps one `SKILL.md` per skill under `skills/`, so it is compatible with multi-skill GitHub repository discovery in the `skills` CLI.
- Machine-readable skill metadata lives in [references/skill-registry.json](references/skill-registry.json).

## Current public skills

- `ai-paper-reproduction`
  - orchestrates README-first reproduction from intake through reporting
- `env-and-assets-bootstrap`
  - prepares conservative environment, checkpoint, dataset, and cache assumptions before execution
- `minimal-run-and-audit`
  - captures conservative execution evidence and writes standardized `repro_outputs/`

## Current helper skills

- `repo-intake-and-plan`
  - maps the repo, extracts documented commands, and recommends the smallest credible target
- `paper-context-resolver`
  - resolves a narrow paper-critical gap only when README and repo evidence are insufficient

## Output files

- `SUMMARY.md`
  - first page result and main blocker
- `COMMANDS.md`
  - copyable setup, asset, run, and verification commands
- `LOG.md`
  - concise process record with evidence and decisions
- `status.json`
  - stable machine-readable status
- `PATCHES.md`
  - patch record, only when repository files were modified

## Shared policies

- Routing policy: [references/routing-policy.md](references/routing-policy.md)
- Research pitfall checklist: [references/research-pitfall-checklist.md](references/research-pitfall-checklist.md)
- Branch and commit policy: [references/branch-and-commit-policy.md](references/branch-and-commit-policy.md)
- Output contract: [references/output-contract.md](references/output-contract.md)
- Skill registry: [references/skill-registry.json](references/skill-registry.json)

## Language behavior

- Human-readable outputs may follow the user's language.
- Machine-readable fields in trusted status files stay in English.
- Filenames stay in English.
- Commands, paths, package names, and config keys stay unchanged.

## Examples

- Main skill examples: [examples/example_prompt_main.md](examples/example_prompt_main.md)
- Sub-skill examples: [examples/example_prompt_subskills.md](examples/example_prompt_subskills.md)
- Real repo trials: [examples/real_repo_trials.md](examples/real_repo_trials.md)
- Release notes: [CHANGELOG.md](CHANGELOG.md)

## Current scope

- README-first reproduction of AI paper repositories
- documented inference or evaluation first
- training only as startup or partial verification unless explicitly needed
- explicit blockers instead of silent semantic changes
- trusted lane by default; exploration requires explicit intent

## Not a general research mega-skill

This repository is not a general paper summarizer or an unconstrained autonomous research agent. It aims to support deep learning research with explicit safety, auditability, and lane-aware boundaries.
