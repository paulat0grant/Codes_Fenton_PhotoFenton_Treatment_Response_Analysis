"""
Random Forest Regression + Variable Importance Plot (VIP) - SIMPLIFIED
========================================================================

This is a simplified replacement for the earlier multi-sheet / multi-output
/ engineered-feature version. It is much easier to describe in a Methods
section because:

  1. ONE input sheet, ONE row per (Matrix, Process, Ratio, Parameter)
     combination - no manual sheet-by-sheet parsing to explain.
  2. ONE target variable (Removal (%)) instead of three simultaneous
     targets - a standard single-output Random Forest.
  3. Predictors are plain experimental conditions (Matrix, Process, Ratio,
     Parameter, Initial Value) - no engineered "Scavenging Index" /
     "Attenuation Factor" features, which were mathematically redundant
     with Matrix (perfectly collinear, since both are deterministic
     functions of the baseline concentrations for only 2 matrices).

Dataset  : Objective_1_Consolidated.xlsx (single sheet)
Target   : Removal (%)
Features : Matrix, Process, Ratio, Parameter, Initial Value

Rows with no baseline concentration available (Phosphate - not present in
the Raw_Effluent_Data sheet) are automatically dropped, since Initial Value
cannot be computed for them.

Method
------
1. One-hot encode the categorical predictors (Matrix, Process, Parameter)
   so each category gets its own interpretable importance score.
2. Fit a RandomForestRegressor.
3. Because the dataset is small (120 usable rows), report BOTH:
     - 5-fold cross-validated R^2 (primary reliability metric)
     - held-out test-set R^2 / RMSE (secondary, illustrative)
4. Compute variable importance two ways:
     - Permutation importance on the test set (primary "VIP Score" - less
       biased, reflects genuine predictive contribution)
     - Mean Decrease in Impurity (MDI, i.e. rf.feature_importances_) shown
       alongside for reference/comparison only.
5. Plot the VIP bar chart.

Usage
-----
    python MLModel101_v2.py /path/to/Objective_1_Consolidated.xlsx
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.inspection import permutation_importance
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
TARGET_COL = "Removal (%)"
CATEGORICAL_COLS = ["Matrix", "Process", "Parameter"]
NUMERIC_COLS = ["Ratio", "Initial Value"]

RANDOM_STATE = 42
N_ESTIMATORS = 1000
TEST_SIZE = 0.2
N_PERMUTATION_REPEATS = 50


# ----------------------------------------------------------------------
# 1. Load & prepare data
# ----------------------------------------------------------------------
def load_and_prepare(path):
    df = pd.read_excel(path)

    n_before = len(df)
    df = df.dropna(subset=["Initial Value", TARGET_COL]).reset_index(drop=True)
    n_after = len(df)
    if n_after < n_before:
        print(f"Dropped {n_before - n_after} rows with no baseline "
              f"(Initial Value) available.")

    y = df[TARGET_COL].astype(float)
    X_raw = df[CATEGORICAL_COLS + NUMERIC_COLS].copy()
    X = pd.get_dummies(X_raw, columns=CATEGORICAL_COLS, drop_first=False)
    return X, y, df


# ----------------------------------------------------------------------
# 2. Train / evaluate Random Forest
# ----------------------------------------------------------------------
def train_random_forest(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    rf = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        oob_score=True,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    y_pred_test = rf.predict(X_test)
    r2_test = r2_score(y_test, y_pred_test)
    rmse_test = mean_squared_error(y_test, y_pred_test) ** 0.5
    mae_test = mean_absolute_error(y_test, y_pred_test)

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(rf, X, y, cv=cv, scoring="r2")

    print("=" * 70)
    print(f"Random Forest Regressor - target: {TARGET_COL}")
    print("=" * 70)
    print(f"Train size: {len(X_train)}   Test size: {len(X_test)}")
    print(f"OOB R^2                : {rf.oob_score_:.4f}")
    print(f"Test R^2               : {r2_test:.4f}")
    print(f"Test RMSE              : {rmse_test:.4f}")
    print(f"Test MAE               : {mae_test:.4f}")
    print(f"5-fold CV R^2 (mean±sd) : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    return rf, X_train, X_test, y_train, y_test


# ----------------------------------------------------------------------
# 3. Variable importance (MDI + permutation)
# ----------------------------------------------------------------------
def compute_importances(rf, X_test, y_test, feature_names):
    mdi = pd.Series(rf.feature_importances_, index=feature_names, name="MDI")

    perm = permutation_importance(
        rf, X_test, y_test,
        n_repeats=N_PERMUTATION_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    perm_mean = pd.Series(perm.importances_mean, index=feature_names, name="Permutation")
    perm_std = pd.Series(perm.importances_std, index=feature_names, name="Permutation_std")

    imp_df = pd.concat([perm_mean, perm_std, mdi], axis=1)
    imp_df = imp_df.sort_values("Permutation", ascending=False)
    return imp_df


# ----------------------------------------------------------------------
# 4. VIP (Variable Importance) plot
# ----------------------------------------------------------------------
def plot_vip(imp_df, out_path="vip_score_simplified.png"):
    plot_df = imp_df.sort_values("Permutation", ascending=True)

    fig, ax = plt.subplots(figsize=(8, max(4, 0.35 * len(plot_df))))
    ax.barh(
        plot_df.index, plot_df["Permutation"],
        xerr=plot_df["Permutation_std"],
        color="#4C72B0", ecolor="black", capsize=3,
    )
    ax.set_xlabel("VIP Score (Permutation Importance, ΔR²)")
    ax.set_title(f"Variable Importance Plot (VIP) — Random Forest\nTarget: {TARGET_COL}")
    ax.axvline(0, color="grey", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nSaved plot to {out_path}")
    return fig


def plot_pred_vs_actual(rf, X_test, y_test, out_path="predicted_vs_actual_simplified.png"):
    y_pred = rf.predict(X_test)
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.scatter(y_test, y_pred, color="#4C72B0", edgecolor="k", alpha=0.8)
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    ax.plot(lims, lims, "k--", linewidth=1, label="1:1 line")
    ax.set_xlabel(f"Actual {TARGET_COL}")
    ax.set_ylabel(f"Predicted {TARGET_COL}")
    ax.set_title("Random Forest: Predicted vs. Actual (test set)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out_path}")
    return fig


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main(path):
    X, y, df = load_and_prepare(path)
    rf, X_train, X_test, y_train, y_test = train_random_forest(X, y)
    imp_df = compute_importances(rf, X_test, y_test, X.columns)

    print("\nVariable importance (sorted by permutation importance):\n")
    print(imp_df.to_string())

    plot_vip(imp_df)
    plot_pred_vs_actual(rf, X_test, y_test)

    plt.show()
    
    imp_df.to_csv("vip_scores_simplified.csv")
    print("\nSaved: vip_scores_simplified.csv")

    return rf, imp_df


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "EditedData.xlsx"
    main(path)
