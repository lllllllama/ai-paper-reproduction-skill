# Trigger Boundary Policy

This repository depends on clear trigger boundaries because the main skill and sub-skills operate on the same domain.

## Main rule

The main skill should trigger only for end-to-end README-first AI repo reproduction requests.

Sub-skills should trigger only for explicitly narrower requests:

- repo intake and planning
- environment and asset preparation
- minimal execution and audit
- narrow paper-context recovery

## Design rule for front matter descriptions

Each `description` should contain both:

- a positive routing clause: `Use when ...`
- an exclusion clause: `Do not use for ...`

This matters because the front matter is the strongest pre-trigger signal.

## Mis-trigger risks to control

- main skill firing on simple repo scan requests
- main skill firing on generic paper summary requests
- `repo-intake-and-plan` firing on environment-only requests
- `env-and-assets-bootstrap` firing on repo scan prompts
- `minimal-run-and-audit` firing before a target command exists
- `paper-context-resolver` firing on general literature requests

## Testing strategy

Use both:

1. static overlap checks on front matter descriptions
2. prompt-suite boundary tests with positive, boundary, and negative cases

Static checks are not enough because overlap often appears only when descriptions are exercised against realistic prompts.
