# ai-paper-reproduction-skills

Lane-aware Codex skill repository for deep learning research workflows.

This repository is built around one default rule: `trusted by default`. It is meant to help researchers reproduce repositories, inspect projects, run conservative verification, and record what happened without turning the process into opaque automation.

## What this repo is for

- README-first AI repository reproduction
- conservative environment and asset planning
- read-only project and model analysis
- trusted training startup verification and recorded training execution
- safe research debugging
- explicitly authorized exploratory code and run work

It is not intended to be:

- a general paper summarizer
- an unconstrained autonomous research agent
- a default “let AI rewrite the whole repo” workflow

## Core policy

- trusted by default
- README-first for reproduction
- explicit exploration only
- low-risk changes before code edits
- audit-heavy trusted outputs
- summary-heavy exploratory outputs

Shared routing, branch, pitfall, and output rules live under [references/](references/).

## Install

Install the full repository skill set:

```bash
npx skills add lllllllama/ai-paper-reproduction-skills --all
```

Install only the main orchestrator:

```bash
npx skills add lllllllama/ai-paper-reproduction-skills --skill ai-paper-reproduction
```

## Public skills

### Trusted lane

- `ai-paper-reproduction`
  - end-to-end README-first reproduction orchestrator
- `env-and-assets-bootstrap`
  - conservative environment, checkpoint, dataset, and cache planning
- `minimal-run-and-audit`
  - inference, evaluation, smoke, and sanity execution with `repro_outputs/`
- `analyze-project`
  - read-only repository and model analysis with `analysis_outputs/`
- `run-train`
  - trusted training execution with `train_outputs/`
- `safe-debug`
  - conservative research debugging with `debug_outputs/`

### Explore lane

- `explore-code`
  - isolated exploratory code adaptation and transplant work with `explore_outputs/`
- `explore-run`
  - isolated exploratory run planning, sweeps, and ranking with `explore_outputs/`

### Helper skills

- `repo-intake-and-plan`
  - narrow helper for repo scanning and documented command extraction
- `paper-context-resolver`
  - narrow helper for README-paper gap resolution

These helper skills are usually orchestrator-invoked rather than primary user entrypoints.

## Current trusted reproduction flow

Today the main orchestrator already does the following:

1. Scan the repository and README.
2. Extract documented commands.
3. Choose the smallest trustworthy target with this priority:
   - documented inference
   - documented evaluation
   - documented training
4. Build a conservative environment setup plan.
5. Build a conservative asset manifest for datasets, checkpoints, weights, and cache locations.
6. Execute the selected target:
   - non-training targets run through the trusted verify path
   - training targets run through `run-train`
7. Write `repro_outputs/`
8. When training was selected, also write `train_outputs/`

### Trusted training behavior

In trusted reproduction, training is intentionally conservative.

- If a smaller documented inference or evaluation target exists, the orchestrator prefers that first.
- If training is the selected trustworthy target, the orchestrator first performs startup verification or a short monitored training check.
- After that short verification, it does not silently continue into a broader training reproduction run.
- Instead, it surfaces:
  - the planned fuller training command
  - a conservative duration hint
  - a human review checkpoint asking whether fuller training should continue

### Explore training behavior

Exploration must be explicit.

- `explore-code` and `explore-run` are never the default route.
- In the explore lane, training does not pause for the trusted-lane confirmation checkpoint.
- Exploratory results are treated as candidates only, not trusted reproduction success.

## Output directories

- `repro_outputs/`
  - trusted reproduction bundle
- `train_outputs/`
  - trusted training execution bundle
- `analysis_outputs/`
  - read-only project analysis
- `debug_outputs/`
  - trusted debug diagnosis and patch plan
- `explore_outputs/`
  - exploratory changeset and run ranking

## Example prompts

Trusted reproduction:

```text
Use ai-paper-reproduction on this AI repo. Stay README-first, prefer documented inference or evaluation, avoid unnecessary repo changes, and write outputs to repro_outputs/.
```

Read-only project analysis:

```text
Use analyze-project on this repo. Read the code, map the model and training entrypoints, and flag suspicious patterns without editing files.
```

Trusted training:

```text
Use run-train on this repo. Run the selected documented training command conservatively for startup verification and write train_outputs/.
```

Safe debug:

```text
Use safe-debug on this traceback. Diagnose the failure first, propose the smallest safe fix, and do not patch until I approve.
```

Explicit exploration:

```text
Use explore-code on an isolated branch. Try a LoRA adaptation for this backbone, keep it exploratory only, and summarize the changes in explore_outputs/.
```

```text
Use explore-run on an experiment branch. Do a small-subset short-cycle sweep, rank the top runs, and treat the results as candidates only.
```

## Local validation

Run the full validation set:

```bash
python scripts/validate_repo.py
python scripts/test_skill_registry.py
python scripts/test_trigger_boundaries.py
python scripts/test_readme_selection.py
python scripts/test_output_rendering.py
python scripts/test_train_output_rendering.py
python scripts/test_analysis_output_rendering.py
python scripts/test_safe_debug_output_rendering.py
python scripts/test_explore_output_rendering.py
python scripts/test_explore_variant_matrix.py
python scripts/test_setup_planning.py
python scripts/test_orchestrator_dry_run.py
python scripts/test_training_lane_routing.py
```

If installation behavior changed, also run:

```bash
python scripts/install_skills.py --target ./tmp/skills --force
```

## Routing summary

- ambiguous requests go to the trusted lane
- exploration requires explicit authorization
- trusted skills must not auto-route into exploration
- explore skills must not claim trusted reproduction success
- same-level skills should not call each other directly

## Registry and shared policy references

- Skill registry: [references/skill-registry.json](references/skill-registry.json)
- Routing policy: [references/routing-policy.md](references/routing-policy.md)
- Branch and commit policy: [references/branch-and-commit-policy.md](references/branch-and-commit-policy.md)
- Output contract: [references/output-contract.md](references/output-contract.md)
- Research pitfall checklist: [references/research-pitfall-checklist.md](references/research-pitfall-checklist.md)

## Current limits

The repository framework is already stable, but some capabilities are still intentionally conservative:

- `run-train` is a bounded training monitor, not a full long-running scheduler
- trusted reproduction still avoids silent semantic changes
- helper skills remain narrow and are not meant to become public “do everything” entrypoints
- exploratory work is isolated and should not be confused with trusted baselines

## Scope

This repository is a lane-aware deep learning research toolkit that optimizes for safety, observability, and reuse.
