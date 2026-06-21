# 82 Planner Recoverability Scores

Submission-hardening version: v5-expanded

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

This repository contains a reproducible local evidence audit for the research bet:

> Score robot plans by recoverability under physical deviation, not just nominal feasibility.

The v5-expanded rebuild adds a plan-first protocol, a calibrated recoverability-certificate score, stronger learned and planning baselines, hard-regime aggregate paired tests, two-split ablations, six-axis stress sweeps, fixed-risk deployment checks, negative cases, generated BibTeX, and a 28-page ICLR-style PDF with bright boxed clickable citations.

## Why This Is Archived

- The evidence is still CPU-only local/generated evidence, not real robot or accepted high-fidelity benchmark evidence.
- On the hard-regime aggregate, `recoverability_score_planner_v5` reaches `0.88711 +/- 0.00776` goal success, while `learned_expected_utility` reaches `0.92305 +/- 0.00917`.
- The paired lower confidence bound versus `learned_expected_utility` is negative: goal-success diff `-0.03594`, lower95 `-0.04882`, with `0/10` better seeds.
- The ablation gate fails: removing budget slack improves combined-hard success, and damage/branch/expected-utility ablations match or beat the full method on adversarial compound shift.
- The fixed-risk gate fails: non-oracle coverage at the `0.05` false-safe budget collapses to zero on both hard fixed-risk splits.
- The maximum combined-stress gate fails: v5 reaches `0.51562`, while `learned_expected_utility` reaches `0.58750`.

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
Copy-Item -Force paper\main.pdf "$HOME\Downloads\82.pdf"
python scripts\validate_submission_artifacts.py
```

The runner writes:

- `results/rollouts.csv` with 74,880 main rollout rows.
- `results/ablation_rollouts.csv` with 16,000 ablation rows.
- `results/stress_sweep_raw.csv` with 94,080 stress rows.
- `results/fixed_risk_raw.csv` with 30,720 fixed-risk rows.
- `results/negative_cases.csv` with 24 retained negative cases.
- `figures/recoverability_*.png`.

Canonical local PDF: `C:/Users/wangz/Downloads/82.pdf`

Final PDF SHA256: `D32F6F11DA77897EC8671FAE3D9860B1474AD6A5091A9F7034BDB33F77BB6249`
