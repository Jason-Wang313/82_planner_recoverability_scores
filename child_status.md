# Child Status 82

Current stage: 2026-06-15 continuation audit terminal
Last update: 2026-06-15 08:43:38 +0100
PDF: C:/Users/wangz/Downloads/82.pdf
GitHub: https://github.com/Jason-Wang313/82_planner_recoverability_scores
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the 2026-06-15 plan-first audit recompiled and reran the full local TAMP recoverability benchmark, then rechecked CSV integrity, seeds, baselines, ablations, stress sweeps, PDF logs, Downloads-only PDF placement, Desktop exclusion, and public GitHub state. The terminal decision remains KILL_ARCHIVE because `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success on `combined_hard_shift`, below `learned_failure_classifier` at 0.87755 +/- 0.04128, with paired difference -0.02721 +/- 0.02776. Its paired gain over `contingent_replanner` is only 0.00680 +/- 0.02828, and ablations that remove the irreversible-trap penalty or failure-probability term improve success.
