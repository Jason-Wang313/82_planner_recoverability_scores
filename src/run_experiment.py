import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 82022026
SEEDS = list(range(10))
TEST_EPISODES_PER_SPLIT_SEED = 64
TRAIN_EPISODES_PER_SEED = 192
ABLATION_EPISODES_PER_SPLIT_SEED = 80
STRESS_EPISODES_PER_SEED = 32
FIXED_RISK_EPISODES_PER_SPLIT_SEED = 64

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

MAIN_SPLITS = [
    "open_easy",
    "narrow_passage_shift",
    "object_slip_shift",
    "irreversible_commitment",
    "sensor_dropout_shift",
    "budget_tight_shift",
    "latent_mode_shift",
    "adversarial_compound_shift",
    "combined_hard_shift",
]

HARD_SPLITS = [
    "narrow_passage_shift",
    "object_slip_shift",
    "irreversible_commitment",
    "sensor_dropout_shift",
    "budget_tight_shift",
    "latent_mode_shift",
    "adversarial_compound_shift",
    "combined_hard_shift",
]

METHODS = [
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
]

NON_ORACLE_METHODS = [m for m in METHODS if m != "oracle_recoverability_upper_bound"]

STRESS_METHODS = [
    "robust_margin_planner",
    "contingent_replanner",
    "learned_failure_classifier",
    "learned_expected_utility",
    "cvar_recovery_planner",
    "recoverability_score_planner_v5",
    "oracle_recoverability_upper_bound",
]

FIXED_RISK_METHODS = [
    "conformal_failure_filter",
    "learned_failure_classifier",
    "learned_expected_utility",
    "cvar_recovery_planner",
    "recoverability_score_planner_v5",
    "oracle_recoverability_upper_bound",
]

PLAN_TYPES = [
    "direct_shortcut",
    "robust_margin_route",
    "contingency_branch",
    "diagnostic_staging",
    "reversible_probe",
    "conservative_backoff",
    "dual_recovery_branch",
]

ABLATIONS = [
    "full_recoverability_score_v5",
    "minus_recovery_success",
    "minus_recovery_cost",
    "minus_irreversible_trap_penalty",
    "minus_damage_penalty",
    "minus_budget_slack",
    "minus_branch_entropy",
    "minus_calibration_penalty",
    "risk_only_score",
    "expected_utility_only",
]

STRESS_LEVELS = [0.0, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50]
FIXED_RISK_BUDGETS = [0.02, 0.05, 0.10, 0.20]
FIXED_RISK_SPLITS = ["combined_hard_shift", "adversarial_compound_shift"]

