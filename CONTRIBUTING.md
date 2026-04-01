# Contributing

This repository is a Codex multi-skill collection. Keep changes small, readable, and easy to validate.

## Local workflow

1. Edit the relevant files under `skills/`, `references/`, or `scripts/`.
2. Run:

```bash
python scripts/validate_repo.py
python scripts/test_skill_registry.py
python scripts/test_trigger_boundaries.py
python scripts/test_readme_selection.py
python scripts/test_output_rendering.py
```

3. If you changed installation behavior, also test:

```bash
python scripts/install_skills.py --target ./tmp/skills --force
```

4. Commit only after the repository validates cleanly.

## Repository rules

- Keep each skill folder named exactly after its front matter `name`.
- Register every public or helper skill in `references/skill-registry.json`.
- Keep `SKILL.md` focused on workflow and boundaries.
- Move detailed policy into `references/`.
- Keep reusable output templates in `assets/`.
- Keep helper automation in `scripts/`.
- Avoid heavy runtime dependencies.
- Preserve trusted-lane defaults unless the change intentionally introduces an explore-lane capability.

## Compatibility rules

- Human-readable Markdown may adapt to user language.
- Machine-readable keys and enums must remain in stable English.
- Output filenames under `repro_outputs/` must remain stable unless there is a strong migration reason.

## Pull request checklist

- `python scripts/validate_repo.py` passes
- `python scripts/test_skill_registry.py` passes
- `python scripts/test_trigger_boundaries.py` passes
- `python scripts/test_readme_selection.py` passes
- `python scripts/test_output_rendering.py` passes
- installer still works
- changed skill metadata still matches its folder and purpose
- routing and lane behavior remain intentional
- output spec changes are intentional and documented
