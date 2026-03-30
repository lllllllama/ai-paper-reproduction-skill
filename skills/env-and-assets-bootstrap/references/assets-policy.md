# Assets Policy

## Goal

Prepare checkpoints, datasets, and caches conservatively and transparently.

## Order of evidence

1. README links and paths
2. config files and default arguments
3. code-level constants or path joins
4. careful inference from filenames

## Behavior

- prefer documented asset sources
- preserve source URLs or identifiers when recording downloads
- avoid mirroring unofficial files unless the project explicitly points to them
- never claim an asset is the canonical one unless the repository or primary paper source supports it

## Common asset groups

- model checkpoints
- tokenizer files
- dataset archives or prepared splits
- cache directories
- output directories

## Reporting

Record:

- requested asset
- source
- target local path
- status: present, missing, downloaded, skipped, unknown
