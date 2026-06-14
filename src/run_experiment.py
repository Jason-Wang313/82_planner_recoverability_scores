import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 82012026
SEEDS = list(range(7))
TEST_EPISODES_PER_SPLIT_SEED = 42
TRAIN_EPISODES_PER_SEED = 144
STRESS_EPISODES_PER_SEED = 24

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

METHODS = [
    "nominal_shortest_plan",
    "risk_averse_plan",
    "expected_cost_replanner",
    "robust_margin_planner",
    "contingent_replanner",
    "learned_failure_classifier",
    "recoverability_score_planner",
    "oracle_recoverability_upper_bound",
]

PLAN_TYPES = [
    "direct_shortcut",
    "robust_margin_route",
    "contingency_branch",
    "diagnostic_staging",
    "conservative_backoff",
]


@dataclass
class CandidatePlan:
    plan_type: str
    nominal_cost: float
    clearance: float
    manipulation_margin: float
    branch_depth: float
    diagnostic_value: float
    reversibility: float
    predicted_failure: float
    predicted_recovery: float
    predicted_recovery_cost: float
    predicted_trap: float
    predicted_damage: float
    true_failure: float
    true_recovery: float
    true_recovery_cost: float
    true_trap: float
    true_damage: float


@dataclass
class Episode:
    split: str
    seed: int
    episode_id: int
    nav_deviation: float
    manipulation_slip: float
    trap_pressure: float
    sensor_uncertainty: float
    clutter: float
    budget: float
    candidates: list


def stable_rng(*parts):
    acc = BASE_SEED
    for part in parts:
        if isinstance(part, str):
            for ch in part:
                acc = (acc * 131 + ord(ch)) % (2**32 - 1)
        else:
            acc = (acc * 131 + int(part)) % (2**32 - 1)
    return np.random.default_rng(acc)


def clip01(x):
    return float(np.clip(x, 0.01, 0.99))


def ci95(vals):
    vals = list(vals)
    if len(vals) <= 1:
        return 0.0
    mean = float(np.mean(vals))
    sd = math.sqrt(sum((x - mean) ** 2 for x in vals) / (len(vals) - 1))
    return 1.96 * sd / math.sqrt(len(vals))


def split_params(split, stress=0.0):
    if split == "train":
        return 0.24, 0.22, 0.18, 0.14, 0.18, 2.45
    if split == "open_easy":
        return 0.10, 0.10, 0.05, 0.08, 0.08, 2.55
    if split == "narrow_passage_shift":
        return 0.42 + 0.12 * stress, 0.16, 0.32 + 0.18 * stress, 0.18, 0.36, 2.30
    if split == "object_slip_shift":
        return 0.16, 0.46 + 0.18 * stress, 0.18, 0.18, 0.24, 2.28
    if split == "irreversible_commitment":
        return 0.24, 0.22, 0.55 + 0.15 * stress, 0.20, 0.30, 2.22
    if split == "combined_hard_shift":
        return 0.48 + 0.10 * stress, 0.46 + 0.12 * stress, 0.52 + 0.15 * stress, 0.34 + 0.10 * stress, 0.46, 2.18
    if split == "stress_navigation":
        return 0.12 + 0.55 * stress, 0.18, 0.20 + 0.30 * stress, 0.15, 0.24, 2.30
    if split == "stress_slip":
        return 0.18, 0.12 + 0.60 * stress, 0.22, 0.17, 0.25, 2.30
    if split == "stress_trap":
        return 0.22 + 0.20 * stress, 0.20, 0.10 + 0.70 * stress, 0.20, 0.34, 2.24
    if split == "stress_sensor":
        return 0.28, 0.28, 0.30, 0.06 + 0.48 * stress, 0.30, 2.28
    if split == "stress_combined":
        return 0.12 + 0.50 * stress, 0.12 + 0.50 * stress, 0.10 + 0.60 * stress, 0.08 + 0.38 * stress, 0.14 + 0.42 * stress, 2.48 - 0.34 * stress
    raise ValueError(split)


def candidate_template(plan_type):
    templates = {
        "direct_shortcut": (1.00, 0.22, 0.30, 0.05, 0.05, 0.18),
        "robust_margin_route": (1.62, 0.76, 0.68, 0.20, 0.12, 0.58),
        "contingency_branch": (1.72, 0.54, 0.56, 0.78, 0.22, 0.78),
        "diagnostic_staging": (1.66, 0.48, 0.54, 0.66, 0.82, 0.86),
        "conservative_backoff": (2.46, 0.88, 0.78, 0.35, 0.16, 0.90),
    }
    return templates[plan_type]


