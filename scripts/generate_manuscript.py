import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"


METHOD_LABELS = {
    "nominal_shortest_plan": "Nominal",
    "risk_averse_plan": "Risk-averse",
    "robust_margin_planner": "Robust margin",
    "expected_cost_replanner": "Expected cost",
    "contingent_replanner": "Contingent",
    "receding_horizon_replanner": "RH replanner",
    "conformal_failure_filter": "Conformal filter",
    "learned_failure_classifier": "Learned risk",
    "learned_expected_utility": "Learned EU",
    "branch_entropy_planner": "Branch entropy",
    "cvar_recovery_planner": "CVaR recovery",
    "recoverability_score_planner_v5": "Recover-v5",
    "oracle_recoverability_upper_bound": "Oracle",
}

PLOT_METHODS = [
    "nominal_shortest_plan",
    "risk_averse_plan",
    "robust_margin_planner",
    "contingent_replanner",
    "conformal_failure_filter",
    "learned_failure_classifier",
    "learned_expected_utility",
    "cvar_recovery_planner",
    "recoverability_score_planner_v5",
    "oracle_recoverability_upper_bound",
]


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ascii_clean(text):
    text = (text or "").replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'")
    return text.encode("ascii", "ignore").decode("ascii")


def tex_escape(text):
    text = ascii_clean(str(text))
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def metric_lookup(rows, split, method, metric):
    for row in rows:
        if row.get("split") == split and row.get("method") == method and row.get("metric") == metric:
            return float(row["mean"]), float(row["ci95"])
    return 0.0, 0.0


def fmt_pm(mean, ci):
    return f"{mean:.3f} +/- {ci:.3f}"


def count_rows(name):
    return len(read_csv(RESULTS / name))


def bib_key(i):
    return f"pool82_{i:02d}"


def write_references():
    rows = read_csv(DOCS / "deep_read_250.csv")[:34]
    entries = []
    for i, row in enumerate(rows, start=1):
        key = bib_key(i)
        title = tex_escape(row.get("title", "Untitled prior work"))
        authors = ascii_clean(row.get("authors") or "Local Prior Work Pool")
        authors = " and ".join([tex_escape(a.strip()) for a in re.split(r";", authors) if a.strip()]) or "Local Prior Work Pool"
        year = ascii_clean(row.get("year") or "n.d.")
        venue = tex_escape(row.get("venue") or "prior-work pool")
        link = tex_escape(row.get("doi") or row.get("url") or row.get("arxiv_id") or "local pool record")
        entries.append(
            "\n".join(
                [
                    f"@misc{{{key},",
                    f"  author={{{authors}}},",
                    f"  title={{{title}}},",
                    f"  year={{{year}}},",
                    f"  note={{{venue}; {link}}}",
                    "}",
                ]
            )
        )
    (PAPER / "references.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return [bib_key(i) for i in range(1, len(rows) + 1)]


def longtable(header, rows, spec, caption, label):
    out = [
        r"\begin{center}",
        r"\scriptsize",
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{caption}}}\\label{{{label}}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endfirsthead",
        f"\\caption[]{{{caption} (continued)}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endhead",
    ]
    out.extend(rows)
    out.extend([r"\bottomrule", r"\end{longtable}", r"\normalsize", r"\end{center}"])
    return "\n".join(out)


def decision_gates(summary_text):
    gates = {}
    in_gate = False
    for line in summary_text.splitlines():
        if line.strip() == "Decision gates:":
            in_gate = True
            continue
        if in_gate and not line.strip():
            break
        if in_gate and ":" in line:
            k, v = line.split(":", 1)
            gates[k.strip()] = v.strip()
    return gates


