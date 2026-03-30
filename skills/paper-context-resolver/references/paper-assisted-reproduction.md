# Paper-Assisted Reproduction

## Purpose

Use paper context only to unblock README-first reproduction when the repository leaves a critical gap.

## Source order

1. paper link explicitly provided by the README
2. official project page or official paper page
3. arXiv or OpenReview primary paper record
4. Google Scholar only to help locate the primary source

## Allowed question types

- dataset version or split
- preprocessing or postprocessing details
- evaluation protocol details
- checkpoint or model variant mapping
- critical runtime assumptions

## Default exclusions

- full paper summary
- novelty explanation
- broad related-work discussion
- speculative "best settings" not tied to reproduction

## Conflict rule

If README and paper disagree:

- do not silently replace README
- record the conflict
- explain which source says what
- preserve the README-first policy in the final report
