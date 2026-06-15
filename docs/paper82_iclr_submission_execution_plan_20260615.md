# Paper 82 ICLR Submission-Readiness Execution Plan - 2026-06-15

## Objective

Re-audit Paper 82, `planner_recoverability_scores`, as an honest ICLR-main-target candidate. The current v4 evidence is negative: the recoverability-score planner does not beat the learned failure classifier on the main combined hard-shift split, and ablations improve when key terms are removed. The continuation pass must verify whether that negative decision still holds, clean stale v3 documentation, rebuild artifacts, and preserve a terminal state supported by evidence.

## Evidence Gate

1. Verify the runner with `python -m py_compile src/run_experiment.py`.
2. Re-run `python src/run_experiment.py` once with the existing deterministic benchmark, preserving all seven seeds, all baselines, ablations, stress axes, and row counts.
3. Audit CSV integrity and expected scale:
   - `rollouts.csv`: 11,760 main rollout rows.
   - `dataset_summary.csv`: generated episode coverage for the five main splits.
   - `raw_seed_metrics.csv`, `metrics.csv`, and `pairwise_stats.csv`: aggregate and paired uncertainty across seeds.
   - `ablation_rollouts.csv`: 2,058 rows.
   - `ablation_metrics.csv`: seven ablation rows.
   - `stress_sweep_raw.csv`: 25,200 rows.
   - `stress_sweep.csv`: stress-axis/method/level summaries.
   - `negative_cases.csv`: retained failure exemplars.
4. Confirm seeds 0 through 6, all eight main methods, all five main evaluation splits, all seven ablations, five stress axes, and six stress levels are present.

## Decision Criteria

Keep `KILL_ARCHIVE` if any of the following remain true:

1. `recoverability_score_planner` does not beat the strongest non-oracle baseline on `combined_hard_shift`.
2. Paired gain over `contingent_replanner` is too small or non-decisive.
3. The proposed method has worse irreversible-failure or damage rates than contingent or learned baselines.
4. Ablations contradict the objective, especially if removing the irreversible-trap penalty or failure-probability term improves success.
5. The benchmark remains local/generated without real robot, recognized high-fidelity simulator, or external TAMP benchmark validation.

Upgrade only to `STRONG_REVISE` if the rerun shows a decisive positive margin over learned failure classification and contingent replanning, favorable irreversible/damage tradeoffs, ablation support for the full recoverability objective, and honest limitations. Do not mark ICLR-main-ready without new external robot/high-fidelity evidence actually present in the repository.

## Artifact Gate

1. Rebuild the PDF with the required LaTeX passes. Use BibTeX if citations are active.
2. Fix recoverable LaTeX/BibTeX issues, including placeholder bibliography warnings or fragile float placement, without changing the empirical claim.
3. Copy only the canonical numbered PDF to `C:/Users/wangz/Downloads/82.pdf`.
4. Confirm `C:/Users/wangz/Desktop/82.pdf` is absent.
5. Record the Downloads PDF SHA256.

## Documentation And Repo Gate

1. Update child status, plan, final audit, hostile reviewer response, attack log, submission readiness docs, and version log with the continuation result.
2. Replace stale v3-only wording in docs that contradicts the v4 executable benchmark outcome.
3. Update root `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md` so the continuation audit is current through Paper 82.
4. Verify the public GitHub repository URL and visibility.
5. Commit and push the Paper 82 repository.
6. Verify local `HEAD` equals `origin/main` and the worktree is clean before moving to Paper 83.

## RAM Discipline

Run one Paper 82 experiment process at a time. Do not reduce seeds, baselines, ablations, stress levels, or row counts to save memory; preserve experiment quality and rely on the repo's deterministic local generator.