METRICS = [
    "goal_success",
    "deviation_rate",
    "recovery_success",
    "irreversible_failure",
    "damage",
    "budget_overrun",
    "total_cost",
    "recovery_attempts",
    "calibration_error",
    "predicted_unsafe",
    "risk_upper",
    "plan_diversity",
    "safety_utility",
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
    branch_entropy: float
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
    latent_mode_shift: float
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
    return float(np.clip(x, 0.001, 0.999))


def ci95(vals):
    vals = [float(v) for v in vals]
    if len(vals) <= 1:
        return 0.0
    mean = float(np.mean(vals))
    sd = math.sqrt(sum((x - mean) ** 2 for x in vals) / (len(vals) - 1))
    return 1.96 * sd / math.sqrt(len(vals))


def split_params(split, stress=0.0):
    if split == "train":
        return 0.24, 0.22, 0.18, 0.14, 0.18, 2.48, 0.10
    if split == "open_easy":
        return 0.10, 0.10, 0.05, 0.08, 0.08, 2.58, 0.04
    if split == "narrow_passage_shift":
        return 0.42 + 0.12 * stress, 0.16, 0.32 + 0.17 * stress, 0.18, 0.36, 2.32, 0.12
    if split == "object_slip_shift":
        return 0.16, 0.46 + 0.18 * stress, 0.18, 0.18, 0.24, 2.30, 0.10
    if split == "irreversible_commitment":
        return 0.24, 0.22, 0.56 + 0.16 * stress, 0.20, 0.30, 2.24, 0.14
    if split == "sensor_dropout_shift":
        return 0.28, 0.26, 0.28, 0.46 + 0.16 * stress, 0.32, 2.30, 0.20
    if split == "budget_tight_shift":
        return 0.30, 0.30, 0.34 + 0.10 * stress, 0.28, 0.36, 1.92 - 0.12 * stress, 0.16
    if split == "latent_mode_shift":
        return 0.30 + 0.06 * stress, 0.32, 0.34 + 0.10 * stress, 0.30, 0.34, 2.20, 0.42 + 0.12 * stress
    if split == "adversarial_compound_shift":
        return 0.52 + 0.12 * stress, 0.52 + 0.13 * stress, 0.58 + 0.18 * stress, 0.42 + 0.10 * stress, 0.54, 2.04 - 0.10 * stress, 0.46 + 0.10 * stress
    if split == "combined_hard_shift":
        return 0.48 + 0.10 * stress, 0.46 + 0.12 * stress, 0.52 + 0.15 * stress, 0.34 + 0.10 * stress, 0.46, 2.18 - 0.08 * stress, 0.32 + 0.08 * stress
    if split == "stress_navigation":
        return 0.12 + 0.55 * stress, 0.18, 0.20 + 0.24 * stress, 0.15, 0.24, 2.32, 0.14
    if split == "stress_slip":
        return 0.18, 0.12 + 0.60 * stress, 0.22, 0.17, 0.25, 2.32, 0.14
    if split == "stress_trap":
        return 0.22 + 0.16 * stress, 0.20, 0.10 + 0.70 * stress, 0.20, 0.34, 2.24, 0.18
    if split == "stress_sensor":
        return 0.28, 0.28, 0.30, 0.06 + 0.48 * stress, 0.30, 2.28, 0.24
    if split == "stress_budget":
        return 0.32, 0.30, 0.34, 0.28, 0.36, 2.42 - 0.50 * stress, 0.18
    if split == "stress_combined":
        return 0.12 + 0.50 * stress, 0.12 + 0.50 * stress, 0.10 + 0.60 * stress, 0.08 + 0.38 * stress, 0.14 + 0.42 * stress, 2.50 - 0.34 * stress, 0.12 + 0.42 * stress
    raise ValueError(split)


def candidate_template(plan_type):
    templates = {
        "direct_shortcut": (1.00, 0.22, 0.30, 0.05, 0.05, 0.18, 0.08),
        "robust_margin_route": (1.62, 0.76, 0.68, 0.20, 0.12, 0.58, 0.20),
        "contingency_branch": (1.74, 0.54, 0.56, 0.78, 0.22, 0.78, 0.54),
        "diagnostic_staging": (1.68, 0.48, 0.54, 0.66, 0.84, 0.86, 0.62),
        "reversible_probe": (1.86, 0.56, 0.58, 0.62, 0.74, 0.92, 0.72),
        "conservative_backoff": (2.44, 0.88, 0.78, 0.35, 0.16, 0.90, 0.30),
        "dual_recovery_branch": (2.06, 0.62, 0.62, 0.92, 0.52, 0.88, 0.88),
    }
    return templates[plan_type]


def make_candidate(plan_type, ep_rng, nav_deviation, manipulation_slip, trap_pressure, sensor_uncertainty, clutter, latent_mode_shift):
    base_cost, clearance, margin, branch_depth, diagnostic, reversibility, branch_entropy = candidate_template(plan_type)
    clearance = float(np.clip(clearance + ep_rng.normal(0.0, 0.045), 0.06, 0.98))
    margin = float(np.clip(margin + ep_rng.normal(0.0, 0.050), 0.06, 0.98))
    diagnostic = float(np.clip(diagnostic + ep_rng.normal(0.0, 0.045), 0.02, 0.98))
    reversibility = float(np.clip(reversibility + ep_rng.normal(0.0, 0.045), 0.02, 0.99))
    branch_entropy = float(np.clip(branch_entropy + ep_rng.normal(0.0, 0.050), 0.01, 0.99))
    nominal_cost = float(max(0.70, base_cost + ep_rng.normal(0.0, 0.055) + 0.11 * clutter * (1.0 - clearance)))

    nav_fail = nav_deviation * (1.08 - clearance) + 0.09 * clutter
    slip_fail = manipulation_slip * (1.05 - margin) + 0.06 * (1.0 - diagnostic)
    hidden_mode_penalty = latent_mode_shift * (1.0 - branch_entropy) * (1.0 - diagnostic)
    true_failure = clip01(0.05 + 0.40 * nav_fail + 0.38 * slip_fail + 0.18 * hidden_mode_penalty - 0.08 * diagnostic - 0.06 * branch_depth)
    true_trap = clip01(
        0.025
        + trap_pressure * (1.10 - reversibility) * (1.05 - clearance)
        + 0.20 * hidden_mode_penalty
        - 0.15 * branch_depth
        - 0.09 * diagnostic
    )
    true_recovery = clip01(
        0.12
        + 0.34 * reversibility
        + 0.25 * branch_depth
        + 0.20 * diagnostic
        + 0.18 * branch_entropy
        + 0.10 * clearance
        - 0.30 * true_trap
        - 0.10 * sensor_uncertainty
    )
    true_recovery_cost = float(
        max(
            0.15,
            0.45
            + 1.00 * (1.0 - reversibility)
            + 0.60 * clutter
            + 0.48 * true_trap
            + 0.18 * latent_mode_shift
            - 0.28 * diagnostic
            - 0.18 * branch_entropy,
        )
    )
    true_damage = clip01(0.025 + 0.40 * true_trap + 0.30 * slip_fail + 0.10 * (1.0 - margin) + 0.08 * hidden_mode_penalty - 0.16 * diagnostic)

    noise = sensor_uncertainty + 0.35 * latent_mode_shift
    predicted_failure = clip01(true_failure + ep_rng.normal(0.0, 0.08 + 0.19 * noise))
    predicted_trap = clip01(true_trap + ep_rng.normal(0.0, 0.07 + 0.16 * noise))
    predicted_recovery = clip01(true_recovery + ep_rng.normal(0.0, 0.08 + 0.16 * noise))
    predicted_recovery_cost = float(max(0.05, true_recovery_cost + ep_rng.normal(0.0, 0.11 + 0.22 * noise)))
    predicted_damage = clip01(true_damage + ep_rng.normal(0.0, 0.07 + 0.16 * noise))

    return CandidatePlan(
        plan_type=plan_type,
        nominal_cost=nominal_cost,
        clearance=clearance,
        manipulation_margin=margin,
        branch_depth=branch_depth,
        diagnostic_value=diagnostic,
        reversibility=reversibility,
        branch_entropy=branch_entropy,
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
    nav, slip, trap, sensor, clutter, budget, latent = split_params(split, stress)
    nav = float(np.clip(nav + rng.normal(0.0, 0.035), 0.02, 0.98))
    slip = float(np.clip(slip + rng.normal(0.0, 0.035), 0.02, 0.98))
    trap = float(np.clip(trap + rng.normal(0.0, 0.035), 0.01, 0.98))
    sensor = float(np.clip(sensor + rng.normal(0.0, 0.030), 0.02, 0.92))
    clutter = float(np.clip(clutter + rng.normal(0.0, 0.035), 0.02, 0.98))
    budget = float(max(1.45, budget + rng.normal(0.0, 0.08)))
    latent = float(np.clip(latent + rng.normal(0.0, 0.030), 0.01, 0.90))
    candidates = [make_candidate(plan_type, rng, nav, slip, trap, sensor, clutter, latent) for plan_type in PLAN_TYPES]
    return Episode(split, seed, episode_id, nav, slip, trap, sensor, clutter, budget, latent, candidates)


def feature_vector(plan):
    return np.array(
        [
            plan.nominal_cost,
            plan.clearance,
            plan.manipulation_margin,
            plan.branch_depth,
            plan.diagnostic_value,
            plan.reversibility,
            plan.branch_entropy,
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
    return expected_success - 0.28 * expected_cost - 0.95 * plan.true_damage - 1.15 * plan.true_trap - 0.65 * overtime


def true_unsafe_value(plan):
    return clip01(plan.true_trap + plan.true_damage + plan.true_failure * (1.0 - plan.true_recovery))


def predicted_unsafe_value(plan):
    return clip01(plan.predicted_trap + plan.predicted_damage + plan.predicted_failure * (1.0 - plan.predicted_recovery))


def ridge_fit(rows, targets, ridge_strength=0.08):
    x = np.asarray(rows, dtype=float)
    y = np.asarray(targets, dtype=float)
    mean = np.mean(x, axis=0)
    std = np.maximum(np.std(x, axis=0), 1e-6)
    xs = (x - mean) / std
    xs = np.c_[np.ones(len(xs)), xs]
    ridge = ridge_strength * np.eye(xs.shape[1])
    ridge[0, 0] = 0.0
    weights = np.linalg.solve(xs.T @ xs + ridge, xs.T @ y)
    return {"mean": mean, "std": std, "weights": weights}


def ridge_predict(model, plan):
    x = (feature_vector(plan) - model["mean"]) / model["std"]
    x = np.r_[1.0, x]
    return float(x @ model["weights"])


def train_models(seed):
    utility_rows = []
    utility_targets = []
    risk_rows = []
    risk_targets = []
    residuals = []
    for episode_id in range(TRAIN_EPISODES_PER_SEED):
        ep = make_episode("train", seed, episode_id)
        for plan in ep.candidates:
            utility_rows.append(feature_vector(plan))
            utility_targets.append(true_expected_utility(plan, ep.budget))
            risk_rows.append(feature_vector(plan))
            risk_targets.append(true_unsafe_value(plan))
            residuals.append(true_unsafe_value(plan) - predicted_unsafe_value(plan))
    calibration_q80 = float(max(0.0, np.quantile(residuals, 0.80)))
    calibration_q90 = float(max(0.0, np.quantile(residuals, 0.90)))
    calibration_q95 = float(max(0.0, np.quantile(residuals, 0.95)))
    return {
        "utility": ridge_fit(utility_rows, utility_targets, ridge_strength=0.08),
        "risk": ridge_fit(risk_rows, risk_targets, ridge_strength=0.08),
        "calibration_q80": calibration_q80,
        "calibration_q90": calibration_q90,
        "calibration_q95": calibration_q95,
    }


def learned_risk(model_bundle, plan):
    return clip01(ridge_predict(model_bundle["risk"], plan))


def learned_utility(model_bundle, plan):
    return ridge_predict(model_bundle["utility"], plan)


def risk_upper(plan, model_bundle=None, method="recoverability"):
    base = predicted_unsafe_value(plan)
    if method in {"learned_failure_classifier", "learned_expected_utility"} and model_bundle is not None:
        base = 0.50 * base + 0.50 * learned_risk(model_bundle, plan)
    if method == "oracle_recoverability_upper_bound":
        return true_unsafe_value(plan)
    q = model_bundle["calibration_q90"] if model_bundle is not None else 0.08
    if method == "cvar_recovery_planner":
        q = model_bundle["calibration_q95"] if model_bundle is not None else 0.10
    if method == "conformal_failure_filter":
        q = model_bundle["calibration_q95"] if model_bundle is not None else 0.10
    return clip01(base + q)


def recoverability_score_v5(plan, budget, model_bundle=None, ablation=None):
    failure = plan.predicted_failure
    recovery = plan.predicted_recovery
    recovery_cost = plan.predicted_recovery_cost
    trap = plan.predicted_trap
    damage = plan.predicted_damage
    branch_entropy = plan.branch_entropy
    diagnostic = plan.diagnostic_value
    calibration_penalty = risk_upper(plan, model_bundle, method="recoverability")
    if ablation == "minus_failure_probability":
        failure = 0.34
    if ablation == "minus_recovery_success":
        recovery = 0.50
    if ablation == "minus_recovery_cost":
        recovery_cost = 0.55
    if ablation == "minus_irreversible_trap_penalty":
        trap = 0.03
    if ablation == "minus_damage_penalty":
        damage = 0.03
    if ablation == "minus_budget_slack":
        budget = 10.0
    if ablation == "minus_branch_entropy":
        branch_entropy = 0.05
    if ablation == "minus_calibration_penalty":
        calibration_penalty = predicted_unsafe_value(plan)
    if ablation == "risk_only_score":
        return -(failure + 1.35 * trap + 0.85 * damage + 0.06 * plan.nominal_cost)
    recoverable_success = failure * (1.0 - trap) * recovery
    no_fail_success = 1.0 - failure
    expected_success = no_fail_success + recoverable_success
    expected_cost = plan.nominal_cost + failure * recovery_cost
    budget_slack = max(0.0, budget - expected_cost)
    overtime = max(0.0, expected_cost - budget)
    expected_utility_only = expected_success - 0.27 * expected_cost - 0.96 * damage - 1.12 * trap - 0.65 * overtime
    if ablation == "expected_utility_only":
        return expected_utility_only
    return (
        expected_utility_only
        + 0.18 * branch_entropy
        + 0.10 * diagnostic
        + 0.07 * budget_slack
        - 0.42 * calibration_penalty
    )


def choose_plan(ep, method, model_bundle=None, ablation=None):
    if method == "nominal_shortest_plan":
        return min(ep.candidates, key=lambda p: p.nominal_cost)
    if method == "risk_averse_plan":
        return min(ep.candidates, key=lambda p: p.predicted_failure + 1.30 * p.predicted_trap + 0.90 * p.predicted_damage + 0.05 * p.nominal_cost)
    if method == "robust_margin_planner":
        return max(ep.candidates, key=lambda p: 1.12 * p.clearance + 1.04 * p.manipulation_margin + 0.20 * p.reversibility - 0.26 * p.nominal_cost - 0.34 * p.predicted_damage)
    if method == "expected_cost_replanner":
        return min(ep.candidates, key=lambda p: p.nominal_cost + p.predicted_failure * (p.predicted_recovery_cost + 1.35 * (1.0 - p.predicted_recovery)) + 1.15 * p.predicted_trap)
    if method == "contingent_replanner":
        return max(ep.candidates, key=lambda p: 0.54 * p.branch_depth + 0.34 * p.reversibility + p.predicted_recovery - p.predicted_failure - 0.88 * p.predicted_trap - 0.20 * p.nominal_cost)
    if method == "receding_horizon_replanner":
        return max(ep.candidates, key=lambda p: 0.55 * (1.0 - p.predicted_failure) + 0.35 * p.predicted_recovery + 0.28 * p.diagnostic_value - 0.30 * p.nominal_cost - 0.70 * p.predicted_damage)
    if method == "conformal_failure_filter":
        candidates = [p for p in ep.candidates if risk_upper(p, model_bundle, method=method) <= 0.54]
        if not candidates:
            candidates = ep.candidates
        return max(candidates, key=lambda p: learned_utility(model_bundle, p) - 0.35 * risk_upper(p, model_bundle, method=method))
    if method == "learned_failure_classifier":
        return min(ep.candidates, key=lambda p: learned_risk(model_bundle, p) + 0.08 * p.nominal_cost)
    if method == "learned_expected_utility":
        return max(ep.candidates, key=lambda p: learned_utility(model_bundle, p))
    if method == "branch_entropy_planner":
        return max(ep.candidates, key=lambda p: 0.58 * p.branch_entropy + 0.34 * p.branch_depth + 0.32 * p.predicted_recovery - 0.22 * p.nominal_cost - 0.55 * p.predicted_trap)
    if method == "cvar_recovery_planner":
        return max(ep.candidates, key=lambda p: recoverability_score_v5(p, ep.budget, model_bundle) - 0.45 * risk_upper(p, model_bundle, method=method))
    if method == "recoverability_score_planner_v5":
        return max(ep.candidates, key=lambda p: recoverability_score_v5(p, ep.budget, model_bundle, ablation=ablation))
    if method == "oracle_recoverability_upper_bound":
        return max(ep.candidates, key=lambda p: true_expected_utility(p, ep.budget))
    raise ValueError(method)


def rollout_outcome(ep, method, plan, model_bundle=None, fixed_risk_budget=None, abstained=False):
    if abstained:
        return {
            "split": ep.split,
            "seed": ep.seed,
            "episode_id": ep.episode_id,
            "method": method,
            "plan_type": "abstain",
            "goal_success": 0,
            "deviation": 0,
            "recovered": 0,
            "irreversible_failure": 0,
            "damage": 0,
            "budget_overrun": 0,
            "total_cost": "0.00000",
            "recovery_attempts": 0,
            "calibration_error": "0.00000",
            "predicted_unsafe": "0.00000",
            "risk_upper": "0.00000",
            "safety_utility": "0.00000",
            "failure_label": "abstained_fixed_risk",
            "fixed_risk_budget": "" if fixed_risk_budget is None else f"{fixed_risk_budget:.2f}",
            "coverage": 0,
            "false_safe": 0,
            "nav_deviation": f"{ep.nav_deviation:.5f}",
            "manipulation_slip": f"{ep.manipulation_slip:.5f}",
            "trap_pressure": f"{ep.trap_pressure:.5f}",
            "sensor_uncertainty": f"{ep.sensor_uncertainty:.5f}",
            "latent_mode_shift": f"{ep.latent_mode_shift:.5f}",
            "budget": f"{ep.budget:.5f}",
        }
    rng = stable_rng("rollout", ep.split, ep.seed, ep.episode_id, method, plan.plan_type)
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
    pred_unsafe = predicted_unsafe_value(plan)
    upper = risk_upper(plan, model_bundle, method=method)
    calibration_error = abs(clip01(1.0 - pred_unsafe) - goal_success)
    safety_utility = goal_success - 1.75 * irreversible - 1.20 * damage - 0.35 * overtime - 0.08 * total_cost
    false_safe = int((irreversible or damage) and fixed_risk_budget is not None)
    return {
        "split": ep.split,
        "seed": ep.seed,
        "episode_id": ep.episode_id,
        "method": method,
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
        "predicted_unsafe": f"{pred_unsafe:.5f}",
        "risk_upper": f"{upper:.5f}",
        "safety_utility": f"{safety_utility:.5f}",
        "failure_label": failure_label,
        "fixed_risk_budget": "" if fixed_risk_budget is None else f"{fixed_risk_budget:.2f}",
        "coverage": 1,
        "false_safe": false_safe,
        "nav_deviation": f"{ep.nav_deviation:.5f}",
        "manipulation_slip": f"{ep.manipulation_slip:.5f}",
        "trap_pressure": f"{ep.trap_pressure:.5f}",
        "sensor_uncertainty": f"{ep.sensor_uncertainty:.5f}",
        "latent_mode_shift": f"{ep.latent_mode_shift:.5f}",
        "budget": f"{ep.budget:.5f}",
    }


def run_plan(ep, method, model_bundle=None, ablation=None):
    plan = choose_plan(ep, method, model_bundle=model_bundle, ablation=ablation)
    out = rollout_outcome(ep, method if ablation is None else ablation, plan, model_bundle=model_bundle)
    return out


def run_fixed_risk_plan(ep, method, model_bundle, budget):
    plan = choose_plan(ep, method, model_bundle=model_bundle)
    upper = risk_upper(plan, model_bundle, method=method)
    abstained = upper > budget
    return rollout_outcome(ep, method, plan, model_bundle=model_bundle, fixed_risk_budget=budget, abstained=abstained)


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
        "latent_mode_shift": f"{ep.latent_mode_shift:.5f}",
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
        row[f"{prefix}_branch_entropy"] = f"{plan.branch_entropy:.5f}"
    return row


def aggregate_seed_metrics(rows, methods, split_name=None):
    out = []
    splits = [split_name] if split_name else sorted({r["split"] for r in rows})
    for split in splits:
        split_rows = rows if split_name else [r for r in rows if r["split"] == split]
        for method in methods:
            method_rows = [r for r in split_rows if r["method"] == method]
            for seed in SEEDS:
                vals = [r for r in method_rows if int(r["seed"]) == seed]
                if not vals:
                    continue
                executed = [r for r in vals if int(r.get("coverage", 1)) == 1]
                deviations = [r for r in executed if int(r["deviation"]) == 1]
                recovery_success = np.mean([int(r["recovered"]) for r in deviations]) if deviations else 1.0
                plan_diversity = len({r["plan_type"] for r in executed}) / max(1, len(PLAN_TYPES))
                out.append({
                    "split": split,
                    "method": method,
                    "seed": seed,
                    "episodes": len(vals),
                    "goal_success": f"{np.mean([int(r['goal_success']) for r in vals]):.5f}",
                    "deviation_rate": f"{np.mean([int(r['deviation']) for r in executed]) if executed else 0.0:.5f}",
                    "recovery_success": f"{recovery_success:.5f}",
                    "irreversible_failure": f"{np.mean([int(r['irreversible_failure']) for r in executed]) if executed else 0.0:.5f}",
                    "damage": f"{np.mean([int(r['damage']) for r in executed]) if executed else 0.0:.5f}",
                    "budget_overrun": f"{np.mean([int(r['budget_overrun']) for r in executed]) if executed else 0.0:.5f}",
                    "total_cost": f"{np.mean([float(r['total_cost']) for r in executed]) if executed else 0.0:.5f}",
                    "recovery_attempts": f"{np.mean([int(r['recovery_attempts']) for r in executed]) if executed else 0.0:.5f}",
                    "calibration_error": f"{np.mean([float(r['calibration_error']) for r in executed]) if executed else 0.0:.5f}",
                    "predicted_unsafe": f"{np.mean([float(r['predicted_unsafe']) for r in executed]) if executed else 0.0:.5f}",
                    "risk_upper": f"{np.mean([float(r['risk_upper']) for r in executed]) if executed else 0.0:.5f}",
                    "plan_diversity": f"{plan_diversity:.5f}",
                    "safety_utility": f"{np.mean([float(r['safety_utility']) for r in vals]):.5f}",
                })
    return out


def aggregate_metrics(seed_rows, methods):
    out = []
    for split in sorted({r["split"] for r in seed_rows}):
        for method in methods:
            vals = [r for r in seed_rows if r["split"] == split and r["method"] == method]
            if not vals:
                continue
            for metric in METRICS:
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


def pairwise_stats(seed_rows, references=None, target="recoverability_score_planner_v5"):
    if references is None:
        references = [
            "robust_margin_planner",
            "contingent_replanner",
            "conformal_failure_filter",
            "learned_failure_classifier",
            "learned_expected_utility",
            "cvar_recovery_planner",
        ]
    metrics = ["goal_success", "recovery_success", "irreversible_failure", "damage", "total_cost", "calibration_error", "safety_utility"]
    rows = []
    for split in sorted({r["split"] for r in seed_rows}):
        for ref in references:
            for metric in metrics:
                diffs = []
                for seed in SEEDS:
                    tv = [r for r in seed_rows if r["split"] == split and r["method"] == target and int(r["seed"]) == seed]
                    rv = [r for r in seed_rows if r["split"] == split and r["method"] == ref and int(r["seed"]) == seed]
                    if tv and rv:
                        diffs.append(float(tv[0][metric]) - float(rv[0][metric]))
                if not diffs:
                    continue
                higher = metric in {"goal_success", "recovery_success", "safety_utility"}
                rows.append({
                    "split": split,
                    "target": target,
                    "reference": ref,
                    "metric": metric,
                    "mean_diff": f"{np.mean(diffs):.5f}",
                    "ci95": f"{ci95(diffs):.5f}",
                    "lower95": f"{np.mean(diffs) - ci95(diffs):.5f}",
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
    models = {seed: train_models(seed) for seed in SEEDS}
    for split in MAIN_SPLITS:
        for seed in SEEDS:
            for episode_id in range(TEST_EPISODES_PER_SPLIT_SEED):
                ep = make_episode(split, seed, episode_id)
                dataset.append(dataset_row(ep))
                for method in METHODS:
                    rows.append(run_plan(ep, method, model_bundle=models[seed]))
            print(f"main split={split} seed={seed} rows={len(rows)}", flush=True)
    seed_rows = aggregate_seed_metrics(rows, METHODS)
    metric_rows = aggregate_metrics(seed_rows, METHODS)
    pair_rows = pairwise_stats(seed_rows)
    hard_rows = [r for r in rows if r["split"] in HARD_SPLITS]
    hard_seed_rows = aggregate_seed_metrics(hard_rows, METHODS, split_name="hard_regime_aggregate")
    hard_metric_rows = aggregate_metrics(hard_seed_rows, METHODS)
    hard_pair_rows = pairwise_stats(hard_seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "dataset_summary.csv", dataset)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    write_csv(RESULTS / "hard_aggregate_seed_metrics.csv", hard_seed_rows)
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metric_rows)
    write_csv(RESULTS / "hard_aggregate_pairwise_stats.csv", hard_pair_rows)
    return rows, seed_rows, metric_rows, pair_rows, hard_seed_rows, hard_metric_rows, hard_pair_rows, models


def run_ablation(models):
    rows = []
    for split in ["combined_hard_shift", "adversarial_compound_shift"]:
        for seed in SEEDS:
            for episode_id in range(ABLATION_EPISODES_PER_SPLIT_SEED):
                ep = make_episode(split, seed, episode_id)
                for ablation in ABLATIONS:
                    local = None if ablation == "full_recoverability_score_v5" else ablation
                    row = run_plan(ep, "recoverability_score_planner_v5", model_bundle=models[seed], ablation=local)
                    row["method"] = ablation
                    row["ablation"] = ablation
                    rows.append(row)
            print(f"ablation split={split} seed={seed} rows={len(rows)}", flush=True)
    seed_rows = aggregate_seed_metrics(rows, ABLATIONS)
    summary = []
    for split in ["combined_hard_shift", "adversarial_compound_shift"]:
        for ablation in ABLATIONS:
            vals = [r for r in seed_rows if r["split"] == split and r["method"] == ablation]
            summary.append({
                "split": split,
                "ablation": ablation,
                "goal_success": f"{np.mean([float(r['goal_success']) for r in vals]):.5f}",
                "ci95_success": f"{ci95([float(r['goal_success']) for r in vals]):.5f}",
                "recovery_success": f"{np.mean([float(r['recovery_success']) for r in vals]):.5f}",
                "irreversible_failure": f"{np.mean([float(r['irreversible_failure']) for r in vals]):.5f}",
                "damage": f"{np.mean([float(r['damage']) for r in vals]):.5f}",
                "total_cost": f"{np.mean([float(r['total_cost']) for r in vals]):.5f}",
                "calibration_error": f"{np.mean([float(r['calibration_error']) for r in vals]):.5f}",
                "safety_utility": f"{np.mean([float(r['safety_utility']) for r in vals]):.5f}",
                "rows": len([r for r in rows if r["split"] == split and r["ablation"] == ablation]),
            })
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, seed_rows, summary


def run_stress(models):
    axes = {
        "navigation": "stress_navigation",
        "slip": "stress_slip",
        "trap": "stress_trap",
        "sensor": "stress_sensor",
        "budget": "stress_budget",
        "combined": "stress_combined",
    }
    raw = []
    summary = []
    seed_summary = []
    for axis, split in axes.items():
        for level in STRESS_LEVELS:
            for seed in SEEDS:
                for episode_id in range(STRESS_EPISODES_PER_SEED):
                    ep = make_episode(split, seed, episode_id, stress=level)
                    for method in STRESS_METHODS:
                        row = run_plan(ep, method, model_bundle=models[seed])
                        row["stress_axis"] = axis
                        row["stress_level"] = f"{level:.2f}"
                        raw.append(row)
                print(f"stress axis={axis} level={level:.2f} seed={seed} rows={len(raw)}", flush=True)
    for axis in axes:
        for level in STRESS_LEVELS:
            for method in STRESS_METHODS:
                vals = [r for r in raw if r["stress_axis"] == axis and r["stress_level"] == f"{level:.2f}" and r["method"] == method]
                for seed in SEEDS:
                    seed_vals = [r for r in vals if int(r["seed"]) == seed]
                    deviations = [r for r in seed_vals if int(r["deviation"]) == 1]
                    recovery_success = np.mean([int(r["recovered"]) for r in deviations]) if deviations else 1.0
                    seed_summary.append({
                        "stress_axis": axis,
                        "stress_level": f"{level:.2f}",
                        "method": method,
                        "seed": seed,
                        "episodes": len(seed_vals),
                        "goal_success": f"{np.mean([int(r['goal_success']) for r in seed_vals]):.5f}",
                        "recovery_success": f"{recovery_success:.5f}",
                        "irreversible_failure": f"{np.mean([int(r['irreversible_failure']) for r in seed_vals]):.5f}",
                        "damage": f"{np.mean([int(r['damage']) for r in seed_vals]):.5f}",
                        "total_cost": f"{np.mean([float(r['total_cost']) for r in seed_vals]):.5f}",
                        "safety_utility": f"{np.mean([float(r['safety_utility']) for r in seed_vals]):.5f}",
                    })
                local = [r for r in seed_summary if r["stress_axis"] == axis and r["stress_level"] == f"{level:.2f}" and r["method"] == method]
                summary.append({
                    "stress_axis": axis,
                    "stress_level": f"{level:.2f}",
                    "method": method,
                    "goal_success": f"{np.mean([float(r['goal_success']) for r in local]):.5f}",
                    "ci95_success": f"{ci95([float(r['goal_success']) for r in local]):.5f}",
                    "recovery_success": f"{np.mean([float(r['recovery_success']) for r in local]):.5f}",
                    "irreversible_failure": f"{np.mean([float(r['irreversible_failure']) for r in local]):.5f}",
                    "damage": f"{np.mean([float(r['damage']) for r in local]):.5f}",
                    "total_cost": f"{np.mean([float(r['total_cost']) for r in local]):.5f}",
                    "safety_utility": f"{np.mean([float(r['safety_utility']) for r in local]):.5f}",
                    "rows": len(vals),
                })
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", seed_summary)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, seed_summary, summary


def run_fixed_risk(models):
    raw = []
    seed_rows = []
    summary = []
    pairwise = []
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            for seed in SEEDS:
                for episode_id in range(FIXED_RISK_EPISODES_PER_SPLIT_SEED):
                    ep = make_episode(split, seed, episode_id)
                    for method in FIXED_RISK_METHODS:
                        row = run_fixed_risk_plan(ep, method, models[seed], budget)
                        row["risk_budget"] = f"{budget:.2f}"
                        raw.append(row)
                print(f"fixed_risk split={split} budget={budget:.2f} seed={seed} rows={len(raw)}", flush=True)
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            for method in FIXED_RISK_METHODS:
                vals = [r for r in raw if r["split"] == split and r["risk_budget"] == f"{budget:.2f}" and r["method"] == method]
                for seed in SEEDS:
                    seed_vals = [r for r in vals if int(r["seed"]) == seed]
                    executed = [r for r in seed_vals if int(r["coverage"]) == 1]
                    coverage = len(executed) / len(seed_vals) if seed_vals else 0.0
                    false_safe = sum(int(r["false_safe"]) for r in executed)
                    false_safe_rate = false_safe / len(executed) if executed else 0.0
                    seed_rows.append({
                        "split": split,
                        "risk_budget": f"{budget:.2f}",
                        "method": method,
                        "seed": seed,
                        "episodes": len(seed_vals),
                        "coverage": f"{coverage:.5f}",
                        "fixed_risk_success": f"{np.mean([int(r['goal_success']) for r in seed_vals]):.5f}",
                        "executed_success": f"{np.mean([int(r['goal_success']) for r in executed]) if executed else 0.0:.5f}",
                        "false_safe_rate": f"{false_safe_rate:.5f}",
                        "irreversible_failure": f"{np.mean([int(r['irreversible_failure']) for r in executed]) if executed else 0.0:.5f}",
                        "damage": f"{np.mean([int(r['damage']) for r in executed]) if executed else 0.0:.5f}",
                        "total_cost": f"{np.mean([float(r['total_cost']) for r in executed]) if executed else 0.0:.5f}",
                    })
                local = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == f"{budget:.2f}" and r["method"] == method]
                summary.append({
                    "split": split,
                    "risk_budget": f"{budget:.2f}",
                    "method": method,
                    "coverage": f"{np.mean([float(r['coverage']) for r in local]):.5f}",
                    "ci95_coverage": f"{ci95([float(r['coverage']) for r in local]):.5f}",
                    "fixed_risk_success": f"{np.mean([float(r['fixed_risk_success']) for r in local]):.5f}",
                    "ci95_fixed_risk_success": f"{ci95([float(r['fixed_risk_success']) for r in local]):.5f}",
                    "executed_success": f"{np.mean([float(r['executed_success']) for r in local]):.5f}",
                    "false_safe_rate": f"{np.mean([float(r['false_safe_rate']) for r in local]):.5f}",
                    "irreversible_failure": f"{np.mean([float(r['irreversible_failure']) for r in local]):.5f}",
                    "damage": f"{np.mean([float(r['damage']) for r in local]):.5f}",
                    "total_cost": f"{np.mean([float(r['total_cost']) for r in local]):.5f}",
                    "rows": len(vals),
                })
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            for ref in [m for m in FIXED_RISK_METHODS if m != "recoverability_score_planner_v5"]:
                for metric in ["coverage", "fixed_risk_success", "executed_success", "false_safe_rate"]:
                    diffs = []
                    for seed in SEEDS:
                        tv = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == f"{budget:.2f}" and r["method"] == "recoverability_score_planner_v5" and int(r["seed"]) == seed]
                        rv = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == f"{budget:.2f}" and r["method"] == ref and int(r["seed"]) == seed]
                        if tv and rv:
                            diffs.append(float(tv[0][metric]) - float(rv[0][metric]))
                    if diffs:
                        pairwise.append({
                            "split": split,
                            "risk_budget": f"{budget:.2f}",
                            "target": "recoverability_score_planner_v5",
                            "reference": ref,
                            "metric": metric,
                            "mean_diff": f"{np.mean(diffs):.5f}",
                            "ci95": f"{ci95(diffs):.5f}",
                            "lower95": f"{np.mean(diffs) - ci95(diffs):.5f}",
                            "seeds": len(diffs),
                        })
    write_csv(RESULTS / "fixed_risk_raw.csv", raw)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "fixed_risk_metrics.csv", summary)
    write_csv(RESULTS / "fixed_risk_pairwise.csv", pairwise)
    return raw, seed_rows, summary, pairwise


def write_negative_cases(main_rows, ablation_rows, fixed_rows):
    candidates = []
    for r in main_rows:
        if int(r["goal_success"]) == 0 and r["method"] == "recoverability_score_planner_v5":
            candidates.append((r, "v5_main_failure"))
        if int(r["goal_success"]) == 0 and r["method"] in {"learned_expected_utility", "cvar_recovery_planner", "contingent_replanner"}:
            candidates.append((r, "strong_baseline_failure"))
    for r in ablation_rows:
        if int(r["goal_success"]) == 1 and r["method"] != "full_recoverability_score_v5":
            candidates.append((r, "ablation_success_counterexample"))
    for r in fixed_rows:
        if int(r.get("false_safe", 0)) == 1:
            candidates.append((r, "fixed_risk_false_safe"))
        if r.get("failure_label") == "abstained_fixed_risk":
            candidates.append((r, "fixed_risk_abstention"))
    lessons = {
        "irreversible_trap": "nominally feasible plan entered a state with no cheap recovery branch",
        "damage_or_lost_object": "physical deviation damaged the object or lost manipulation state",
        "budget_overrun": "recovery existed but consumed too much budget",
        "unrecovered_deviation": "failure was detected but recovery action did not succeed",
        "abstained_fixed_risk": "fixed-risk safety budget rejected execution and reduced coverage",
        "success": "counterexample where a simpler ablation or baseline succeeds",
    }
    out = []
    seen = set()
    for r, source in candidates:
        key = (r["split"], r["method"], r["failure_label"], r["plan_type"], source)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "source": source,
            "split": r["split"],
            "seed": r["seed"],
            "episode_id": r["episode_id"],
            "method": r["method"],
            "plan_type": r["plan_type"],
            "failure_label": r["failure_label"],
            "goal_success": r["goal_success"],
            "deviation": r["deviation"],
            "recovered": r["recovered"],
            "total_cost": r["total_cost"],
            "risk_upper": r["risk_upper"],
            "lesson": lessons.get(r["failure_label"], "negative case retained for audit"),
        })
        if len(out) >= 24:
            break
    write_csv(RESULTS / "negative_cases.csv", out)
    return out


