# Submission Readiness Decision

Decision: KILL_ARCHIVE

ICLR main-conference readiness: NO.

Reason: The v4 continuation audit contains executable local evidence, but the result is negative. `recoverability_score_planner` reaches 0.85034 +/- 0.04163 goal success on `combined_hard_shift`, below `learned_failure_classifier` at 0.87755 +/- 0.04128. Its paired gain over `contingent_replanner` is only 0.00680 +/- 0.02828, and it has higher irreversible failure and damage than contingent replanning. Ablations also contradict the objective because removing the irreversible-trap penalty and removing the failure-probability term improve success.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with implemented model, strong real baselines, manual related work, and deployment evidence.

2026-06-15 continuation action: keep KILL_ARCHIVE. Do not submit this paper to ICLR main in its current form.
