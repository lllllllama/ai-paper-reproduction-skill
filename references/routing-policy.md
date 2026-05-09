# Routing Policy

This repository uses explicit research lanes to keep skill routing predictable and safe.

## Default stance

Route ambiguous requests to the trusted lane by default.

Do not route to exploration unless the user clearly authorizes speculative trial work.

Use `agent-operating-principles.md` as the shared posture: think before acting,
keep the solution small, change only what is necessary, and work toward
verifiable goals. These principles guide lane choice without forcing a fixed
implementation sequence.

## Lifecycle model

Route by the user's current lifecycle need before choosing a concrete skill:

| Lifecycle need | Preferred skill |
|---|---|
| Understand a repository without heavy execution | `analyze-project` |
| Reproduce a README-documented repository end to end | `ai-research-reproduction` |
| Prepare environment, assets, checkpoints, or caches | `env-and-assets-bootstrap` |
| Run documented inference or evaluation | `minimal-run-and-audit` |
| Start, resume, or verify training | `run-train` |
| Diagnose an active research-code failure | `safe-debug` |
| Explore candidates on top of `current_research` | `ai-research-explore`, `explore-code`, or `explore-run` |
| Report or package evidence | the skill that owns the active output directory |

## Trusted lane

Trusted-lane skills are for:

- README-first paper reproduction
- repository analysis and code familiarization
- environment and asset preparation
- conservative run verification
- training execution requested by the researcher
- safe research debugging

Current trusted public skills:

- `ai-research-reproduction`
- `env-and-assets-bootstrap`
- `minimal-run-and-audit`
- `analyze-project`
- `run-train`
- `safe-debug`

Traits:

- preserve scientific meaning
- minimize unreviewed code changes
- write durable audit outputs
- surface assumptions, deviations, and blockers

## Explore lane

Explore-lane skills are for:

- end-to-end exploratory work on top of `current_research`
- broad-sweep experiments
- low-cost speculative variants
- isolated branch or worktree modifications
- migration-learning style adaptation attempts
- summary-oriented result ranking

Current explore public skills:

- `ai-research-explore`
- `explore-code`
- `explore-run`

The explore lane follows a two-loop rhythm:

- outer loop: understand the repository, freeze task/evaluation/budget, map
  sources, gate ideas, and decide whether a candidate is worth trying
- inner loop: make one bounded candidate change or run, smoke-check it, collect
  evidence, rank it, then stop or return to the outer loop

This is not a never-stop autonomous research policy. Stop at blockers, missing
anchors, unclear scientific meaning, exhausted budget, or human checkpoints.

Explore-lane requests should usually contain signals such as:

- "try a batch"
- "sweep"
- "see what works"
- "idle GPU"
- "broad search"
- "explore"
- "try several variants"
- "current_research"
- "on top of the current research"
- "coordinate code and run exploration"

## Helper lane

Helper skills are narrow and should not dominate routing when a public trusted-lane skill is a better fit.

Helpers should mostly be:

- orchestrator-invoked
- explicitly named by the user
- used only when the request is clearly narrower than a public skill

Current helper skills:

- `repo-intake-and-plan`
- `paper-context-resolver`

## Safety rules

- Trusted skills must not auto-route into exploration.
- Exploration must not silently claim trusted reproduction success.
- Peer leaf skills should not call each other directly.
- End-to-end orchestration should happen through the public orchestrator skill for the relevant task family.

