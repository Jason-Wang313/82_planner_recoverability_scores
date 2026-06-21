# Paper 82 Expanded Submission-Readiness Plan - 2026-06-21

## Objective

Rebuild Paper 82, `planner_recoverability_scores`, into the strongest honest ICLR-main-target manuscript possible under the current constraints: CPU-only, RAM-light, no fabricated robot evidence, no Desktop PDFs, numbered final PDF in Downloads only, public GitHub repo, and bright boxed clickable citations. The rebuild must add real theory, a materially stronger experiment suite, fixed-risk safety checks, ablations, stress tests, negative cases, and a 25+ page manuscript without padding.

The starting v4 record is negative: the proposed recoverability score loses to a learned failure classifier on `combined_hard_shift`, has only a tiny paired gain over contingent replanning, and improves when central score terms are removed. The v5 pass must not hide that record. It may revise the method, but the final protocol below is frozen before execution and all predefined results must be reported honestly.

## Method Upgrade To Test

The v5 method is `recoverability_score_planner_v5`, a calibrated recoverability-certificate planner. For each candidate plan it estimates:

- nominal survival probability;
- recoverable deviation probability;
- irreversible trap probability;
- damage probability;
- expected recovery cost;
- budget slack;
- branch entropy as a proxy for how many distinct recovery modes remain available;
- uncertainty-adjusted safety penalty from held-out calibration residuals.

The paper will state a theory layer around recoverability certificates:

- define recoverability value as expected success after a deviation, not merely low failure probability;
- prove a bounded-error lemma showing how calibration residuals upper-bound conservative safety risk;
- prove a monotonicity proposition: if two plans have equal nominal success and cost, the plan with higher calibrated recoverability and lower irreversible risk weakly dominates under the score;
- identify the failure mode where recoverability collapses to ordinary risk avoidance when recovery cost and trap probability are not separable.

These are modeling/theoretical claims about the local benchmark and score, not claims of robot deployment.

## Main Experiment Protocol

Run one deterministic CPU process, one paper at a time. Do not reduce seeds, splits, methods, or rows for convenience.

Main evaluation:

- seeds: 10 (`0..9`);
- test episodes per split and seed: 64;
- training episodes per seed for learned baselines/calibration: 192;
- splits: `open_easy`, `narrow_passage_shift`, `object_slip_shift`, `irreversible_commitment`, `sensor_dropout_shift`, `budget_tight_shift`, `latent_mode_shift`, `adversarial_compound_shift`, and `combined_hard_shift`;
- methods: `nominal_shortest_plan`, `risk_averse_plan`, `robust_margin_planner`, `expected_cost_replanner`, `contingent_replanner`, `receding_horizon_replanner`, `conformal_failure_filter`, `learned_failure_classifier`, `learned_expected_utility`, `branch_entropy_planner`, `cvar_recovery_planner`, `recoverability_score_planner_v5`, and `oracle_recoverability_upper_bound`;
- expected main rollout rows: `9 * 10 * 64 * 13 = 74,880`;
- expected dataset rows: `9 * 10 * 64 = 5,760`;
- produce seed metrics, aggregate metrics, paired statistics, hard-regime aggregate seed metrics, hard-regime aggregate metrics, and hard-regime paired statistics.

Hard-regime aggregate:

- include `narrow_passage_shift`, `object_slip_shift`, `irreversible_commitment`, `sensor_dropout_shift`, `budget_tight_shift`, `latent_mode_shift`, `adversarial_compound_shift`, and `combined_hard_shift`;
- report aggregate goal success, recovery success, irreversible failure, damage, budget overrun, total cost, calibration error, plan diversity, and safety utility;
- compare v5 against the strongest non-oracle baseline by paired seed differences.

## Ablation Protocol

Run ablations on `combined_hard_shift` and `adversarial_compound_shift`, 10 seeds, 80 episodes per split and seed.

Ablations:

