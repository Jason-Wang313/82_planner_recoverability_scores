# Paper 82 Terminal Audit - 2026-06-15

## Scope

Paper 82, `planner_recoverability_scores`, was re-audited under the sequential ICLR-main-target continuation gate. The audit tested whether the v4 negative result still holds and whether any evidence exists to revive the paper.

## Plan

The execution plan was written first in `docs/paper82_iclr_submission_execution_plan_20260615.md`. The plan required code compilation, a full deterministic experiment rerun, CSV integrity checks, main TAMP baseline analysis, paired uncertainty, irreversible/damage tradeoff analysis, ablations, stress sweeps, PDF hygiene, Downloads-only artifact placement, Desktop exclusion, public GitHub verification, and stale-documentation cleanup.

## Verification

- Code compilation: `python -m py_compile src/run_experiment.py` passed.
- Experiment rerun: `python src/run_experiment.py` completed and returned terminal recommendation KILL_ARCHIVE.
- Main rows: 11,760 rollout rows, 1,470 dataset-summary rows, 280 seed-level metric rows, 360 aggregate-metric rows, and 120 pairwise-stat rows.
- Ablation rows: 2,058 ablation rollout rows and 7 ablation summary rows.
- Stress rows: 25,200 stress rollout rows and 150 stress summary rows.
- Negative cases: 16 rows.
- Seeds: 0 through 6.
- Methods: `contingent_replanner`, `expected_cost_replanner`, `learned_failure_classifier`, `nominal_shortest_plan`, `oracle_recoverability_upper_bound`, `recoverability_score_planner`, `risk_averse_plan`, and `robust_margin_planner`.

## Central Evidence

On `combined_hard_shift`, `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success. `learned_failure_classifier` reaches 0.87755 +/- 0.04128, and `contingent_replanner` reaches 0.84353 +/- 0.04055.

The paired goal-success difference versus `learned_failure_classifier` is -0.02721 +/- 0.02776 with only 1/7 better seeds. The paired goal-success gain over `contingent_replanner` is only 0.00680 +/- 0.02828 with 4/7 better seeds.

The safety tradeoff is also unfavorable against contingent replanning: recoverability scoring has 0.00680 irreversible failure and 0.01701 damage, while contingent replanning has 0.00000 irreversible failure and 0.01020 damage.

Ablations contradict the objective. Full recoverability score reaches 0.85034 success. Removing the irreversible-trap penalty improves success to 0.86734, and removing the failure-probability term improves success to 0.86394.

At maximum combined stress, recoverability scoring reaches 0.85119 success, slightly above learned failure classification at 0.84524. This favorable stress slice does not rescue the paper because the main split, paired statistics, and ablations remain negative.

## Artifact Verification

- Downloads PDF: `C:/Users/wangz/Downloads/82.pdf`
- SHA256: `CB79882533BE0A5DA119C783411BE47C2534307987372ADD8B39C7509595140E`
- Desktop PDF: absent at `C:/Users/wangz/Desktop/82.pdf`
- GitHub: `https://github.com/Jason-Wang313/82_planner_recoverability_scores`

## Decision

Final decision: KILL_ARCHIVE.

The paper is useful as a reproducible negative diagnostic, but it should not be submitted to ICLR main. The proposed method loses to the strongest learned baseline on the main split, has no decisive paired advantage over contingent replanning, carries worse safety metrics than contingent replanning, and is contradicted by its own ablations.