def make_candidate(plan_type, ep_rng, nav_deviation, manipulation_slip, trap_pressure, sensor_uncertainty, clutter):
    base_cost, clearance, margin, branch_depth, diagnostic, reversibility = candidate_template(plan_type)
    clearance = float(np.clip(clearance + ep_rng.normal(0.0, 0.045), 0.08, 0.96))
    margin = float(np.clip(margin + ep_rng.normal(0.0, 0.050), 0.08, 0.96))
    diagnostic = float(np.clip(diagnostic + ep_rng.normal(0.0, 0.040), 0.02, 0.96))
    reversibility = float(np.clip(reversibility + ep_rng.normal(0.0, 0.045), 0.02, 0.98))
    nominal_cost = float(max(0.70, base_cost + ep_rng.normal(0.0, 0.055) + 0.12 * clutter * (1.0 - clearance)))

    nav_fail = nav_deviation * (1.08 - clearance) + 0.10 * clutter
    slip_fail = manipulation_slip * (1.05 - margin) + 0.06 * (1.0 - diagnostic)
    true_failure = clip01(0.05 + 0.42 * nav_fail + 0.40 * slip_fail - 0.12 * diagnostic - 0.07 * branch_depth)
    true_trap = clip01(0.03 + trap_pressure * (1.10 - reversibility) * (1.05 - clearance) - 0.14 * branch_depth - 0.10 * diagnostic)
    true_recovery = clip01(0.16 + 0.40 * reversibility + 0.28 * branch_depth + 0.18 * diagnostic + 0.12 * clearance - 0.30 * true_trap)
    true_recovery_cost = float(max(0.15, 0.45 + 1.05 * (1.0 - reversibility) + 0.65 * clutter + 0.45 * true_trap - 0.32 * diagnostic))
    true_damage = clip01(0.03 + 0.42 * true_trap + 0.30 * slip_fail + 0.10 * (1.0 - margin) - 0.18 * diagnostic)

    noise = sensor_uncertainty
    predicted_failure = clip01(true_failure + ep_rng.normal(0.0, 0.10 + 0.22 * noise))
    predicted_trap = clip01(true_trap + ep_rng.normal(0.0, 0.08 + 0.18 * noise))
    predicted_recovery = clip01(true_recovery + ep_rng.normal(0.0, 0.09 + 0.18 * noise))
    predicted_recovery_cost = float(max(0.05, true_recovery_cost + ep_rng.normal(0.0, 0.12 + 0.25 * noise)))
    predicted_damage = clip01(true_damage + ep_rng.normal(0.0, 0.08 + 0.18 * noise))

    return CandidatePlan(
        plan_type=plan_type,
        nominal_cost=nominal_cost,
        clearance=clearance,
        manipulation_margin=margin,
        branch_depth=branch_depth,
        diagnostic_value=diagnostic,
        reversibility=reversibility,
        predicted_failure=predicted_failure,
        predicted_recovery=predicted_recovery,
        predicted_recovery_cost=predicted_recovery_cost,
        predicted_trap=predicted_trap,
        predicted_damage=predicted_damage,
        true_failure=true_failure,
        true_recovery=true_recovery,
        true_recovery_cost=true_recovery_cost,
        true_trap=true_trap,
        true_damage=true_damage,
    )


def make_episode(split, seed, episode_id, stress=0.0):
    rng = stable_rng("episode", split, seed, episode_id, int(1000 * stress))
    nav, slip, trap, sensor, clutter, budget = split_params(split, stress)
    nav = float(np.clip(nav + rng.normal(0.0, 0.035), 0.02, 0.95))
    slip = float(np.clip(slip + rng.normal(0.0, 0.035), 0.02, 0.95))
    trap = float(np.clip(trap + rng.normal(0.0, 0.035), 0.01, 0.95))
    sensor = float(np.clip(sensor + rng.normal(0.0, 0.025), 0.02, 0.80))
    clutter = float(np.clip(clutter + rng.normal(0.0, 0.035), 0.02, 0.95))
    budget = float(max(1.75, budget + rng.normal(0.0, 0.08)))
    candidates = [make_candidate(plan_type, rng, nav, slip, trap, sensor, clutter) for plan_type in PLAN_TYPES]
    return Episode(split, seed, episode_id, nav, slip, trap, sensor, clutter, budget, candidates)