def terminal_decision(hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary):
    prop = metric_value(hard_metric_rows, "hard_regime_aggregate", "recoverability_score_planner_v5", "goal_success")
    non_oracle_scores = [(m, metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[0]) for m in NON_ORACLE_METHODS if m != "recoverability_score_planner_v5"]
    best_ref, best_score = max(non_oracle_scores, key=lambda x: x[1])
    pair = [r for r in hard_pair_rows if r["split"] == "hard_regime_aggregate" and r["reference"] == best_ref and r["metric"] == "goal_success"][0]
    safety_scores = []
    for method in NON_ORACLE_METHODS:
        trap = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "irreversible_failure")[0]
        damage = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "damage")[0]
        safety_scores.append((method, trap + damage))
    safety_ref, safety_best = min(safety_scores, key=lambda x: x[1])
    prop_safety = metric_value(hard_metric_rows, "hard_regime_aggregate", "recoverability_score_planner_v5", "irreversible_failure")[0] + metric_value(hard_metric_rows, "hard_regime_aggregate", "recoverability_score_planner_v5", "damage")[0]
    full_rows = [r for r in ablation_summary if r["ablation"] == "full_recoverability_score_v5"]
    ablation_gate = True
    for full in full_rows:
        others = [r for r in ablation_summary if r["split"] == full["split"] and r["ablation"] != "full_recoverability_score_v5"]
        full_success = float(full["goal_success"])
        full_safety = float(full["irreversible_failure"]) + float(full["damage"])
        for row in others:
            alt_success = float(row["goal_success"])
            alt_safety = float(row["irreversible_failure"]) + float(row["damage"])
            if alt_success >= full_success and alt_safety <= full_safety + 0.005:
                ablation_gate = False
    fixed_budget = [r for r in fixed_summary if r["risk_budget"] == "0.05" and r["method"] == "recoverability_score_planner_v5"]
    fixed_gate = all(float(r["coverage"]) >= 0.25 and float(r["false_safe_rate"]) <= 0.05 for r in fixed_budget)
    max_stress = [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.50"]
    prop_stress = [r for r in max_stress if r["method"] == "recoverability_score_planner_v5"][0]
    best_stress = max(float(r["goal_success"]) for r in max_stress if r["method"] != "oracle_recoverability_upper_bound")
    stress_gate = float(prop_stress["goal_success"]) >= best_stress - 0.03
    margin_gate = prop[0] >= best_score + 0.03
    paired_gate = float(pair["lower95"]) > 0.0
    safety_gate = prop_safety <= safety_best + 0.01
    gates = {
        "best_reference": best_ref,
        "best_reference_success": best_score,
        "proposed_hard_success": prop[0],
        "hard_margin": prop[0] - best_score,
        "paired_lower95_vs_best": float(pair["lower95"]),
        "safety_reference": safety_ref,
        "safety_reference_sum": safety_best,
        "proposed_safety_sum": prop_safety,
        "margin_gate": margin_gate,
        "paired_gate": paired_gate,
        "safety_gate": safety_gate,
        "ablation_gate": ablation_gate,
        "fixed_risk_gate": fixed_gate,
        "stress_gate": stress_gate,
    }
    decision = "STRONG_REVISE" if all([margin_gate, paired_gate, safety_gate, ablation_gate, fixed_gate, stress_gate]) else "KILL_ARCHIVE"
    return decision, gates


def write_summary(metric_rows, hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary, rollout_rows, ablation_rows, stress_raw, fixed_raw, negative_cases):
    decision, gates = terminal_decision(hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary)
    hard_methods = [
        "recoverability_score_planner_v5",
        "contingent_replanner",
        "conformal_failure_filter",
        "learned_failure_classifier",
        "learned_expected_utility",
        "cvar_recovery_planner",
        "oracle_recoverability_upper_bound",
    ]
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 82 planner_recoverability_scores v5 expanded rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write("Reason: CPU-only local TAMP recoverability benchmark expanded with theory, hard aggregates, ablations, stress, and fixed-risk deployment; no robot hardware or external high-fidelity benchmark is present.\n")
        f.write(f"Main rollout rows: {len(rollout_rows)}\n")
        f.write(f"Ablation rollout rows: {len(ablation_rows)}\n")
        f.write(f"Stress rollout rows: {len(stress_raw)}\n")
        f.write(f"Fixed-risk rollout rows: {len(fixed_raw)}\n")
        f.write(f"Negative cases: {len(negative_cases)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write("\nHard-regime aggregate goal success:\n")
        for method in hard_methods:
            val = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "goal_success")
            safety = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "safety_utility")
            trap = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "irreversible_failure")
            damage = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "damage")
            f.write(f"{method}={val[0]:.5f} ci95={val[1]:.5f} safety_utility={safety[0]:.5f} irreversible={trap[0]:.5f} damage={damage[0]:.5f}\n")
        f.write("\nDecision gates:\n")
        for key, value in gates.items():
            f.write(f"{key}: {value}\n")
        f.write("\nPairwise hard aggregate versus strongest non-oracle:\n")
        for row in hard_pair_rows:
            if row["split"] == "hard_regime_aggregate" and row["reference"] == gates["best_reference"]:
                f.write(f"{row['metric']} diff={row['mean_diff']} ci95={row['ci95']} lower95={row['lower95']} better_seeds={row['target_better_seeds']}/{row['seeds']}\n")
        f.write("\nAblation results:\n")
        for row in ablation_summary:
            f.write(
                f"{row['split']} {row['ablation']} goal_success={row['goal_success']} ci95={row['ci95_success']} "
                f"irreversible={row['irreversible_failure']} damage={row['damage']} safety_utility={row['safety_utility']}\n"
            )
        f.write("\nCombined stress level 1.50:\n")
        for row in [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.50"]:
            f.write(
                f"{row['method']} goal_success={row['goal_success']} ci95={row['ci95_success']} "
                f"irreversible={row['irreversible_failure']} damage={row['damage']} safety_utility={row['safety_utility']}\n"
            )
        f.write("\nFixed-risk budget 0.05:\n")
        for row in [r for r in fixed_summary if r["risk_budget"] == "0.05"]:
            f.write(
                f"{row['split']} {row['method']} coverage={row['coverage']} fixed_risk_success={row['fixed_risk_success']} "
                f"executed_success={row['executed_success']} false_safe_rate={row['false_safe_rate']} damage={row['damage']}\n"
            )
    return decision, gates


def plot_outputs(hard_metric_rows, ablation_summary, stress_summary, fixed_summary):
    plot_methods = [
        "nominal_shortest_plan",
        "risk_averse_plan",
        "robust_margin_planner",
        "contingent_replanner",
        "learned_failure_classifier",
        "learned_expected_utility",
        "cvar_recovery_planner",
        "recoverability_score_planner_v5",
        "oracle_recoverability_upper_bound",
    ]
    vals = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[0] for m in plot_methods]
    errs = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[1] for m in plot_methods]
    colors = ["#868e96", "#adb5bd", "#74c0fc", "#4dabf7", "#2f9e44", "#37b24d", "#f08c00", "#087f5b", "#095c4a"]
    plt.figure(figsize=(12.8, 4.9))
    plt.bar(range(len(plot_methods)), vals, yerr=errs, color=colors, capsize=3)
    plt.xticks(range(len(plot_methods)), [m.replace("_", "\n") for m in plot_methods], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Hard-regime aggregate planner recoverability")
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_success.png", dpi=220)
    plt.close()

    traps = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "irreversible_failure")[0] for m in plot_methods]
    damage = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "damage")[0] for m in plot_methods]
    x = np.arange(len(plot_methods))
    plt.figure(figsize=(12.5, 4.9))
    plt.bar(x - 0.18, traps, width=0.36, label="irreversible trap", color="#c92a2a")
    plt.bar(x + 0.18, damage, width=0.36, label="damage/lost object", color="#f08c00")
    plt.xticks(x, [m.replace("_", "\n") for m in plot_methods], fontsize=7)
    plt.ylabel("executed failure rate")
    plt.title("Irreversible and damaging failures")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_failures.png", dpi=220)
    plt.close()

    combined_ablation = [r for r in ablation_summary if r["split"] == "combined_hard_shift"]
    plt.figure(figsize=(12.0, 5.0))
    plt.bar(range(len(combined_ablation)), [float(r["goal_success"]) for r in combined_ablation], yerr=[float(r["ci95_success"]) for r in combined_ablation], color="#f08c00", capsize=3)
    plt.xticks(range(len(combined_ablation)), [r["ablation"].replace("_", "\n") for r in combined_ablation], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Recoverability score v5 ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_ablation.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.0, 5.2))
    for method in STRESS_METHODS:
        rows = sorted([r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method], key=lambda r: float(r["stress_level"]))
        x = [float(r["stress_level"]) for r in rows]
        y = [float(r["goal_success"]) for r in rows]
        e = [float(r["ci95_success"]) for r in rows]
        plt.errorbar(x, y, yerr=e, marker="o", linewidth=2, capsize=3, label=method)
    plt.xlabel("combined deviation/trap/sensor/budget stress")
    plt.ylabel("goal success")
    plt.ylim(0, 1.05)
    plt.title("Recoverability stress sweep")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_stress_sweep.png", dpi=220)
    plt.close()

    budget_rows = [r for r in fixed_summary if r["split"] == "combined_hard_shift" and r["risk_budget"] == "0.05"]
    plt.figure(figsize=(10.8, 4.8))
    x = np.arange(len(budget_rows))
    plt.bar(x - 0.18, [float(r["coverage"]) for r in budget_rows], width=0.36, label="coverage", color="#4dabf7")
    plt.bar(x + 0.18, [float(r["false_safe_rate"]) for r in budget_rows], width=0.36, label="false-safe rate", color="#c92a2a")
    plt.xticks(x, [r["method"].replace("_", "\n") for r in budget_rows], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("rate")
    plt.title("Fixed-risk deployment at 0.05 budget")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "recoverability_fixed_risk.png", dpi=220)
    plt.close()


