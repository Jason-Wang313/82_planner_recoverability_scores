# Plan

Build paper 82 `planner_recoverability_scores` from the shared pool, compile PDF to Downloads only, and publish the exact-name public repo.

## 2026-06-15 Continuation Plan and Result

Plan before execution: re-audit Paper 82 under the ICLR-main-target gate without reducing experiment quality. The required checks were code compilation, full deterministic experiment rerun, CSV row/schema/seed/method coverage, main TAMP baseline comparisons, paired uncertainty, irreversible/damage tradeoffs, ablations, stress sweeps, PDF cleanliness, Downloads-only artifact placement, Desktop exclusion, public GitHub readiness, and stale v3 documentation cleanup.

Result: `python -m py_compile src/run_experiment.py` passed and `python src/run_experiment.py` regenerated 11,760 main rollout rows, 2,058 ablation rollout rows, and 25,200 stress rollout rows. The evidence still supports KILL_ARCHIVE. `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success on `combined_hard_shift`, below `learned_failure_classifier` at 0.87755 +/- 0.04128. The paired gain over `contingent_replanner` is only 0.00680 +/- 0.02828, while irreversible failure and damage are worse than contingent replanning. The strongest ablations also contradict the objective: removing the irreversible-trap penalty reaches 0.86734 success and removing the failure-probability term reaches 0.86394.

## 2026-06-21 Expanded-Standard v5 Plan and Result

Plan before execution: `docs/paper82_expanded_submission_plan_20260621.md` froze the expanded protocol before the runner was replaced. The plan required 10 seeds, nine main splits, thirteen methods, hard-regime aggregate paired tests, two-split ablations, six stress axes, fixed-risk deployment budgets, negative cases, a 25+ page manuscript, bright boxed clickable citations, Downloads-only numbered PDF placement, Desktop exclusion, public GitHub push, and root-ledger updates.

Result: `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py` passed, `python src/run_experiment.py` completed, `python scripts/generate_manuscript.py` regenerated the manuscript and references, LaTeX/BibTeX produced a 28-page PDF, visual QA sampled rendered PNG pages, and `python scripts/validate_submission_artifacts.py` passed. The evidence remains KILL_ARCHIVE. Final row counts: 74,880 main rollouts, 5,760 dataset rows, 1,170 seed metrics, 1,521 aggregate metrics, 378 paired rows, 130 hard-regime seed rows, 169 hard-regime aggregate metrics, 42 hard-regime paired rows, 16,000 ablation rows, 94,080 stress rows, 30,720 fixed-risk rows, and 24 negative cases. `recoverability_score_planner_v5` reaches 0.88711 +/- 0.00776 hard-regime aggregate success, below `learned_expected_utility` at 0.92305 +/- 0.00917, with paired lower95 -0.04882. The ablation, fixed-risk, and maximum-stress gates fail. Downloads-only PDF SHA256: D32F6F11DA77897EC8671FAE3D9860B1474AD6A5091A9F7034BDB33F77BB6249.
