---
name: ai-research-reproduction
description: Main orchestrator for README-first AI repo reproduction. Use when the user wants an end-to-end, minimal-trustworthy reproduction flow that reads the repository first, selects the smallest documented inference or evaluation target, coordinates intake, setup, trusted execution, optional trusted training, optional repository analysis, and optional paper-gap resolution, enforces conservative patch rules, records evidence assumptions deviations and human decision points, and writes the standardized `repro_outputs/` bundle. Do not use for paper summary, generic environment setup, isolated repo scanning, standalone command execution, silent protocol changes, or broad research assistance outside repository-grounded reproduction.
---

# ai-research-reproduction

## Purpose

Use this as the trusted-lane orchestrator for README-first AI repository
reproduction. The skill guides the agent toward a minimal trustworthy run with
auditable evidence; it should not micromanage implementation details that the
model can infer from the repository.

Start from the shared operating principles in
`../../references/agent-operating-principles.md`.

## Fit

Use this skill when all are true:

- The target is an AI code repository with a README, scripts, configs, or
  documented commands.
- The request spans multiple trusted phases such as intake, setup, execution,
  training verification, analysis, paper-gap resolution, and reporting.
- The desired result is a small reproducible target, not broad experimentation.

Do not use this skill for paper summaries, generic environment setup, isolated
repo scanning, standalone command execution, open-ended research design, or
explicit candidate-only exploration.

## Trusted Target Selection

Choose the smallest target that can honestly demonstrate repository-grounded
reproduction:

1. documented inference
2. documented evaluation
3. documented training startup or partial verification
4. full training only after explicit user confirmation

Treat README guidance as the primary reproduction intent. Use repository files
to clarify the README, not to silently replace it. When the README and paper
conflict, record the conflict and use `paper-context-resolver` only for the
narrow reproduction-critical gap.

## Workflow

1. Read the README and nearby repo signals.
2. Use `repo-intake-and-plan` to extract documented commands and candidate
   targets.
3. Select and justify the minimum trustworthy target.
4. Use `env-and-assets-bootstrap` only for target-specific environment,
   checkpoint, dataset, and cache assumptions.
5. Use `analyze-project` only when structure, insertion points, or suspicious
   implementation patterns need read-only clarification.
6. Use `minimal-run-and-audit` for documented inference, evaluation, smoke, or
   sanity execution.
7. Use `run-train` instead when the selected trusted target is training startup,
   short-run verification, full kickoff, or resume.
8. Pause for human review before fuller training claims or any change that could
   alter dataset, split, checkpoint, preprocessing, metric, loss, model
   semantics, or result interpretation.
9. Write the standardized outputs and give a concise final note in the user's
   language when practical.

## Patch Boundary

Prefer no repository edits. If edits are needed, keep them conservative and
auditable:

- Try command-line arguments, environment variables, path fixes, dependency
  version fixes, or dependency-file fixes before code changes.
- Avoid changing model architecture, core inference semantics, training logic,
  loss functions, or experiment meaning.
- If repository files must change, create a branch named
  `repro/YYYY-MM-DD-short-task`, keep verified patch commits sparse, and record
  README-fidelity impact in `PATCHES.md`.

See `references/patch-policy.md`.

## Outputs

Always target `repro_outputs/`:

```text
SUMMARY.md
COMMANDS.md
LOG.md
status.json
PATCHES.md   # only if patches were applied
```

Use the templates under `assets/` and the field rules in
`references/output-spec.md`.

- Put the shortest high-value summary in `SUMMARY.md`.
- Put copyable commands in `COMMANDS.md`.
- Put process evidence, assumptions, failures, and decisions in `LOG.md`.
- Put durable machine-readable state in `status.json`.
- Put branch, commit, validation, and README-fidelity impact in `PATCHES.md` when needed.
- Distinguish verified facts from inferred guesses.

## Reference Loading

- Load `references/language-policy.md` when writing human-readable outputs.
- Load `references/research-safety-principles.md` before protocol-sensitive
  decisions.
- Load `references/patch-policy.md` before modifying repository files.
- Keep specialized logic in sub-skills, scripts, templates, or references rather
  than expanding this entrypoint.

