# Repo Scan Rules

## Primary files

Always check these first when present:

- `README.md`
- `README`
- `requirements.txt`
- `environment.yml`
- `environment.yaml`
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `Dockerfile`

## High-signal directories

Inspect for command or configuration clues:

- `configs/`
- `config/`
- `scripts/`
- `tools/`
- `examples/`
- `notebooks/`
- `checkpoints/`

## Extraction priorities

1. explicit README commands
2. setup instructions
3. documented inference or demo entrypoints
4. documented evaluation entrypoints
5. documented training entrypoints
6. config references and asset path hints

## Classification guidance

- `inference`: demo, predict, generate, sample, infer, test-time forward use
- `evaluation`: eval, validate, benchmark, score, reproduce metrics
- `training`: train, finetune, pretrain, launch long-running experiments
- `other`: install, download, preprocess, export, convert, utility

## Conservative behavior

- prefer explicit README evidence over filename guesses
- mark guessed classifications as inferred
- record ambiguity instead of overcommitting