def feature_vector(plan):
    return np.array(
        [
            plan.nominal_cost,
            plan.clearance,
            plan.manipulation_margin,
            plan.branch_depth,
            plan.diagnostic_value,
            plan.reversibility,
            plan.predicted_failure,
            plan.predicted_recovery,
            plan.predicted_recovery_cost,
            plan.predicted_trap,
            plan.predicted_damage,
        ],
        dtype=float,
    )


def true_expected_utility(plan, budget):
    recoverable_success = plan.true_failure * (1.0 - plan.true_trap) * plan.true_recovery
    no_fail_success = 1.0 - plan.true_failure
    expected_success = no_fail_success + recoverable_success
    expected_cost = plan.nominal_cost + plan.true_failure * plan.true_recovery_cost
    overtime = max(0.0, expected_cost - budget)
    return expected_success - 0.28 * expected_cost - 0.90 * plan.true_damage - 1.05 * plan.true_trap - 0.65 * overtime


def predicted_recoverability_score(plan, budget, ablation=None):
    failure = plan.predicted_failure
    recovery = plan.predicted_recovery
    recovery_cost = plan.predicted_recovery_cost
    trap = plan.predicted_trap
    damage = plan.predicted_damage
    diagnostic = plan.diagnostic_value
    if ablation == "minus_failure_probability":
        failure = 0.35
    if ablation == "minus_recovery_success":
        recovery = 0.50
    if ablation == "minus_recovery_cost":
        recovery_cost = 0.60
    if ablation == "minus_irreversible_trap_penalty":
        trap = 0.04
    if ablation == "minus_diagnostic_value":
        diagnostic = 0.10
    if ablation == "risk_only_score":
        return -(failure + 1.25 * trap + 0.75 * damage + 0.08 * plan.nominal_cost)
    recoverable_success = failure * (1.0 - trap) * recovery
    no_fail_success = 1.0 - failure
    overtime = max(0.0, plan.nominal_cost + failure * recovery_cost - budget)
    return (
        no_fail_success
        + recoverable_success
        + 0.22 * diagnostic
        - 0.24 * plan.nominal_cost
        - 0.24 * failure * recovery_cost
        - 0.92 * trap
        - 0.72 * damage
        - 0.62 * overtime
    )


def train_learned_model(seed):
    rows = []
    targets = []
    for episode_id in range(TRAIN_EPISODES_PER_SEED):
        ep = make_episode("train", seed, episode_id)
        for plan in ep.candidates:
            rows.append(feature_vector(plan))
            targets.append(true_expected_utility(plan, ep.budget))
    x = np.asarray(rows, dtype=float)
    y = np.asarray(targets, dtype=float)
    mean = np.mean(x, axis=0)
    std = np.maximum(np.std(x, axis=0), 1e-6)
    xs = (x - mean) / std
    xs = np.c_[np.ones(len(xs)), xs]
    ridge = 0.05 * np.eye(xs.shape[1])
    ridge[0, 0] = 0.0
    weights = np.linalg.solve(xs.T @ xs + ridge, xs.T @ y)
    return {"mean": mean, "std": std, "weights": weights}


def predict_learned(model, plan):
    x = (feature_vector(plan) - model["mean"]) / model["std"]
    x = np.r_[1.0, x]
    return float(x @ model["weights"])


def choose_plan(ep, method, model=None, ablation=None):
    if method == "nominal_shortest_plan":
        return min(ep.candidates, key=lambda p: p.nominal_cost)
    if method == "risk_averse_plan":
        return min(ep.candidates, key=lambda p: p.predicted_failure + 1.25 * p.predicted_trap + 0.85 * p.predicted_damage + 0.05 * p.nominal_cost)
    if method == "expected_cost_replanner":
        return min(ep.candidates, key=lambda p: p.nominal_cost + p.predicted_failure * (p.predicted_recovery_cost + 1.4 * (1.0 - p.predicted_recovery)) + 1.2 * p.predicted_trap)
    if method == "robust_margin_planner":
        return max(ep.candidates, key=lambda p: 1.15 * p.clearance + 1.05 * p.manipulation_margin - 0.26 * p.nominal_cost - 0.35 * p.predicted_damage)
    if method == "contingent_replanner":
        return max(ep.candidates, key=lambda p: 0.55 * p.branch_depth + 0.35 * p.reversibility + p.predicted_recovery - p.predicted_failure - 0.85 * p.predicted_trap - 0.20 * p.nominal_cost)
    if method == "learned_failure_classifier":
        return max(ep.candidates, key=lambda p: predict_learned(model, p))
    if method == "recoverability_score_planner":
        return max(ep.candidates, key=lambda p: predicted_recoverability_score(p, ep.budget, ablation=ablation))
    if method == "oracle_recoverability_upper_bound":
        return max(ep.candidates, key=lambda p: true_expected_utility(p, ep.budget))
    raise ValueError(method)


