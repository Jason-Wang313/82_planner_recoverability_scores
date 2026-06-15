# Plan

Build paper 82 `planner_recoverability_scores` from the shared pool, compile PDF to Downloads only, and publish the exact-name public repo.

## 2026-06-15 Continuation Plan and Result

Plan before execution: re-audit Paper 82 under the ICLR-main-target gate without reducing experiment quality. The required checks were code compilation, full deterministic experiment rerun, CSV row/schema/seed/method coverage, main TAMP baseline comparisons, paired uncertainty, irreversible/damage tradeoffs, ablations, stress sweeps, PDF cleanliness, Downloads-only artifact placement, Desktop exclusion, public GitHub readiness, and stale v3 documentation cleanup.

Result: `python -m py_compile src/run_experiment.py` passed and `python src/run_experiment.py` regenerated 11,760 main rollout rows, 2,058 ablation rollout rows, and 25,200 stress rollout rows. The evidence still supports KILL_ARCHIVE. `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success on `combined_hard_shift`, below `learned_failure_classifier` at 0.87755 +/- 0.04128. The paired gain over `contingent_replanner` is only 0.00680 +/- 0.02828, while irreversible failure and damage are worse than contingent replanning. The strongest ablations also contradict the objective: removing the irreversible-trap penalty reaches 0.86734 success and removing the failure-probability term reaches 0.86394.
