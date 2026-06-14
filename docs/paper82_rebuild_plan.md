# Paper 82 Rebuild Plan

## Goal

Rebuild `planner_recoverability_scores` from an archive-only synthetic scaffold into the strongest honest ICLR-main-target artifact possible. The scientific question is whether task-and-motion planners should score candidate plans by how recoverable their likely physical deviations are, not only by nominal feasibility, nominal path cost, or scalar risk.

## Evidence Standard

The rebuild must replace scalar probability diagnostics with an implemented benchmark, implemented baselines, multi-seed evaluation, ablations, stress tests, uncertainty summaries, negative cases, figures, and a reproducible paper PDF. Because this workspace does not contain real robot logs or an external high-fidelity task-and-motion planning benchmark for this paper, the ceiling is `STRONG_REVISE`. If recoverability scoring fails to clear strong robust/replanning baselines, the correct terminal decision is `KILL_ARCHIVE`.

## Benchmark

Create a deterministic local task-and-motion planning benchmark with 2D manipulation/navigation plans, hidden physical deviations, action failure modes, irreversible traps, recovery actions, and goal completion. Each episode will contain candidate plan skeletons with equal or similar nominal feasibility but different failure recoverability.

Evaluation splits:

1. `open_easy`: low deviation and mostly reversible failures.
2. `narrow_passage_shift`: base/navigation deviations can trap the robot or block future approaches.
3. `object_slip_shift`: manipulation deviations cause slips, drops, or displaced objects.
4. `irreversible_commitment`: some plans enter states where recovery is impossible or very costly.
5. `combined_hard_shift`: clutter, narrow passages, slip, occlusion, and irreversible commitments combined.

## Methods

Implement all methods in `src/run_experiment.py` with no hidden hand-entered result tables.

Baselines:

1. `nominal_shortest_plan`: chooses the lowest nominal path/action cost.
2. `risk_averse_plan`: avoids high predicted failure probability.
3. `expected_cost_replanner`: minimizes expected cost with one-step replanning.
4. `robust_margin_planner`: maximizes clearance and manipulation margin.
5. `contingent_replanner`: keeps a simple contingency branch for the most likely failure.
6. `learned_failure_classifier`: lightweight learned proxy over plan features and failure labels.

Proposed mechanism:

`recoverability_score_planner`: estimates failure probability, recovery success, recovery cost, irreversible trap probability, and diagnostic value for each candidate plan, then chooses the plan with the best recoverable-risk score.

Upper bound:

`oracle_recoverability_upper_bound`: uses ground-truth deviation/recovery outcomes to choose the best candidate plan.

## Metrics

Report seed-level and aggregate metrics:

1. Goal success.
2. Recovery success after deviation.
3. Irreversible failure/trap rate.
4. Damage or lost-object rate.
5. Total cost.
6. Recovery attempts.
7. Calibration error for recoverability score.
8. Paired differences versus the strongest non-oracle baseline.

## Ablations

Evaluate proposed variants on `combined_hard_shift`:

1. Full recoverability score.
2. Minus recovery-success term.
3. Minus recovery-cost term.
4. Minus irreversible-trap penalty.
5. Minus diagnostic-value term.
6. Minus failure-probability term.
7. Risk-only score.

## Stress Tests

Sweep independent stress levels for navigation deviation, manipulation slip, irreversible trap probability, sensor uncertainty, and combined shift. Compare recoverability scoring against robust margin, contingent replanning, learned failure classification, and the oracle.

## Paper Update

Rewrite the paper as a compact ICLR-style submission-hardening report:

1. Define recoverability score operationally.
2. Describe benchmark dynamics, candidate plan skeletons, deviations, and recovery actions.
3. Present main results, ablations, stress tests, and negative cases.
4. Include hostile related-work pressure and limitations.
5. Use the terminal decision supported by evidence, not the desired outcome.

## Delivery Checklist

1. Run all experiments from scratch.
2. Produce CSVs and figures in the repo.
3. Compile the PDF and copy only `82.pdf` to `C:\Users\wangz\Downloads`.
4. Update local status files and root pool reports.
5. Commit changes and push the matching public GitHub repository.