def run_plan(ep, method, model=None, ablation=None):
    plan = choose_plan(ep, method, model=model, ablation=ablation)
    rng = stable_rng("rollout", ep.split, ep.seed, ep.episode_id, plan.plan_type)
    deviation = int(rng.random() < plan.true_failure)
    recovered = 0
    irreversible = 0
    damage = 0
    recovery_attempts = 0
    total_cost = plan.nominal_cost
    if deviation:
        irreversible = int(rng.random() < plan.true_trap)
        damage = int(rng.random() < plan.true_damage)
        if not irreversible:
            recovery_attempts = 1
            recovered = int(rng.random() < plan.true_recovery)
            total_cost += plan.true_recovery_cost
            if not recovered and rng.random() < 0.35:
                damage = 1
        else:
            if rng.random() < 0.45:
                damage = 1
    overtime = int(total_cost > ep.budget)
    goal_success = int((not deviation or recovered) and not irreversible and not damage and not overtime)
    if goal_success:
        failure_label = "success"
    elif irreversible:
        failure_label = "irreversible_trap"
    elif damage:
        failure_label = "damage_or_lost_object"
    elif overtime:
        failure_label = "budget_overrun"
    elif deviation and not recovered:
        failure_label = "unrecovered_deviation"
    else:
        failure_label = "failed_unknown"
    predicted_success = 1.0 - plan.predicted_failure * (1.0 - plan.predicted_recovery) - plan.predicted_trap - plan.predicted_damage
    calibration_error = abs(clip01(predicted_success) - goal_success)
    return {
        "split": ep.split,
        "seed": ep.seed,
        "episode_id": ep.episode_id,
        "method": method if ablation is None else ablation,
        "plan_type": plan.plan_type,
        "goal_success": goal_success,
        "deviation": deviation,
        "recovered": recovered,
        "irreversible_failure": irreversible,
        "damage": damage,
        "budget_overrun": overtime,
        "total_cost": f"{total_cost:.5f}",
        "recovery_attempts": recovery_attempts,
        "calibration_error": f"{calibration_error:.5f}",
        "failure_label": failure_label,
        "predicted_failure": f"{plan.predicted_failure:.5f}",
        "predicted_recovery": f"{plan.predicted_recovery:.5f}",
        "predicted_trap": f"{plan.predicted_trap:.5f}",
        "predicted_damage": f"{plan.predicted_damage:.5f}",
        "nav_deviation": f"{ep.nav_deviation:.5f}",
        "manipulation_slip": f"{ep.manipulation_slip:.5f}",
        "trap_pressure": f"{ep.trap_pressure:.5f}",
        "sensor_uncertainty": f"{ep.sensor_uncertainty:.5f}",
        "budget": f"{ep.budget:.5f}",
    }


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def dataset_row(ep):
    row = {
        "split": ep.split,
        "seed": ep.seed,
        "episode_id": ep.episode_id,
        "nav_deviation": f"{ep.nav_deviation:.5f}",
        "manipulation_slip": f"{ep.manipulation_slip:.5f}",
        "trap_pressure": f"{ep.trap_pressure:.5f}",
        "sensor_uncertainty": f"{ep.sensor_uncertainty:.5f}",
        "clutter": f"{ep.clutter:.5f}",
        "budget": f"{ep.budget:.5f}",
    }
    for plan in ep.candidates:
        prefix = plan.plan_type
        row[f"{prefix}_nominal_cost"] = f"{plan.nominal_cost:.5f}"
        row[f"{prefix}_true_failure"] = f"{plan.true_failure:.5f}"
        row[f"{prefix}_true_recovery"] = f"{plan.true_recovery:.5f}"
        row[f"{prefix}_true_trap"] = f"{plan.true_trap:.5f}"
        row[f"{prefix}_true_damage"] = f"{plan.true_damage:.5f}"
    return row


