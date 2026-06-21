# Submission Version Log

## v1 - Generated Draft
- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening
- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/82.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive
- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats are not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Recoverability Benchmark Rebuild

- Added `docs/paper82_rebuild_plan.md` before executing the rebuild.
- Replaced the toy scaffold with an executable local task-and-motion recoverability benchmark.
- Implemented nominal, risk-averse, expected-cost, robust-margin, contingent replanning, learned failure classifier, recoverability-score, and oracle baselines.
- Ran seven seeds, 11,760 main rollout rows, 2,058 ablation rollout rows, and 25,200 stress-sweep rows.
- Produced figures, paired statistics, ablations, stress sweeps, negative cases, and a negative evidence manuscript.
- Terminal decision: KILL_ARCHIVE.

## v4 Continuation Audit - 2026-06-15

- Added `docs/paper82_iclr_submission_execution_plan_20260615.md` before rerunning the evidence gate.
- Recompiled and reran the full deterministic recoverability benchmark without reducing seeds, baselines, ablations, stress levels, or row counts.
- Rechecked CSV integrity, seed/method/split/ablation/stress coverage, paired statistics, irreversible/damage tradeoffs, ablations, stress behavior, PDF logs, Downloads-only placement, Desktop exclusion, and public GitHub status.
- Cleaned BibTeX placeholder entries by adding explicit authors and changed fragile `[h]` floats to `[tbp]` before rebuilding the PDF.
- Verified `C:/Users/wangz/Downloads/82.pdf` SHA256 `CB79882533BE0A5DA119C783411BE47C2534307987372ADD8B39C7509595140E`.
- Terminal decision remains: KILL_ARCHIVE.

## v5 Expanded-Standard Audit - 2026-06-21

- Added `docs/paper82_expanded_submission_plan_20260621.md` before changing code.
- Replaced the v4 runner with a 10-seed, nine-split, thirteen-method CPU-only audit.
- Added hard-regime aggregate seed metrics, hard-regime paired tests, expanded ablations, six-axis stress sweeps, fixed-risk deployment budgets, and negative cases.
- Added `scripts/generate_manuscript.py` and `scripts/validate_submission_artifacts.py`.
- Generated a 28-page ICLR-style KILL_ARCHIVE manuscript with bright boxed clickable citations and evidence appendices.
- Verified `C:/Users/wangz/Downloads/82.pdf` SHA256 `D32F6F11DA77897EC8671FAE3D9860B1474AD6A5091A9F7034BDB33F77BB6249`; `C:/Users/wangz/Desktop/82.pdf` is absent.
- Terminal decision remains: KILL_ARCHIVE.
