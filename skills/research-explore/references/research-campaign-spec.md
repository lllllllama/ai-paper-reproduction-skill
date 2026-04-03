# Research Campaign Spec

## Purpose

Use `research_campaign.json` or `research_campaign.yaml` when `research-explore` is operating in the third scenario:

- the task family is already chosen
- the dataset is already chosen
- the evaluation method is already chosen
- the provided SOTA table is already frozen by the researcher
- the remaining work is campaign governance, implementation, and candidate filtering

`variant_spec` still exists, but it is now the run-level part of a larger campaign.

## Minimal Shape

```json
{
  "current_research": "seg-branch@abc1234",
  "task_family": "segmentation",
  "dataset": "DemoSeg",
  "benchmark": {
    "name": "DemoBench",
    "primary_metric": "miou",
    "metric_goal": "maximize"
  },
  "evaluation_source": {
    "command": "python eval.py --config configs/demo.yaml",
    "path": "eval.py",
    "primary_metric": "miou",
    "metric_goal": "maximize"
  },
  "sota_reference": [
    {
      "name": "Provided SOTA",
      "metric": "miou",
      "value": 80.0,
      "source": "paper-or-table-url"
    }
  ],
  "candidate_ideas": [
    {
      "id": "idea-lora-rank",
      "summary": "Increase LoRA rank while keeping the decoder unchanged.",
      "change_scope": "lora_rank",
      "target_component": "segmentation_head",
      "expected_upside": 0.85,
      "implementation_risk": 0.20,
      "eval_risk": 0.15,
      "rollback_ease": 0.90,
      "estimated_runtime_cost": 0.35,
      "single_variable_fit": 0.95
    }
  ],
  "compute_budget": {
    "max_runtime_hours": 8
  },
  "baseline_gate": {
    "abandon_gap": 2.0
  },
  "execution_policy": {
    "run_selected_variants": true,
    "max_executed_variants": 2,
    "variant_timeout": 1800
  },
  "variant_spec": {
    "current_research": "seg-branch@abc1234",
    "base_command": "python train.py --config configs/demo.yaml",
    "variant_axes": {
      "lora_rank": ["4", "8"]
    },
    "subset_sizes": [64],
    "short_run_steps": [100],
    "max_variants": 2,
    "max_short_cycle_runs": 1,
    "primary_metric": "miou",
    "metric_goal": "maximize"
  }
}
```

## Required Top-Level Fields

- `current_research`
  Durable anchor for the current research state.
- `task_family`
  The already-chosen task family, such as `segmentation`, `classification`, or `depth`.
- `dataset`
  The dataset name used for this campaign.
- `benchmark`
  The benchmark name or descriptor. A dictionary may also carry `primary_metric` and `metric_goal`.
- `evaluation_source`
  The frozen evaluation contract input. Prefer a command plus an optional path.
- `sota_reference`
  The user-provided comparison table. `research-explore` treats this as authoritative input and does not prove completeness.
- `candidate_ideas`
  Candidate directions that the researcher already wants to consider.
- `variant_spec`
  The run-level candidate matrix used by `explore-run`.

## `evaluation_source`

Supported fields:

- `command`
- `path`
- `primary_metric`
- `metric_goal`
- `execution_kind`
- `artifacts`
- `notes`
- `split`

This block feeds both:

- `analysis_outputs/EVAL_CONTRACT.md`
- the baseline gate

## `sota_reference`

Each item should contain:

- `name`
- `metric`
- `value`

Optional fields:

- `source`
- `notes`
- `metric_goal`

This is a frozen comparison set for the campaign. It is not a guarantee that the real global SOTA has been fully covered.

## `candidate_ideas`

Each item should contain:

- `id`
- `summary`
- `change_scope`
- `target_component`
- `expected_upside`
- `implementation_risk`
- `eval_risk`
- `rollback_ease`
- `estimated_runtime_cost`
- `single_variable_fit`

Optional fields:

- `hypothesis`
- `supporting_changes`

The orchestrator uses these to run the idea gate. It does not treat them as novelty claims.

## Gates

### Baseline gate

Default rules:

- `maximize`: abandon if baseline trails provided SOTA by more than `2.0` absolute points
- `minimize`: abandon if baseline is worse than provided SOTA by more than `5%`

The gate can return:

- `proceed`
- `borderline`
- `abandon`
- `not-applicable`

### Idea gate

Ideas are ranked with:

- `expected_upside`
- `single_variable_fit`
- `rollback_ease`
- `implementation_risk`
- `eval_risk`
- `estimated_runtime_cost`

If the top-two ideas are too close, `research-explore` records a human checkpoint instead of silently training.

## Output Expectations

Campaign mode writes:

- `analysis_outputs/RESEARCH_MAP.md`
- `analysis_outputs/CHANGE_MAP.md`
- `analysis_outputs/EVAL_CONTRACT.md`
- `analysis_outputs/status.json`
- `explore_outputs/CHANGESET.md`
- `explore_outputs/IDEA_GATE.md`
- `explore_outputs/EXPERIMENT_PLAN.md`
- `explore_outputs/EXPERIMENT_LEDGER.md`
- `explore_outputs/TOP_RUNS.md`
- `explore_outputs/status.json`

## Notes

- Keep idea generation human-guided.
- Keep evaluation and SOTA inputs human-frozen.
- Let `research-explore` focus on understanding, gating, implementation planning, controlled execution, and comparison.