def aggregate_seed_metrics(rows, methods=METHODS):
    out = []
    for split in sorted({r["split"] for r in rows}):
        for method in methods:
            for seed in SEEDS:
                vals = [r for r in rows if r["split"] == split and r["method"] == method and int(r["seed"]) == seed]
                if not vals:
                    continue
                deviations = [r for r in vals if int(r["deviation"]) == 1]
                recovery_success = np.mean([int(r["recovered"]) for r in deviations]) if deviations else 1.0
                out.append({
                    "split": split,
                    "method": method,
                    "seed": seed,
                    "episodes": len(vals),
                    "goal_success": f"{np.mean([int(r['goal_success']) for r in vals]):.5f}",
                    "deviation_rate": f"{np.mean([int(r['deviation']) for r in vals]):.5f}",
                    "recovery_success": f"{recovery_success:.5f}",
                    "irreversible_failure": f"{np.mean([int(r['irreversible_failure']) for r in vals]):.5f}",
                    "damage": f"{np.mean([int(r['damage']) for r in vals]):.5f}",
                    "budget_overrun": f"{np.mean([int(r['budget_overrun']) for r in vals]):.5f}",
                    "total_cost": f"{np.mean([float(r['total_cost']) for r in vals]):.5f}",
                    "recovery_attempts": f"{np.mean([int(r['recovery_attempts']) for r in vals]):.5f}",
                    "calibration_error": f"{np.mean([float(r['calibration_error']) for r in vals]):.5f}",
                })
    return out


def aggregate_metrics(seed_rows, methods=METHODS):
    out = []
    metrics = [
        "goal_success",
        "deviation_rate",
        "recovery_success",
        "irreversible_failure",
        "damage",
        "budget_overrun",
        "total_cost",
        "recovery_attempts",
        "calibration_error",
    ]
    for split in sorted({r["split"] for r in seed_rows}):
        for method in methods:
            vals = [r for r in seed_rows if r["split"] == split and r["method"] == method]
            if not vals:
                continue
            for metric in metrics:
                nums = [float(v[metric]) for v in vals]
                out.append({
                    "split": split,
                    "method": method,
                    "metric": metric,
                    "mean": f"{np.mean(nums):.5f}",
                    "ci95": f"{ci95(nums):.5f}",
                    "seeds": len(nums),
                    "episodes_per_seed": vals[0]["episodes"],
                })
    return out


def pairwise_stats(seed_rows):
    refs = ["robust_margin_planner", "contingent_replanner", "expected_cost_replanner", "learned_failure_classifier"]
    metrics = ["goal_success", "recovery_success", "irreversible_failure", "damage", "total_cost", "calibration_error"]
    rows = []
    for split in sorted({r["split"] for r in seed_rows}):
        for ref in refs:
            for metric in metrics:
                diffs = []
                for seed in SEEDS:
                    tv = [r for r in seed_rows if r["split"] == split and r["method"] == "recoverability_score_planner" and int(r["seed"]) == seed]
                    rv = [r for r in seed_rows if r["split"] == split and r["method"] == ref and int(r["seed"]) == seed]
                    if tv and rv:
                        diffs.append(float(tv[0][metric]) - float(rv[0][metric]))
                higher = metric in {"goal_success", "recovery_success"}
                rows.append({
                    "split": split,
                    "target": "recoverability_score_planner",
                    "reference": ref,
                    "metric": metric,
                    "mean_diff": f"{np.mean(diffs):.5f}",
                    "ci95": f"{ci95(diffs):.5f}",
                    "target_better_seeds": sum(1 for d in diffs if (d > 0 if higher else d < 0)),
                    "seeds": len(diffs),
                })
    return rows


def metric_value(metric_rows, split, method, metric):
    rows = [r for r in metric_rows if r["split"] == split and r["method"] == method and r["metric"] == metric]
    return (float(rows[0]["mean"]), float(rows[0]["ci95"])) if rows else (0.0, 0.0)


def run_main():
    rows = []
    dataset = []
    splits = ["open_easy", "narrow_passage_shift", "object_slip_shift", "irreversible_commitment", "combined_hard_shift"]
    models = {seed: train_learned_model(seed) for seed in SEEDS}
    for split in splits:
        for seed in SEEDS:
            for episode_id in range(TEST_EPISODES_PER_SPLIT_SEED):
                ep = make_episode(split, seed, episode_id)
                dataset.append(dataset_row(ep))
                for method in METHODS:
                    rows.append(run_plan(ep, method, model=models[seed]))
            print(f"main split={split} seed={seed} rows={len(rows)}", flush=True)
    seed_rows = aggregate_seed_metrics(rows)
    metric_rows = aggregate_metrics(seed_rows)
    pair_rows = pairwise_stats(seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "dataset_summary.csv", dataset)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    return rows, seed_rows, metric_rows, pair_rows, models