def main():
    rollout_rows, seed_rows, metric_rows, pair_rows, hard_seed_rows, hard_metric_rows, hard_pair_rows, models = run_main()
    ablation_rows, ablation_seed_rows, ablation_summary = run_ablation(models)
    stress_raw, stress_seed_rows, stress_summary = run_stress(models)
    fixed_raw, fixed_seed_rows, fixed_summary, fixed_pairwise = run_fixed_risk(models)
    negative_cases = write_negative_cases(rollout_rows, ablation_rows, fixed_raw)
    decision, gates = write_summary(
        metric_rows,
        hard_metric_rows,
        hard_pair_rows,
        ablation_summary,
        stress_summary,
        fixed_summary,
        rollout_rows,
        ablation_rows,
        stress_raw,
        fixed_raw,
        negative_cases,
    )
    plot_outputs(hard_metric_rows, ablation_summary, stress_summary, fixed_summary)
    print(f"terminal={decision}")
    print(
        "rows "
        f"main={len(rollout_rows)} ablation={len(ablation_rows)} stress={len(stress_raw)} "
        f"fixed_risk={len(fixed_raw)} negative_cases={len(negative_cases)}"
    )
    print(f"gates={gates}")
    print(f"wrote results to {RESULTS}")


if __name__ == "__main__":
    main()
