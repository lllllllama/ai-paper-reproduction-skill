# Routing Policy

This repository uses explicit research lanes to keep skill routing predictable and safe.

## Default stance

Route ambiguous requests to the trusted lane by default.

Do not route to exploration unless the user clearly authorizes speculative trial work.

## Trusted lane

Trusted-lane skills are for:

- README-first paper reproduction
- repository analysis and code familiarization
- environment and asset preparation
- conservative run verification
- training execution requested by the researcher
- safe research debugging

Traits:

- preserve scientific meaning
- minimize unreviewed code changes
- write durable audit outputs
- surface assumptions, deviations, and blockers

## Explore lane

Explore-lane skills are for:

- broad-sweep experiments
- low-cost speculative variants
- isolated branch or worktree modifications
- migration-learning style adaptation attempts
- summary-oriented result ranking

Explore-lane requests should usually contain signals such as:

- "try a batch"
- "sweep"
- "see what works"
- "idle GPU"
- "broad search"
- "explore"
- "try several variants"

## Helper lane

Helper skills are narrow and should not dominate routing when a public trusted-lane skill is a better fit.

Helpers should mostly be:

- orchestrator-invoked
- explicitly named by the user
- used only when the request is clearly narrower than a public skill

## Safety rules

- Trusted skills must not auto-route into exploration.
- Exploration must not silently claim trusted reproduction success.
- Same-level skills should not call each other directly.
- End-to-end orchestration should happen only through the public orchestrator skill.