ABLATIONS = [
    "full_recoverability_score",
    "minus_recovery_success",
    "minus_recovery_cost",
    "minus_irreversible_trap_penalty",
    "minus_diagnostic_value",
    "minus_failure_probability",
    "risk_only_score",
]


def run_ablation():
    rows = []
    summary = []
    for seed in SEEDS:
        for episode_id in range(TEST_EPISODES_PER_SPLIT_SEED):
            ep = make_episode("combined_hard_shift", seed, episode_id)
            for ablation in ABLATIONS:
                local = None if ablation == "full_recoverability_score" else ablation
                row = run_plan(ep, "recoverability_score_planner", ablation=local) | {"ablation": ablation}
                row["method"] = ablation
                rows.append(row)
        print(f"ablation seed={seed} rows={len(rows)}", flush=True)
    for ablation in ABLATIONS:
        vals = [r for r in rows if r["ablation"] == ablation]
        seed_rows = aggregate_seed_metrics(vals, methods=[ablation])
        nums = {metric: [float(r[metric]) for r in seed_rows] for metric in ["goal_success", "recovery_success", "irreversible_failure", "damage", "total_cost", "calibration_error"]}
        summary.append({
            "split": "combined_hard_shift",
            "ablation": ablation,
            "goal_success": f"{np.mean(nums['goal_success']):.5f}",
            "ci95_success": f"{ci95(nums['goal_success']):.5f}",
            "recovery_success": f"{np.mean(nums['recovery_success']):.5f}",
            "irreversible_failure": f"{np.mean(nums['irreversible_failure']):.5f}",
            "damage": f"{np.mean(nums['damage']):.5f}",
            "total_cost": f"{np.mean(nums['total_cost']):.5f}",
            "calibration_error": f"{np.mean(nums['calibration_error']):.5f}",
            "rows": len(vals),
        })
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, summary


def run_stress(models):
    axes = {
        "navigation": "stress_navigation",
        "slip": "stress_slip",
        "trap": "stress_trap",
        "sensor": "stress_sensor",
        "combined": "stress_combined",
    }
    methods = ["robust_margin_planner", "contingent_replanner", "learned_failure_classifier", "recoverability_score_planner", "oracle_recoverability_upper_bound"]
    raw = []
    summary = []
    for axis, split in axes.items():
        for level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            for seed in SEEDS:
                for episode_id in range(STRESS_EPISODES_PER_SEED):
                    ep = make_episode(split, seed, episode_id, stress=level)
                    for method in methods:
                        row = run_plan(ep, method, model=models[seed])
                        row["stress_axis"] = axis
                        row["stress_level"] = f"{level:.1f}"
                        raw.append(row)
                print(f"stress axis={axis} level={level:.1f} seed={seed} rows={len(raw)}", flush=True)
    for axis in axes:
        for level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            for method in methods:
                vals = [r for r in raw if r["stress_axis"] == axis and r["stress_level"] == f"{level:.1f}" and r["method"] == method]
                seed_rows = aggregate_seed_metrics(vals, methods=[method])
                summary.append({
                    "stress_axis": axis,
                    "stress_level": f"{level:.1f}",
                    "method": method,
                    "goal_success": f"{np.mean([float(r['goal_success']) for r in seed_rows]):.5f}",
                    "ci95_success": f"{ci95([float(r['goal_success']) for r in seed_rows]):.5f}",
                    "recovery_success": f"{np.mean([float(r['recovery_success']) for r in seed_rows]):.5f}",
                    "irreversible_failure": f"{np.mean([float(r['irreversible_failure']) for r in seed_rows]):.5f}",
                    "damage": f"{np.mean([float(r['damage']) for r in seed_rows]):.5f}",
                    "total_cost": f"{np.mean([float(r['total_cost']) for r in seed_rows]):.5f}",
                    "rows": len(vals),
                })
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, summary


def write_negative_cases(rows):
    failures = [r for r in rows if int(r["goal_success"]) == 0]
    lessons = {
        "irreversible_trap": "nominally feasible plan entered a state with no cheap recovery branch",
        "damage_or_lost_object": "physical deviation damaged the object or lost manipulation state",
        "budget_overrun": "recovery existed but consumed too much budget",
        "unrecovered_deviation": "failure was detected but recovery action did not succeed",
    }
    out = []
    seen = set()
    for r in failures:
        key = (r["split"], r["method"], r["failure_label"], r["plan_type"])
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "split": r["split"],
            "seed": r["seed"],
            "episode_id": r["episode_id"],
            "method": r["method"],
            "plan_type": r["plan_type"],
            "failure_label": r["failure_label"],
            "deviation": r["deviation"],
            "recovered": r["recovered"],
            "total_cost": r["total_cost"],
            "lesson": lessons.get(r["failure_label"], "negative case retained for audit"),
        })
        if len(out) >= 16:
            break
    write_csv(RESULTS / "negative_cases.csv", out)


