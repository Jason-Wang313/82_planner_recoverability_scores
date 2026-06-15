# Final Audit

1. Chosen thesis: Planner Recoverability Scores explores `Score plans by recoverability under physical deviation, not just nominal feasibility.` for task and motion planning.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v4 continuation audit.
4. Reason: the executable local benchmark is reproducible, but the proposed recoverability score loses to the learned failure classifier and is contradicted by ablations.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, and `docs/hostile_reviewer_response.md`.
6. Reproducibility: `python src\run_experiment.py` reruns the local benchmark, but no real robot or high-fidelity benchmark is reproduced.
7. Claim-validity status: main-conference claims killed; archive memo retained as a negative evidence audit.
8. Exact Downloads PDF path: `C:/Users/wangz/Downloads/82.pdf`
9. GitHub URL: https://github.com/Jason-Wang313/82_planner_recoverability_scores
10. Confirmation: no visible Desktop copy was requested or made.

## 2026-06-15 Continuation Audit

1. Plan-first requirement: satisfied by `docs/paper82_iclr_submission_execution_plan_20260615.md` before the evidence gate was rerun.
2. Code gate: `python -m py_compile src/run_experiment.py` passed.
3. Experiment gate: `python src/run_experiment.py` completed with terminal recommendation KILL_ARCHIVE.
4. CSV integrity gate: audited 11,760 `rollouts.csv` rows, 1,470 `dataset_summary.csv` rows, 280 `raw_seed_metrics.csv` rows, 360 `metrics.csv` rows, 120 `pairwise_stats.csv` rows, 2,058 `ablation_rollouts.csv` rows, 7 `ablation_metrics.csv` rows, 25,200 `stress_sweep_raw.csv` rows, 150 `stress_sweep.csv` rows, and 16 `negative_cases.csv` rows.
5. Coverage gate: seeds 0 through 6, eight main methods, five main splits, seven ablations, five stress axes, and six stress levels are present.
6. Decisive split: on `combined_hard_shift`, `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success, below `learned_failure_classifier` at 0.87755 +/- 0.04128.
7. Paired statistics: recoverability minus learned failure classifier is -0.02721 +/- 0.02776 with only 1/7 better seeds. The gain over `contingent_replanner` is only 0.00680 +/- 0.02828 with 4/7 better seeds.
8. Safety gate: `recoverability_score_planner` has irreversible failure 0.00680 and damage 0.01701, while `contingent_replanner` has irreversible failure 0.00000 and damage 0.01020.
9. Ablation gate: removing the irreversible-trap penalty improves success to 0.86734, and removing the failure-probability term improves success to 0.86394. This contradicts the proposed objective.
10. Stress gate: maximum combined stress is mildly favorable to recoverability scoring at 0.85119 success, but this does not overturn the main split or ablation failures.
11. PDF gate: `paper/main.pdf` rebuilt after float-placement cleanup, then copied to `C:/Users/wangz/Downloads/82.pdf`.
12. Artifact gate: `C:/Users/wangz/Downloads/82.pdf` SHA256 is `CB79882533BE0A5DA119C783411BE47C2534307987372ADD8B39C7509595140E`; `C:/Users/wangz/Desktop/82.pdf` is absent.
13. Final decision: KILL_ARCHIVE. The paper is useful as a reproducible negative diagnostic, but it is not ICLR-main-ready and should not be reframed as a positive method paper.
