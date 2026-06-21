# Child Status 82

Current stage: 2026-06-21 expanded-standard v5 terminal
Last update: 2026-06-21 21:46:59 +08:00
PDF: C:/Users/wangz/Downloads/82.pdf
PDF pages: 28
PDF SHA256: D32F6F11DA77897EC8671FAE3D9860B1474AD6A5091A9F7034BDB33F77BB6249
GitHub: https://github.com/Jason-Wang313/82_planner_recoverability_scores
Submission-hardening version: v5-expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the 2026-06-21 expanded-standard plan-first audit rebuilt Paper 82 with a stronger calibrated recoverability score, 10 seeds, nine main splits, thirteen methods, hard-regime aggregates, paired statistics, ablations, six-axis stress sweeps, fixed-risk deployment checks, negative cases, generated manuscript/BibTeX, bright boxed citation settings, visual PDF QA, and artifact validation. The terminal decision remains KILL_ARCHIVE because `recoverability_score_planner_v5` reaches only `0.88711 +/- 0.00776` hard-regime aggregate goal success versus `0.92305 +/- 0.00917` for `learned_expected_utility`; the paired lower95 versus that baseline is `-0.04882`; ablations match or beat the full score; fixed-risk coverage at budget `0.05` is zero for non-oracle methods; maximum combined stress is dominated by learned expected utility; and no real robot or accepted high-fidelity external benchmark evidence exists.
