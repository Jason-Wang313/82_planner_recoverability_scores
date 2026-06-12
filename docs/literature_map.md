        # Literature Map

        Paper: 82 planner_recoverability_scores

        Field box: task and motion planning

        Thesis: Planner Recoverability Scores turns the seed bet into a mechanism: Score plans by recoverability under physical deviation, not just nominal feasibility.

        ## Landscape Sweep Summary
        The selector ranked records from the shared 500,000-record pool. The closest visible clusters are:
        - An incremental constraint-based framework for task and motion planning (2018)
- XFlowMP: Task-Conditioned Motion Fields for Generative Robot Planning with Schrodinger Bridges (2025)
- Combined Task and Motion Planning via Sketch Decompositions (2024)
- Representation, learning, and planning algorithms for geometric task and motion planning (2022)
- A Hybrid Approach to Intricate Motion, Manipulation and Task Planning (2009)
- Socially intelligent task and motion planning for human-robot interaction (2020)
- Extended Tree Search for Robot Task and Motion Planning (2021)
- Learning to guide task and motion planning using score-space representation (2019)
- AND/OR net representation for robotic task sequence planning (1998)
- Contingent Task and Motion Planning under Uncertainty for Human–Robot Interactions (2020)
- Discovering State and Action Abstractions for Generalized Task and Motion Planning (2022)
- Sequence-Based Plan Feasibility Prediction for Efficient Task and Motion Planning (2023)

        ## Hidden Assumptions
        - The executed trajectory is a sufficient training target.
- Unobserved physical alternatives can be averaged into uncertainty.
- Task labels capture the mechanism that caused failure.
- A planner only needs nominal feasibility.
- Embodiment-specific contact effects are nuisance variation.

        ## Boundary
        The project avoids weak moves such as bigger models, generic uncertainty, or a benchmark-only contribution. It centers a mechanism-level change: Planner recoverability scores keeps action-critical alternatives explicit until a physical observation collapses them.