def main():
    PAPER.mkdir(exist_ok=True)
    citation_keys = write_references()
    metrics = read_csv(RESULTS / "metrics.csv")
    hard_metrics = read_csv(RESULTS / "hard_aggregate_metrics.csv")
    hard_pairs = read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv")
    ablations = read_csv(RESULTS / "ablation_metrics.csv")
    ablation_seed = read_csv(RESULTS / "ablation_seed_metrics.csv")
    stress = read_csv(RESULTS / "stress_sweep.csv")
    fixed = read_csv(RESULTS / "fixed_risk_metrics.csv")
    fixed_seed = read_csv(RESULTS / "fixed_risk_seed_metrics.csv")
    negative = read_csv(RESULTS / "negative_cases.csv")
    prior = read_csv(DOCS / "deep_read_250.csv")[:28]
    summary_text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    gates = decision_gates(summary_text)

    prop_hard = metric_lookup(hard_metrics, "hard_regime_aggregate", "recoverability_score_planner_v5", "goal_success")
    best_ref = gates.get("best_reference", "learned_expected_utility")
    best_ref_label = METHOD_LABELS.get(best_ref, best_ref)
    best_ref_hard = metric_lookup(hard_metrics, "hard_regime_aggregate", best_ref, "goal_success")

    lines = []
    lines.extend(
        [
            r"\documentclass{article}",
            r"\usepackage{iclr2026_conference,times}",
            r"\input{math_commands.tex}",
            r"\usepackage{hyperref}",
            r"\usepackage{url}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{array}",
            r"\usepackage{longtable}",
            r"\usepackage{xcolor}",
            r"\hypersetup{colorlinks=false,pdfborder={0 0 1.6},citebordercolor={0 1 0},linkbordercolor={1 0.55 0},urlbordercolor={0 0.45 1}}",
            r"\graphicspath{{../figures/}}",
            r"\newcommand{\methodname}{recoverability-score planner v5}",
            r"\title{Planner Recoverability Scores Under Physical Deviation:\\An Expanded Negative ICLR-Main Readiness Audit}",
            r"\author{Anonymous Authors}",
            r"\begin{document}",
            r"\maketitle",
            r"\begin{abstract}",
            (
                "This paper asks whether task-and-motion plans should be scored by calibrated recoverability under physical deviation, not only by nominal feasibility or expected cost. "
                f"We rebuild the original archive into a frozen v5 audit with {count_rows('rollouts.csv'):,} main rollouts, {count_rows('ablation_rollouts.csv'):,} ablation rollouts, "
                f"{count_rows('stress_sweep_raw.csv'):,} stress rollouts, {count_rows('fixed_risk_raw.csv'):,} fixed-risk rollouts, and {count_rows('negative_cases.csv')} retained negative cases. "
                f"The expanded method reaches {fmt_pm(*prop_hard)} hard-regime aggregate goal success, but the strongest non-oracle baseline, {tex_escape(best_ref_label)}, reaches {fmt_pm(*best_ref_hard)}. "
                "The paired lower confidence bound versus that baseline is negative, central ablations match or beat the full score, fixed-risk coverage collapses at the 0.05 budget, and maximum combined stress is dominated by learned expected utility. "
                "The correct terminal decision is therefore \\textbf{KILL/ARCHIVE}: the recoverability idea remains interesting, but this repository still lacks the evidence needed for an ICLR main-conference submission."
            ),
            r"\end{abstract}",
        ]
    )

    lines.extend(
        [
            r"\section{Terminal Decision}",
            (
                "\\textbf{Decision: KILL/ARCHIVE for ICLR main.} "
                "The v5 rebuild is much stronger than the old archive: it adds a calibrated recoverability certificate, a larger benchmark, learned expected-utility and fixed-risk baselines, paired hard-regime statistics, two hard ablation splits, six stress axes, and explicit negative cases. "
                "Those additions make the paper more useful, but they do not rescue the central claim. "
                f"On the predefined hard-regime aggregate, \\methodname{{}} reaches {fmt_pm(*prop_hard)}, while {tex_escape(best_ref_label)} reaches {fmt_pm(*best_ref_hard)}. "
                "Because the protocol was frozen before execution, this is not a tuning failure to hide; it is the result."
            ),
            (
                "The archive is valuable precisely because it refuses to optimize for pretty results. "
                "It records that nominal feasibility is inadequate, but also that the proposed recoverability score is not yet a decisive alternative to learned expected utility or calibrated risk filtering. "
                "A future version would need real robot or recognized high-fidelity benchmark evidence, external baselines, and a learned or certified score that survives the ablation and fixed-risk gates."
            ),
            r"\section{Problem Setting}",
            (
                "A task-and-motion planner often chooses among plans that look similar in nominal feasibility but differ sharply after contact, slip, sensing dropout, or hidden mode shifts. "
                "A direct shortcut may be short and feasible until a small deviation leaves the robot wedged in a narrow passage. "
                "A conservative route may avoid the deviation but consume the whole budget. "
                "A contingency branch may be longer but keeps an executable recovery route available. "
                "The recoverability thesis says that these alternatives should be represented explicitly rather than averaged into a single scalar uncertainty term."
            ),
            (
                "This thesis sits near task-and-motion planning, robust motion planning, feasibility prediction, contingent planning, and learning-guided search. "
                f"The hostile prior-work pool includes incremental constraint-based TAMP \\citep{{{citation_keys[0]}}}, sketch decompositions \\citep{{{citation_keys[2]}}}, geometric TAMP learning \\citep{{{citation_keys[3]}}}, score-space guidance \\citep{{{citation_keys[7]}}}, sequence feasibility prediction \\citep{{{citation_keys[11]}}}, and robust feedback planning \\citep{{{citation_keys[17]}}}. "
                "These papers make weak claims easy to attack: if recoverability is just another risk or learned feasibility score, the contribution disappears."
            ),
            r"\section{Recoverability Certificates}",
            (
                "For an episode $e$ and candidate plan $p$, let $f_p$ denote the probability of a physical deviation, $r_p$ the probability that a deviation is recoverable, $t_p$ the probability of an irreversible trap, $d_p$ the probability of damage, $c_p$ the nominal cost, $k_p$ the expected recovery cost, and $B_e$ the execution budget. "
                "The recoverable-success term is $f_p(1-t_p)r_p$, while nominal survival is $1-f_p$. "
                "The proposed score tests whether a planner should prefer plans with a larger recoverable-success term and lower irreversible-risk term even when their nominal cost is higher."
            ),
            (
                "\\textbf{Definition 1 (recoverability certificate).} "
                "A recoverability certificate is a tuple $(\\hat f_p,\\hat r_p,\\hat t_p,\\hat d_p,\\hat k_p,h_p,\\epsilon_p)$ containing predicted deviation, recovery, trap, damage, recovery cost, branch entropy, and a calibration residual upper bound. "
                "The certificate is not a proof of robot safety; it is a compact local model of what the planner believes can still be recovered after execution leaves the nominal path."
            ),
            (
                "\\textbf{Lemma 1 (calibrated unsafe upper bound).} "
                "If the held-out residual satisfies $u_p-\\hat u_p \\leq \\epsilon$ for unsafe value $u_p=t_p+d_p+f_p(1-r_p)$, then $\\hat u_p+\\epsilon$ is a conservative upper bound on the unsafe value for that calibration population. "
                "The v5 score uses this bound as a penalty and the fixed-risk experiment uses it as an abstention rule. "
                "The lemma only transfers as far as the calibration population transfers; the fixed-risk collapse below shows why this limitation matters."
            ),
            (
                "\\textbf{Proposition 1 (recoverability dominance under equal nominal terms).} "
                "Consider two plans with equal nominal cost and equal predicted deviation probability. "
                "If one plan has weakly higher predicted recovery success, weakly lower trap and damage probabilities, and weakly larger branch entropy, then the v5 score weakly prefers it. "
                "This is a design property, not an empirical guarantee. "
                "The ablation section tests whether the property actually helps when learned baselines can infer expected utility directly."
            ),
            (
                "\\textbf{Failure mode.} "
                "If recovery cost, trap probability, and damage probability are not separately identifiable from the local observations, recoverability degenerates into ordinary risk avoidance. "
                "That degeneration is visible when removing budget slack, damage penalties, or expected-utility terms improves success. "
                "The v5 paper therefore treats ablations as a central falsification test rather than a decorative appendix."
            ),
            r"\section{Frozen Experimental Protocol}",
            (
                "The protocol was written before execution in \\texttt{docs/paper82\\_expanded\\_submission\\_plan\\_20260621.md}. "
                "The main evaluation uses 10 seeds, 9 splits, 64 test episodes per split and seed, 13 methods, and 74,880 main rollouts. "
                "The hard-regime aggregate combines all non-easy splits: narrow passages, object slip, irreversible commitment, sensor dropout, tight budgets, latent modes, adversarial compound shifts, and combined hard shifts."
            ),
            (
                "The strongest non-oracle baselines are intentionally uncomfortable: learned risk classification, learned expected utility, CVaR recovery planning, conformal failure filtering, contingent replanning, and robust-margin planning. "
                "The protocol also includes a high-information oracle as a ceiling. "
                "The decision gate marks \\texttt{STRONG\\_REVISE} only if v5 beats the strongest non-oracle baseline by at least 0.03 absolute hard-regime success, has a positive paired lower confidence bound, does not worsen safety, passes ablation necessity, preserves fixed-risk coverage at budget 0.05, and is not dominated at maximum combined stress."
            ),
        ]
    )

    hard_rows = []
    for method in PLOT_METHODS:
        success = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "goal_success")
        safety = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "safety_utility")
        trap = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "irreversible_failure")
        damage = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "damage")
        cost = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "total_cost")
        hard_rows.append(
            f"{tex_escape(METHOD_LABELS[method])} & {fmt_pm(*success)} & {fmt_pm(*safety)} & {trap[0]:.4f} & {damage[0]:.4f} & {cost[0]:.3f}\\\\"
        )
    lines.extend(
        [
            r"\section{Main Hard-Regime Results}",
            (
                "Table~\\ref{tab:hard-main} is the central result. "
                "Recover-v5 is better than the older contingent and CVaR-style hand-built scores, but it loses to learned expected utility and learned risk. "
                "This is not a small presentation issue: the strongest learned baseline wins all 10 paired hard-aggregate seeds on goal success."
            ),
            longtable(
                r"Method & Goal success & Safety utility & Irrev. & Damage & Cost",
                hard_rows,
                r"p{0.23\linewidth}ccccc",
                "Hard-regime aggregate over eight non-easy splits.",
                "tab:hard-main",
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{recoverability_success.png}",
            r"\caption{Hard-regime aggregate goal success. The proposed method is not the best non-oracle method.}",
            r"\label{fig:hard-success}",
            r"\end{figure}",
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{recoverability_failures.png}",
            r"\caption{Irreversible and damage failures on the hard aggregate. Safety is low in absolute terms, but the learned expected-utility baseline remains stronger overall.}",
            r"\label{fig:failures}",
            r"\end{figure}",
        ]
    )

    pair_rows = []
    for row in hard_pairs:
        if row["reference"] == best_ref:
            pair_rows.append(
                f"{tex_escape(row['metric'])} & {row['mean_diff']} & {row['ci95']} & {row['lower95']} & {row['target_better_seeds']}/{row['seeds']}\\\\"
            )
    lines.extend(
        [
            r"\section{Paired Hard-Aggregate Test}",
            (
                f"The predefined paired test compares Recover-v5 with the strongest non-oracle method selected by hard-regime aggregate success, {tex_escape(best_ref_label)}. "
                "The lower confidence bound is negative for goal success and safety utility, so the positive-paper claim fails under paired evidence."
            ),
            longtable(
                r"Metric & Mean diff & CI95 & Lower95 & Better seeds",
                pair_rows,
                r"p{0.28\linewidth}cccc",
                f"Paired seed differences for Recover-v5 minus {tex_escape(best_ref_label)}.",
                "tab:paired",
            ),
        ]
    )

    ablation_rows = []
    for row in ablations:
        ablation_rows.append(
            f"{tex_escape(row['split'])} & {tex_escape(row['ablation'])} & {row['goal_success']} & {row['ci95_success']} & {row['irreversible_failure']} & {row['damage']} & {row['safety_utility']}\\\\"
        )
    lines.extend(
        [
            r"\section{Ablations}",
            (
                "The ablation test is the harshest mechanism test. "
                "On combined hard shift, removing budget slack improves success from 0.836 to 0.855 and improves safety utility. "
                "On adversarial compound shift, removing the damage penalty, removing branch entropy, and expected-utility-only all match or beat the full score. "
                "That means the score is not yet a clean decomposition of recoverability; some terms are compensating for misspecification rather than carrying necessary mechanism information."
            ),
            longtable(
                r"Split & Ablation & Success & CI95 & Irrev. & Damage & Safety utility",
                ablation_rows,
                r"p{0.20\linewidth}p{0.26\linewidth}ccccc",
                "Ablations on combined hard shift and adversarial compound shift.",
                "tab:ablations",
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{recoverability_ablation.png}",
            r"\caption{Combined hard-shift ablations. Central removals do not consistently degrade the method.}",
            r"\label{fig:ablation}",
            r"\end{figure}",
        ]
    )

    stress_focus = [r for r in stress if r["stress_axis"] == "combined"]
    stress_rows = []
    for row in stress_focus:
        stress_rows.append(
            f"{row['stress_level']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['goal_success']} & {row['ci95_success']} & {row['irreversible_failure']} & {row['damage']} & {row['safety_utility']}\\\\"
        )
    lines.extend(
        [
            r"\section{Stress Tests}",
            (
                "The stress sweep exposes whether recoverability helps when deviations, traps, sensing uncertainty, and budget pressure rise together. "
                "At the maximum combined stress level, Recover-v5 reaches 0.516 success, while learned expected utility reaches 0.588 and the oracle reaches 0.625. "
                "The method therefore fails the maximum-stress dominance gate."
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{recoverability_stress_sweep.png}",
            r"\caption{Combined stress sweep across seven levels. Recover-v5 does not dominate the learned expected-utility baseline at the hardest level.}",
            r"\label{fig:stress}",
            r"\end{figure}",
            longtable(
                r"Level & Method & Success & CI95 & Irrev. & Damage & Safety utility",
                stress_rows,
                r"cp{0.25\linewidth}ccccc",
                "Combined stress sweep.",
                "tab:stress-combined",
            ),
        ]
    )

    fixed_rows = []
    for row in fixed:
        fixed_rows.append(
            f"{tex_escape(row['split'])} & {row['risk_budget']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['coverage']} & {row['fixed_risk_success']} & {row['executed_success']} & {row['false_safe_rate']}\\\\"
        )
    lines.extend(
        [
            r"\section{Fixed-Risk Deployment}",
            (
                "A paper about recoverability must answer a deployment question: can it execute only when the risk of irreversible or damaging failure is below a target budget? "
                "At budget 0.05, all learned and recoverability methods abstain on both hard fixed-risk splits; only the oracle maintains meaningful coverage. "
                "This is a severe limitation. "
                "The calibrated upper bound is conservative enough to avoid false-safe execution, but so conservative that it removes practical coverage."
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.96\linewidth]{recoverability_fixed_risk.png}",
            r"\caption{Fixed-risk deployment at budget 0.05 on combined hard shift. Non-oracle coverage collapses.}",
            r"\label{fig:fixed-risk}",
            r"\end{figure}",
            longtable(
                r"Split & Budget & Method & Coverage & Fixed success & Executed success & False-safe",
                fixed_rows,
                r"p{0.19\linewidth}cp{0.20\linewidth}cccc",
                "Fixed-risk deployment over two hard splits and four budgets.",
                "tab:fixed-risk",
            ),
        ]
    )

    neg_rows = []
    for row in negative:
        neg_rows.append(
            f"{tex_escape(row['source'])} & {tex_escape(row['split'])} & {tex_escape(row['method'])} & {tex_escape(row['plan_type'])} & {tex_escape(row['failure_label'])} & {tex_escape(row['lesson'])}\\\\"
        )
    lines.extend(
        [
            r"\section{Negative Cases}",
            (
                "The negative cases are not anecdotes selected to flatter the method. "
                "They include v5 failures, strong-baseline failures, ablation counterexamples, fixed-risk false-safe examples when present, and fixed-risk abstentions. "
                "They make the reviewer-facing limitation concrete: recoverability is useful only if the score can separate recoverable deviations from irreversible ones without abstaining everywhere."
            ),
            longtable(
                r"Source & Split & Method & Plan & Outcome & Lesson",
                neg_rows,
                r"p{0.15\linewidth}p{0.16\linewidth}p{0.18\linewidth}p{0.13\linewidth}p{0.15\linewidth}p{0.23\linewidth}",
                "Retained negative cases.",
                "tab:negative-cases",
            ),
        ]
    )

    split_rows = []
    for split in sorted({r["split"] for r in metrics}):
        for method in [
            "nominal_shortest_plan",
            "risk_averse_plan",
            "robust_margin_planner",
            "expected_cost_replanner",
            "contingent_replanner",
            "receding_horizon_replanner",
            "conformal_failure_filter",
            "learned_failure_classifier",
            "learned_expected_utility",
            "branch_entropy_planner",
            "cvar_recovery_planner",
            "recoverability_score_planner_v5",
            "oracle_recoverability_upper_bound",
        ]:
            success = metric_lookup(metrics, split, method, "goal_success")
            safety = metric_lookup(metrics, split, method, "safety_utility")
            trap = metric_lookup(metrics, split, method, "irreversible_failure")
            damage = metric_lookup(metrics, split, method, "damage")
            split_rows.append(
                f"{tex_escape(split)} & {tex_escape(METHOD_LABELS[method])} & {fmt_pm(*success)} & {fmt_pm(*safety)} & {trap[0]:.4f} & {damage[0]:.4f}\\\\"
            )
    full_pair_rows = []
    for row in hard_pairs:
        full_pair_rows.append(
            f"{tex_escape(METHOD_LABELS.get(row['reference'], row['reference']))} & {tex_escape(row['metric'])} & {row['mean_diff']} & {row['ci95']} & {row['lower95']} & {row['target_better_seeds']}/{row['seeds']}\\\\"
        )
    full_stress_rows = []
    for row in stress:
        full_stress_rows.append(
            f"{tex_escape(row['stress_axis'])} & {row['stress_level']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['goal_success']} & {row['ci95_success']} & {row['irreversible_failure']} & {row['damage']} & {row['safety_utility']}\\\\"
        )
    ablation_seed_rows = []
    for row in ablation_seed:
        ablation_seed_rows.append(
            f"{tex_escape(row['split'])} & {tex_escape(row['method'])} & {row['seed']} & {row['episodes']} & {row['goal_success']} & {row['irreversible_failure']} & {row['damage']} & {row['safety_utility']}\\\\"
        )
    fixed_seed_rows = []
    for row in fixed_seed:
        fixed_seed_rows.append(
            f"{tex_escape(row['split'])} & {row['risk_budget']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['seed']} & {row['coverage']} & {row['fixed_risk_success']} & {row['executed_success']} & {row['false_safe_rate']}\\\\"
        )
    prior_rows = []
    for i, row in enumerate(prior, start=1):
        prior_rows.append(
            f"\\citep{{{bib_key(i)}}} & {tex_escape(row.get('title', ''))} & {tex_escape(row.get('year', ''))} & {tex_escape(row.get('venue', ''))} & {tex_escape(row.get('hostile_score', ''))}\\\\"
        )
    lines.extend(
        [
            r"\section{Reviewer Attack Surface}",
            (
                "A hostile reviewer can make at least four fair attacks. "
                "First, learned expected utility already absorbs the same signals and wins. "
                "Second, fixed-risk abstention shows that the calibration story is not deployable yet. "
                "Third, ablations reveal that some score terms are not necessary. "
                "Fourth, the entire result remains local and generated, with no hardware or recognized high-fidelity simulator validation. "
                "The manuscript should invite these attacks rather than pretending they do not exist."
            ),
            (
                "The strongest defense is modest: the repository now provides a reproducible failure analysis at meaningful scale. "
                "It separates a plausible robotics hypothesis from an unsupported submission claim. "
                "That is useful for deciding what to build next, but it is not enough for ICLR main."
            ),
            r"\section{Reproducibility}",
            r"\begin{verbatim}",
            r"python src\run_experiment.py",
            r"python scripts\generate_manuscript.py",
            r"cd paper",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"bibtex main",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"python ..\scripts\validate_submission_artifacts.py",
            r"\end{verbatim}",
            (
                "The canonical numbered PDF is \\texttt{C:/Users/wangz/Downloads/82.pdf}. "
                "No PDF should be copied to the visible Desktop. "
                "The validator checks row counts, page count, link settings, unresolved references, artifact placement, and SHA256."
            ),
            r"\section{Limitations}",
            (
                "The limitations are not boilerplate. "
                "The local generator may not capture contact dynamics, perception failure, or planner engineering constraints of real systems. "
                "The learned baselines are still lightweight ridge models, so stronger neural or TAMP-specific baselines could widen the gap further. "
                "The oracle uses hidden probabilities and exists only as a ceiling. "
                "The fixed-risk calibration is population-bound and fails to provide useful non-oracle coverage at the strict budget. "
                "The related-work pool is broad but still needs manual expert vetting before any real submission."
            ),
            r"\section{Conclusion}",
            (
                "Recoverability remains a good robotics question: plans should be judged by what remains possible after the world pushes them off the nominal path. "
                "But the v5 evidence says this particular hand-designed recoverability score is not yet the answer. "
                "A learned expected-utility baseline wins the hard aggregate, ablations expose misspecification, fixed-risk coverage collapses, and maximum stress is dominated. "
                "The honest action is to archive Paper 82 as a strong negative diagnostic and move to the next paper."
            ),
            r"\appendix",
            r"\section{Full Split Metrics}",
            longtable(
                r"Split & Method & Success & Safety utility & Irrev. & Damage",
                split_rows,
                r"p{0.22\linewidth}p{0.22\linewidth}cccc",
                "Per-split metrics for all methods.",
                "tab:split-metrics",
            ),
            r"\section{Full Hard-Aggregate Pairwise Table}",
            (
                "The main text reports the paired comparison against the strongest non-oracle baseline. "
                "The full paired table is included here to make clear that the decision does not depend on selectively choosing one reference or one metric."
            ),
            longtable(
                r"Reference & Metric & Mean diff & CI95 & Lower95 & Better seeds",
                full_pair_rows,
                r"p{0.22\linewidth}p{0.22\linewidth}cccc",
                "All hard-regime aggregate paired seed differences for Recover-v5.",
                "tab:full-pairwise",
            ),
            r"\section{Full Stress Sweep Across All Axes}",
            (
                "The main text focuses on the combined stress axis because it is the hardest single diagnostic. "
                "For auditability, Table~\\ref{tab:full-stress} reports every predefined stress axis, level, method, and aggregate metric."
            ),
            longtable(
                r"Axis & Level & Method & Success & CI95 & Irrev. & Damage & Safety utility",
                full_stress_rows,
                r"p{0.13\linewidth}cp{0.20\linewidth}ccccc",
                "All stress axes, levels, and methods.",
                "tab:full-stress",
            ),
            r"\section{Ablation Seed-Level Metrics}",
            (
                "The ablation gate fails at the aggregate level, but seed-level rows are retained so that the failure cannot be dismissed as a table-generation artifact. "
                "These rows are generated directly from \\texttt{ablation\\_seed\\_metrics.csv}."
            ),
            longtable(
                r"Split & Ablation & Seed & Episodes & Success & Irrev. & Damage & Safety utility",
                ablation_seed_rows,
                r"p{0.16\linewidth}p{0.26\linewidth}cccccc",
                "Seed-level ablation metrics.",
                "tab:ablation-seeds",
            ),
            r"\section{Fixed-Risk Seed-Level Metrics}",
            (
                "Fixed-risk coverage is the most submission-damaging result: non-oracle methods abstain at the strict 0.05 budget. "
                "The seed-level table below shows this is consistent across seeds rather than an averaging artifact."
            ),
            longtable(
                r"Split & Budget & Method & Seed & Coverage & Fixed success & Executed success & False-safe",
                fixed_seed_rows,
                r"p{0.17\linewidth}cp{0.18\linewidth}ccccc",
                "Seed-level fixed-risk metrics.",
                "tab:fixed-risk-seeds",
            ),
            r"\section{Full Prior-Work Pressure Table}",
            (
                "Table~\\ref{tab:prior-work} lists the highest-ranked hostile prior-work records used to bound the novelty claim. "
                "The point is not to claim that all are direct baselines; the point is to make the surrounding field visible enough that generic uncertainty or feasibility-score claims cannot pass as novelty."
            ),
            longtable(
                r"Citation & Title & Year & Venue & Hostile score",
                prior_rows,
                r"p{0.12\linewidth}p{0.42\linewidth}cp{0.25\linewidth}c",
                "Hostile prior-work pressure from the local deep-read pool.",
                "tab:prior-work",
            ),
            r"\bibliographystyle{iclr2026_conference}",
            r"\bibliography{references}",
            r"\end{document}",
        ]
    )
    (PAPER / "main.tex").write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'} and {PAPER / 'references.bib'}")


if __name__ == "__main__":
    main()
