        # Hostile Reviewer Response

        Paper: 82 Planner Recoverability Scores

        ## Strongest Technical Threats
        - XFlowMP: Task-Conditioned Motion Fields for Generative Robot Planning with Schrodinger Bridges (2025)
- An incremental constraint-based framework for task and motion planning (2018)
- Combined Task and Motion Planning via Sketch Decompositions (2024)
- Representation, learning, and planning algorithms for geometric task and motion planning (2022)
- Socially intelligent task and motion planning for human-robot interaction (2020)
- Integrating Task-Motion Planning with Reinforcement Learning for Robust Decision Making in Mobile Robots (2018)
- Contingent Task and Motion Planning under Uncertainty for Human-Robot Interactions (2020)
- Integrating Motion Planning in Vision Language Action Agents (2025)

        ## ICLR Main Response
        A hostile ICLR reviewer would be correct to reject this as a main-conference submission. The v4 paper has an executable local benchmark, but the proposed recoverability score does not beat the learned failure classifier on the main hard split and its ablations expose objective misspecification. It also does not contain the real robot, high-fidelity simulator, or manual related-work depth needed for the ICLR main track.

        ## Honest Action
        The paper is marked `KILL_ARCHIVE`. This avoids converting a generated workshop-style idea into an overstated main-conference claim.

        ## What Would Be Needed To Revive
        - Real robot or high-fidelity benchmark experiments.
        - Implemented model and baselines, not synthetic probability tables.
        - Manual full-paper related-work audit.
        - Paper-specific writing and figures.
        - Evidence that the core mechanism is learned and useful under deployment shift.

## 2026-06-15 Continuation Response

The continuation audit strengthens the hostile-reviewer conclusion:

- `recoverability_score_planner`: 0.85034 +/- 0.04163 goal success on `combined_hard_shift`.
- `learned_failure_classifier`: 0.87755 +/- 0.04128 goal success.
- Paired recoverability-minus-learned difference: -0.02721 +/- 0.02776, better in only 1/7 seeds.
- Paired gain over `contingent_replanner`: 0.00680 +/- 0.02828, not decisive.
- `contingent_replanner` has lower irreversible failure and damage than the proposed score.
- Removing the irreversible-trap penalty or failure-probability term improves success, contradicting the mechanism.

The honest action remains KILL_ARCHIVE.
