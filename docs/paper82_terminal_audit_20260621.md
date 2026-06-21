# Paper 82 Terminal Audit - 2026-06-21

## Scope

Paper 82, `planner_recoverability_scores`, was rebuilt under the expanded-standard ICLR-main-target continuation gate. The rebuild added real theory, a stronger local benchmark, hard-regime aggregate statistics, ablations, stress sweeps, fixed-risk checks, a generated 28-page manuscript, bright boxed citations, and artifact validation.

## Verification

- Plan-first document: `docs/paper82_expanded_submission_plan_20260621.md`.
- Code compile: `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py` passed.
- Full experiment: `python src/run_experiment.py` completed.
- Manuscript generation: `python scripts/generate_manuscript.py` completed.
- PDF build: `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` completed.
- Artifact validation: `python scripts/validate_submission_artifacts.py` passed.
- Visual QA: rendered 28 pages to PNG and inspected representative pages for citation boxes, figures, dense tables, fixed-risk appendix, and references.

## Row Counts

- Main rollouts: 74,880.
- Dataset rows: 5,760.
- Raw seed metrics: 1,170.
- Aggregate metrics: 1,521.
- Pairwise stats: 378.
- Hard-regime seed metrics: 130.
- Hard-regime aggregate metrics: 169.
- Hard-regime paired stats: 42.
- Ablation rollouts: 16,000.
- Ablation seed metrics: 200.
- Ablation metrics: 20.
- Stress rollouts: 94,080.
- Stress seed metrics: 2,940.
- Stress metrics: 294.
- Fixed-risk rollouts: 30,720.
- Fixed-risk seed metrics: 480.
- Fixed-risk metrics: 48.
- Fixed-risk pairwise rows: 160.
- Negative cases: 24.

## Central Evidence

On the hard-regime aggregate, `recoverability_score_planner_v5` reaches 0.88711 +/- 0.00776 goal success. The strongest non-oracle baseline, `learned_expected_utility`, reaches 0.92305 +/- 0.00917.

The paired goal-success difference versus `learned_expected_utility` is -0.03594 +/- 0.01288 with lower95 -0.04882 and 0/10 better seeds.

The ablation gate fails because central removals match or beat the full method on success/safety tradeoffs. The fixed-risk gate fails because non-oracle coverage at the 0.05 budget is zero on both hard fixed-risk splits. The stress gate fails because at maximum combined stress `recoverability_score_planner_v5` reaches 0.51562, while `learned_expected_utility` reaches 0.58750.

## Artifact Verification

- Downloads PDF: `C:/Users/wangz/Downloads/82.pdf`.
- PDF pages: 28.
- SHA256: `D32F6F11DA77897EC8671FAE3D9860B1474AD6A5091A9F7034BDB33F77BB6249`.
- Desktop PDF: absent at `C:/Users/wangz/Desktop/82.pdf`.
- GitHub: `https://github.com/Jason-Wang313/82_planner_recoverability_scores`.

## Decision

Final decision: KILL_ARCHIVE.

The expanded paper is a materially stronger negative diagnostic, but it should not be submitted to ICLR main. The proposed recoverability score loses to the strongest learned baseline, fails ablation necessity, fails fixed-risk coverage, fails maximum combined stress dominance, and lacks real robot or accepted high-fidelity external benchmark evidence.