- `full_recoverability_score_v5`;
- `minus_recovery_success`;
- `minus_recovery_cost`;
- `minus_irreversible_trap_penalty`;
- `minus_damage_penalty`;
- `minus_budget_slack`;
- `minus_branch_entropy`;
- `minus_calibration_penalty`;
- `risk_only_score`;
- `expected_utility_only`;

Expected ablation rows: `2 * 10 * 80 * 10 = 16,000`.

The mechanism gate fails if any central ablation matches or beats the full method on hard-split goal success without a safety tradeoff, or if removing calibration improves both success and irreversible/damage rates.

## Stress Protocol

Run stress sweeps over six axes:

- navigation deviation;
- manipulation slip;
- trap pressure;
- sensor uncertainty;
- budget tightness;
- combined adversarial shift.

Use stress levels `0.0, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50`, 10 seeds, 32 episodes per seed, and the seven stress methods:

- `robust_margin_planner`;
- `contingent_replanner`;
- `learned_failure_classifier`;
- `learned_expected_utility`;
- `cvar_recovery_planner`;
- `recoverability_score_planner_v5`;
- `oracle_recoverability_upper_bound`.

Expected stress rollout rows: `6 * 7 * 10 * 32 * 7 = 94,080`.

The stress gate fails if v5 is dominated by a non-oracle method on maximum combined stress or if its irreversible/damage rate grows faster than the best learned or contingent baseline.

## Fixed-Risk Protocol

Evaluate safety-filtered deployment under false-irreversible-or-damage budgets `0.02`, `0.05`, `0.10`, and `0.20` on `combined_hard_shift` and `adversarial_compound_shift`.

Candidate methods:

- `conformal_failure_filter`;
- `learned_failure_classifier`;
- `learned_expected_utility`;
- `cvar_recovery_planner`;
- `recoverability_score_planner_v5`;
- `oracle_recoverability_upper_bound`.

Each method may abstain from executing a plan if its estimated irreversible/damage risk exceeds the budget. Report coverage, fixed-risk success, executed success, false-safety rate, damage, irreversible failure, and cost.

The fixed-risk gate fails if v5 cannot maintain false-safety below budget while preserving meaningful coverage at budget `0.05`.

## Negative Cases

Retain at least 20 negative cases spanning:

- irreversible traps;
- damage or lost-object failures;
- budget overruns;
- unrecovered deviations;
- high-confidence false-safe executions;
- cases where an ablation or baseline outperforms v5.

The manuscript must include these cases as evidence against overclaiming.

## Decision Criteria

Mark `STRONG_REVISE` only if all local gates pass:

- v5 beats the strongest non-oracle baseline on the hard-regime aggregate by at least `0.03` absolute goal success;
- the paired lower confidence bound versus the strongest non-oracle baseline is positive;
- v5 does not increase irreversible failure or damage versus the strongest safety baseline;
- fixed-risk coverage at budget `0.05` is at least `0.25` with false-safety not above budget;
- central ablations degrade either success or safety, showing the score terms are necessary;
- maximum combined stress is not dominated by a non-oracle baseline.

Mark `KILL_ARCHIVE` if any gate fails. Do not mark ICLR-main-ready without real robot evidence, accepted high-fidelity external benchmark validation, released trained baselines, and manual full related-work vetting.

## Manuscript And Artifact Requirements

- Generate a 25+ page ICLR-style manuscript from frozen CSVs.
- Use bright boxed clickable citations via `hyperref` with visible citation borders.
- Include theory, protocol, main results, hard-regime aggregate, ablations, stress, fixed-risk deployment, negative cases, limitations, and reviewer-attack responses.
- Build the final numbered PDF only as `C:/Users/wangz/Downloads/82.pdf`.
- Do not copy any PDF to Desktop.
- Add a validator that checks expected row counts, page count, citation/link settings, unresolved references, PDF placement, Desktop exclusion, and SHA256.
- Commit and push all repository changes to the public GitHub repository.
- Update root `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, `MASTER_SUBMISSION_REPORT.md`, and `SUBMISSION_AUDIT_MATRIX.csv` before moving to Paper 83.
