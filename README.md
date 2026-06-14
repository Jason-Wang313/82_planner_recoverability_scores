# 82 Planner Recoverability Scores

Submission-hardening version: v4

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

This repository contains a reproducible local evidence audit for the research bet:

> Score robot plans by recoverability under physical deviation, not just nominal feasibility.

The v4 rebuild adds an executable benchmark, baselines, ablations, stress sweeps, figures, and an updated paper. The idea remains useful, but the empirical result is negative: on the combined hard-shift split, the recoverability-score planner reaches `0.85034 +/- 0.04163` goal success, while a learned failure classifier reaches `0.87755 +/- 0.04128`. The paired goal-success gain over a contingent replanner is only `0.00680 +/- 0.02828`, and two ablations improve over the full score.

## Why This Is Archived

- The evidence is a deterministic local benchmark, not real-robot or high-fidelity simulator evidence.
- The proposed score does not beat the strongest learned baseline on the main hard split.
- Ablations expose objective misspecification: removing the irreversible-trap penalty or failure-probability term improves success.

## Reproduce

```powershell
python src\run_experiment.py
```

The runner writes:

- `results/rollouts.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep.csv`
- `results/negative_cases.csv`
- `results/summary.txt`
- `figures/recoverability_*.png`

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/82.pdf`