def terminal_decision(metric_rows, pair_rows, ablation_summary):
    prop = metric_value(metric_rows, "combined_hard_shift", "recoverability_score_planner", "goal_success")
    robust = metric_value(metric_rows, "combined_hard_shift", "robust_margin_planner", "goal_success")
    contingent = metric_value(metric_rows, "combined_hard_shift", "contingent_replanner", "goal_success")
    learned = metric_value(metric_rows, "combined_hard_shift", "learned_failure_classifier", "goal_success")
    best = max(robust[0], contingent[0], learned[0])
    diff_cont = [r for r in pair_rows if r["split"] == "combined_hard_shift" and r["reference"] == "contingent_replanner" and r["metric"] == "goal_success"][0]
    trap_diff = [r for r in pair_rows if r["split"] == "combined_hard_shift" and r["reference"] == "contingent_replanner" and r["metric"] == "irreversible_failure"][0]
    full = [r for r in ablation_summary if r["ablation"] == "full_recoverability_score"][0]
    no_rec = [r for r in ablation_summary if r["ablation"] == "minus_recovery_success"][0]
    no_trap = [r for r in ablation_summary if r["ablation"] == "minus_irreversible_trap_penalty"][0]
    ablation_drop = float(full["goal_success"]) - max(float(no_rec["goal_success"]), float(no_trap["goal_success"]))
    if prop[0] >= best + 0.05 and float(diff_cont["mean_diff"]) > 0.03 and float(trap_diff["mean_diff"]) < -0.02 and ablation_drop >= 0.03:
        return "STRONG_REVISE"
    return "KILL_ARCHIVE"


