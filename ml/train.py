#!/usr/bin/env python3
"""
Training script for the Adaptive Load Tutor cognitive-load predictor.

Usage:
    python ml/train.py

Reads ``ml/training_data.csv``, trains three regressors (GradientBoosting,
RandomForest, Ridge), selects the best via 5-fold cross-validation, and
persists the winning model plus metadata under ``ml/artifacts/``.
"""

import json
import os
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml
from scipy.stats import pearsonr
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "train_config.yaml")
DATA_PATH = os.path.join(SCRIPT_DIR, "training_data.csv")
ARTIFACTS_DIR = os.path.join(SCRIPT_DIR, "artifacts")
PLOTS_DIR = os.path.join(ARTIFACTS_DIR, "plots")

FEATURE_COLS = [
    "compile_errors",
    "runtime_errors",
    "wrong",
    "correct",
    "hint_open",
    "run_code",
    "pause_mean_ms",
    "delete_ratio",
    "face_present",
    "gaze_on_screen",
    "gaze_dispersion",
    "blink_rate",
    "head_motion",
    "away_events",
]


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def build_models(cfg: dict) -> dict:
    """Instantiate candidate models from config."""
    seed = cfg.get("random_seed", 42)
    gb_params = cfg["models"]["gradient_boosting"]
    rf_params = cfg["models"]["random_forest"]
    ridge_params = cfg["models"]["ridge"]

    return {
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=gb_params["n_estimators"],
            max_depth=gb_params["max_depth"],
            learning_rate=gb_params["learning_rate"],
            random_state=seed,
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=rf_params["n_estimators"],
            max_depth=rf_params["max_depth"],
            random_state=seed,
            n_jobs=-1,
        ),
        "Ridge": Ridge(
            alpha=ridge_params["alpha"],
        ),
    }


def evaluate_cv(model, X, y, cv) -> dict:
    """Run cross-validated prediction and return MAE, RMSE, Pearson r."""
    y_pred = cross_val_predict(model, X, y, cv=cv)

    mae = mean_absolute_error(y, y_pred)
    rmse = root_mean_squared_error(y, y_pred)
    r, p_value = pearsonr(y, y_pred)

    return {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "pearson_r": round(float(r), 4),
        "pearson_p": round(float(p_value), 6),
        "y_pred": y_pred,
    }


def plot_correlation(y_true, y_pred, model_name: str, save_path: str):
    """Scatter plot of predicted vs actual effort labels."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.35, edgecolors="k", linewidth=0.3, s=28)
    lo, hi = 0.5, 7.5
    ax.plot([lo, hi], [lo, hi], "--", color="red", linewidth=1, label="ideal")
    ax.set_xlabel("Actual effort label")
    ax.set_ylabel("Predicted effort label")
    ax.set_title(f"{model_name} -- Predicted vs Actual")
    ax.legend()
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved correlation plot -> {save_path}")


def plot_feature_importance(model, feature_names: list[str], model_name: str, save_path: str):
    """Horizontal bar chart of feature importances (tree models only)."""
    if not hasattr(model, "feature_importances_"):
        print(f"  Skipping feature importance plot for {model_name} (not tree-based).")
        return

    importances = model.feature_importances_
    indices = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(range(len(indices)), importances[indices], align="center")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices])
    ax.set_xlabel("Feature Importance")
    ax.set_title(f"{model_name} -- Feature Importances")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved feature importance plot -> {save_path}")


def main():
    # ------------------------------------------------------------------ load
    print("=" * 60)
    print("Adaptive Load Tutor -- ML Training Pipeline")
    print("=" * 60)

    cfg = load_config()
    seed = cfg.get("random_seed", 42)
    n_folds = cfg.get("cv_folds", 5)
    target_col = cfg.get("target_column", "effort_label")

    if not os.path.exists(DATA_PATH):
        print(f"ERROR: {DATA_PATH} not found.")
        print("Run  python ml/generate_synthetic_data.py  first.")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df)} samples from {DATA_PATH}")
    print(f"Features: {FEATURE_COLS}")
    print(f"Target:   {target_col}")

    X = df[FEATURE_COLS].values
    y = df[target_col].values

    # ensure output dirs exist
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # -------------------------------------------------------------- train/cv
    models = build_models(cfg)
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)

    results = {}
    print(f"\nRunning {n_folds}-fold cross-validation ...\n")

    for name, model in models.items():
        print(f"  [{name}]")
        metrics = evaluate_cv(model, X, y, kf)
        results[name] = metrics
        print(f"    MAE  = {metrics['mae']}")
        print(f"    RMSE = {metrics['rmse']}")
        print(f"    r    = {metrics['pearson_r']}  (p={metrics['pearson_p']})")

    # --------------------------------------------------------- select best
    best_name = min(results, key=lambda n: results[n]["mae"])
    best_metrics = results[best_name]
    print(f"\nBest model: {best_name}  (MAE={best_metrics['mae']})\n")

    # -------------------------------------------------------- retrain on all
    best_model = models[best_name]
    best_model.fit(X, y)

    # ---------------------------------------------------------- save artefacts
    model_path = os.path.join(ARTIFACTS_DIR, "load_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"Saved model       -> {model_path}")

    feature_path = os.path.join(ARTIFACTS_DIR, "feature_names.json")
    with open(feature_path, "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)
    print(f"Saved features    -> {feature_path}")

    # evaluation report
    report = {
        "best_model": best_name,
        "cv_folds": n_folds,
        "n_samples": len(df),
        "results": {
            name: {k: v for k, v in m.items() if k != "y_pred"}
            for name, m in results.items()
        },
    }
    report_path = os.path.join(ARTIFACTS_DIR, "evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved eval report -> {report_path}")

    # ----------------------------------------------------------- plots
    print("\nGenerating plots ...")

    # correlation plot for the best model
    corr_path = os.path.join(PLOTS_DIR, "correlation_plot.png")
    plot_correlation(y, results[best_name]["y_pred"], best_name, corr_path)

    # feature importance plot for the best model
    imp_path = os.path.join(PLOTS_DIR, "feature_importance.png")
    plot_feature_importance(best_model, FEATURE_COLS, best_name, imp_path)

    # ----------------------------------------------------------- summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"  Samples:         {len(df)}")
    print(f"  Features:        {len(FEATURE_COLS)}")
    print(f"  CV folds:        {n_folds}")
    print(f"  Best model:      {best_name}")
    print(f"  Best MAE:        {best_metrics['mae']}")
    print(f"  Best RMSE:       {best_metrics['rmse']}")
    print(f"  Best Pearson r:  {best_metrics['pearson_r']}")
    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=FutureWarning)
    main()
