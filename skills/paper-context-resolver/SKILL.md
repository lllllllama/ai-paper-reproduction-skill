---
name: paper-context-resolver
description: Resolve reproduction-critical gaps from primary paper sources only when README and repository files are insufficient, while preserving README-first behavior and explicitly recording any conflicts.
---

# paper-context-resolver

## When to apply

- README and repo files leave a reproduction-critical gap.
- The gap concerns dataset version, split, preprocessing, evaluation protocol, checkpoint mapping, or runtime assumptions.
- The main skill needs a narrow evidence supplement instead of a full paper summary.

## When not to apply

- The README already gives enough reproduction detail.
- The user wants a general paper explanation rather than reproduction support.
- The goal is to override README instructions without documenting the conflict.

## Clear boundaries

- This skill is optional.
- It supplements README-first reproduction.
- It does not replace the main orchestration flow.
- It does not summarize the whole paper by default.

## Input expectations

- target repo metadata
- reproduction-critical question
- existing README or repo evidence
- any already known paper links

## Output expectations

- narrowed source list
- reproduction-relevant answer only
- explicit README-paper conflict note when applicable
- clear distinction between direct evidence and inference

## Notes

Use `references/paper-assisted-reproduction.md`.