def write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, rollout_rows, ablation_rows, stress_raw):
    decision = terminal_decision(metric_rows, pair_rows, ablation_summary)
    prop = metric_value(metric_rows, "combined_hard_shift", "recoverability_score_planner", "goal_success")
    robust = metric_value(metric_rows, "combined_hard_shift", "robust_margin_planner", "goal_success")
    contingent = metric_value(metric_rows, "combined_hard_shift", "contingent_replanner", "goal_success")
    learned = metric_value(metric_rows, "combined_hard_shift", "learned_failure_classifier", "goal_success")
    expected = metric_value(metric_rows, "combined_hard_shift", "expected_cost_replanner", "goal_success")
    oracle = metric_value(metric_rows, "combined_hard_shift", "oracle_recoverability_upper_bound", "goal_success")
    trap_prop = metric_value(metric_rows, "combined_hard_shift", "recoverability_score_planner", "irreversible_failure")
    trap_cont = metric_value(metric_rows, "combined_hard_shift", "contingent_replanner", "irreversible_failure")
    damage_prop = metric_value(metric_rows, "combined_hard_shift", "recoverability_score_planner", "damage")
    damage_cont = metric_value(metric_rows, "combined_hard_shift", "contingent_replanner", "damage")
    diff_cont = [r for r in pair_rows if r["split"] == "combined_hard_shift" and r["reference"] == "contingent_replanner" and r["metric"] == "goal_success"][0]
    stress_max = [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.0"]
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 82 planner_recoverability_scores v4 rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write("Reason: local task-and-motion recoverability benchmark exists, but no robot hardware or external high-fidelity benchmark is available.\n")
        f.write(f"Main rollout rows: {len(rollout_rows)}\n")
        f.write(f"Ablation rollout rows: {len(ablation_rows)}\n")
        f.write(f"Stress rollout rows: {len(stress_raw)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write("\nCombined hard-shift goal success:\n")
        f.write(f"recoverability_score_planner={prop[0]:.5f} ci95={prop[1]:.5f}\n")
        f.write(f"contingent_replanner={contingent[0]:.5f} ci95={contingent[1]:.5f}\n")
        f.write(f"robust_margin_planner={robust[0]:.5f} ci95={robust[1]:.5f}\n")
        f.write(f"learned_failure_classifier={learned[0]:.5f} ci95={learned[1]:.5f}\n")
        f.write(f"expected_cost_replanner={expected[0]:.5f} ci95={expected[1]:.5f}\n")
        f.write(f"oracle_recoverability_upper_bound={oracle[0]:.5f} ci95={oracle[1]:.5f}\n")
        f.write(f"irreversible proposed={trap_prop[0]:.5f}, contingent={trap_cont[0]:.5f}\n")
        f.write(f"damage proposed={damage_prop[0]:.5f}, contingent={damage_cont[0]:.5f}\n")
        f.write(f"paired goal-success diff vs contingent={diff_cont['mean_diff']} ci95={diff_cont['ci95']}\n")
        f.write("\nAblation combined_hard_shift:\n")
        for row in ablation_summary:
            f.write(
                f"{row['ablation']} goal_success={row['goal_success']} ci95={row['ci95_success']} "
                f"recovery_success={row['recovery_success']} irreversible={row['irreversible_failure']} damage={row['damage']} cost={row['total_cost']}\n"
            )
        f.write("\nCombined stress level 1.0:\n")
        for row in stress_max:
            f.write(
                f"{row['method']} goal_success={row['goal_success']} ci95={row['ci95_success']} "
                f"irreversible={row['irreversible_failure']} damage={row['damage']} cost={row['total_cost']}\n"
            )
    write_negative_cases(rollout_rows)
    return decision


def plot_outputs(metric_rows, ablation_summary, stress_summary):
    vals = [metric_value(metric_rows, "combined_hard_shift", m, "goal_success")[0] for m in METHODS]
    errs = [metric_value(metric_rows, "combined_hard_shift", m, "goal_success")[1] for m in METHODS]
    colors = ["#868e96", "#adb5bd", "#74c0fc", "#4dabf7", "#f08c00", "#2f9e44", "#087f5b", "#095c4a"]
    plt.figure(figsize=(11.8, 4.8))
    plt.bar(range(len(METHODS)), vals, yerr=errs, color=colors, capsize=3)
    plt.xticks(range(len(METHODS)), [m.replace("_", "\n") for m in METHODS], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Combined hard-shift planner recoverability")
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_success.png", dpi=220)
    plt.close()

    traps = [metric_value(metric_rows, "combined_hard_shift", m, "irreversible_failure")[0] for m in METHODS]
    damage = [metric_value(metric_rows, "combined_hard_shift", m, "damage")[0] for m in METHODS]
    x = np.arange(len(METHODS))
    plt.figure(figsize=(11.2, 4.8))
    plt.bar(x - 0.18, traps, width=0.36, label="irreversible trap", color="#c92a2a")
    plt.bar(x + 0.18, damage, width=0.36, label="damage/lost object", color="#f08c00")
    plt.xticks(x, [m.replace("_", "\n") for m in METHODS], fontsize=7)
    plt.ylabel("failure rate")
    plt.title("Irreversible and damaging failures")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_failures.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.5, 4.8))
    plt.bar(range(len(ablation_summary)), [float(r["goal_success"]) for r in ablation_summary], yerr=[float(r["ci95_success"]) for r in ablation_summary], color="#f08c00", capsize=3)
    plt.xticks(range(len(ablation_summary)), [r["ablation"].replace("_", "\n") for r in ablation_summary], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Recoverability score ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_ablation.png", dpi=220)
    plt.close()

    plt.figure(figsize=(9.2, 5.0))
    for method in ["robust_margin_planner", "contingent_replanner", "learned_failure_classifier", "recoverability_score_planner", "oracle_recoverability_upper_bound"]:
        rows = sorted([r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method], key=lambda r: float(r["stress_level"]))
        x = [float(r["stress_level"]) for r in rows]
        y = [float(r["goal_success"]) for r in rows]
        e = [float(r["ci95_success"]) for r in rows]
        plt.errorbar(x, y, yerr=e, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("combined deviation/trap stress")
    plt.ylabel("goal success")
    plt.ylim(0, 1.05)
    plt.title("Recoverability stress sweep")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_stress_sweep.png", dpi=220)
    plt.close()


def main():
    rollout_rows, seed_rows, metric_rows, pair_rows, models = run_main()
    ablation_rows, ablation_summary = run_ablation()
    stress_raw, stress_summary = run_stress(models)
    decision = write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, rollout_rows, ablation_rows, stress_raw)
    plot_outputs(metric_rows, ablation_summary, stress_summary)
    print(f"terminal={decision}")
    print(f"main_rollouts={len(rollout_rows)} ablation_rollouts={len(ablation_rows)} stress_rollouts={len(stress_raw)}")
    print(f"wrote results to {RESULTS}")


if __name__ == "__main__":
    main()
