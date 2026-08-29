"""
Derringer & Suich (1980) Desirability-Function Optimization
============================================================

Experimental factors : Matrix, Process, Fe:H2O2 Ratio, aSOR, CTCI
Responses (desirability functions):
    - % COD removal      -> "larger is better"   (maximize)
    - Residual aSOR       -> "smaller is better"  (minimize)
    - Sulphate Change     -> "smaller is better"  (minimize) *ASSUMPTION - see note below
    - COD IRI             -> "smaller is better"  (minimize) *ASSUMPTION - see note below

*** IMPORTANT - CHECK THESE ASSUMPTIONS BEFORE TRUSTING THE RESULTS ***
"Sulphate Change" and "COD IRI" directions were not specified. This script
assumes lower is better for both (i.e. you want to minimize sulphate
production and minimize the inhibition/residual index). If your actual goal
is different (e.g. you WANT a bigger sulphate increase, or IRI has a target
value rather than "smaller is better"), edit the RESPONSE_SPECS dictionary
below - each entry's "goal" can be "max", "min", or "target", and low/high/
target bounds can be set manually instead of being auto-derived from the data.

Method
------
1. Individual desirability (d_i) is computed for each response using the
   classic Derringer & Suich piecewise functions:
       larger-is-better  : d = 0 below `low`, 1 above `high`, interpolated
                            in between with exponent r
       smaller-is-better : d = 1 below `low`, 0 above `high`, interpolated
                            in between with exponent s
       target-is-best    : two-sided ramp peaking at `target`
2. Composite desirability D = weighted geometric mean of the d_i
   (D = 0 if ANY d_i = 0 - this is the point of using a geometric mean:
   one badly-failing response tanks the overall score).
3. Because Ratio is the only continuous, freely adjustable factor in the
   dataset (aSOR and CTCI are fixed properties of each Matrix, not
   independently set), a quadratic response surface is fitted for every
   response, separately for each (Matrix, Process) combination, as a
   function of Ratio. These surfaces are then used to find the Ratio value
   that maximizes composite desirability within each Matrix/Process group,
   and to identify the single best combination overall.

Usage
-----
    python desirability_optimization.py /path/to/SpreadSheet.xlsx
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

# ----------------------------------------------------------------------
# 1. RESPONSE SPECIFICATIONS  (edit this to match your real objectives)
# ----------------------------------------------------------------------
# goal   : "max"    -> larger-is-better
#          "min"    -> smaller-is-better
#          "target" -> two-sided, peaks at `target`
# low/high: the "fails completely" / "fully satisfied" bounds
#           (for "max": low = worst acceptable, high = ideal/saturating value)
#           (for "min": low = ideal/saturating value, high = worst acceptable)
#           (for "target": low/high are the two failure bounds, target is ideal)
# r, s   : curvature exponents (1 = linear, >1 = convex/lenient near the
#           bound then strict near the target, <1 = concave/strict early)
# weight : relative importance in the composite geometric mean

RESPONSE_SPECS = {
    "% COD removal": dict(goal="max", low=30, high=95, r=1, weight=1),
    "Residual aSOR": dict(goal="min", low=None, high=None, s=1, weight=1),
    "Sulphate Change": dict(goal="min", low=None, high=None, s=1, weight=1),
}
# `low`/`high` set to None -> auto-derived from the observed min/max of the
# column in the dataset (see `fill_auto_bounds`). Replace None with a real
# number to use a fixed engineering/regulatory target instead of the
# data-driven range.

FACTOR_COL = "Ratio"          # the continuous factor optimized over
GROUP_COLS = ["Matrix", "Process"]   # categorical groups (fixed conditions)


# ----------------------------------------------------------------------
# 2. Derringer & Suich individual desirability functions
# ----------------------------------------------------------------------
def desirability_max(y, low, high, r=1):
    y = np.asarray(y, dtype=float)
    d = np.where(y <= low, 0.0,
        np.where(y >= high, 1.0, ((y - low) / (high - low)) ** r))
    return np.clip(d, 0.0, 1.0)


def desirability_min(y, low, high, s=1):
    """low = ideal (d=1), high = worst acceptable (d=0)."""
    y = np.asarray(y, dtype=float)
    d = np.where(y <= low, 1.0,
        np.where(y >= high, 0.0, ((high - y) / (high - low)) ** s))
    return np.clip(d, 0.0, 1.0)


def desirability_target(y, low, target, high, r=1, s=1):
    y = np.asarray(y, dtype=float)
    d = np.where(
        y < low, 0.0,
        np.where(
            y <= target, ((y - low) / (target - low)) ** r,
            np.where(y <= high, ((high - y) / (high - target)) ** s, 0.0)
        )
    )
    return np.clip(d, 0.0, 1.0)


def fill_auto_bounds(df, specs):
    """Fill in None low/high/target bounds from observed data min/max."""
    specs = {k: dict(v) for k, v in specs.items()}  # deep-ish copy
    for col, spec in specs.items():
        vals = df[col].astype(float)
        vmin, vmax = vals.min(), vals.max()
        if spec["goal"] == "max":
            if spec.get("low") is None:
                spec["low"] = vmin
            if spec.get("high") is None:
                spec["high"] = vmax
        elif spec["goal"] == "min":
            if spec.get("low") is None:
                spec["low"] = vmin
            if spec.get("high") is None:
                spec["high"] = vmax
        elif spec["goal"] == "target":
            if spec.get("low") is None:
                spec["low"] = vmin
            if spec.get("high") is None:
                spec["high"] = vmax
            if spec.get("target") is None:
                spec["target"] = (vmin + vmax) / 2
    return specs


def individual_desirability(y, spec):
    if spec["goal"] == "max":
        return desirability_max(y, spec["low"], spec["high"], spec.get("r", 1))
    elif spec["goal"] == "min":
        return desirability_min(y, spec["low"], spec["high"], spec.get("s", 1))
    elif spec["goal"] == "target":
        return desirability_target(
            y, spec["low"], spec["target"], spec["high"],
            spec.get("r", 1), spec.get("s", 1),
        )
    else:
        raise ValueError(f"Unknown goal '{spec['goal']}'")


def composite_desirability(d_dict, weights):
    """Weighted geometric mean: D = (prod d_i^w_i) ^ (1 / sum w_i)."""
    ws = np.array([weights[k] for k in d_dict])
    ds = np.array([np.asarray(d_dict[k], dtype=float) for k in d_dict])
    # avoid log(0): if any d_i is exactly 0, D must be 0
    with np.errstate(divide="ignore"):
        zero_mask = np.any(ds <= 0, axis=0)
        log_d = np.sum(ws[:, None] * np.log(np.where(ds > 0, ds, 1e-12)), axis=0)
        D = np.exp(log_d / ws.sum())
    D = np.where(zero_mask, 0.0, D)
    return D


# ----------------------------------------------------------------------
# 3. Row-wise desirability on the raw experimental data
# ----------------------------------------------------------------------
def score_raw_data(df, specs):
    df = df.copy()
    d_cols = {}
    for col, spec in specs.items():
        d = individual_desirability(df[col].values, spec)
        df[f"d({col})"] = d
        d_cols[col] = d
    weights = {col: spec["weight"] for col, spec in specs.items()}
    df["Composite D"] = composite_desirability(d_cols, weights)
    return df.sort_values("Composite D", ascending=False)


# ----------------------------------------------------------------------
# 4. Per-group quadratic response surface (Response vs Ratio) + optimizer
# ----------------------------------------------------------------------
def fit_quadratic(x, y):
    """Exact quadratic fit (3 pts -> 3 coeffs) or least-squares if more pts."""
    X = np.column_stack([np.ones_like(x), x, x ** 2])
    coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coeffs


def predict_quadratic(coeffs, x):
    x = np.asarray(x, dtype=float)
    return coeffs[0] + coeffs[1] * x + coeffs[2] * x ** 2


def optimize_groups(df, specs, factor_col=FACTOR_COL, group_cols=GROUP_COLS):
    weights = {col: spec["weight"] for col, spec in specs.items()}
    groups = df.groupby(group_cols)
    x_lo, x_hi = df[factor_col].min(), df[factor_col].max()

    group_models = {}   # (matrix, process) -> {response: coeffs}
    group_results = []

    for key, sub in groups:
        sub = sub.sort_values(factor_col)
        x = sub[factor_col].values.astype(float)
        models = {}
        for col in specs:
            models[col] = fit_quadratic(x, sub[col].values.astype(float))
        group_models[key] = models

        def neg_D(ratio):
            preds = {col: predict_quadratic(models[col], np.array([ratio]))
                      for col in specs}
            d = {col: individual_desirability(preds[col], specs[col])[0]
                  for col in specs}
            D = composite_desirability({k: np.array([v]) for k, v in d.items()},
                                         weights)[0]
            return -D

        res = minimize_scalar(neg_D, bounds=(x_lo, x_hi), method="bounded")
        best_ratio = res.x
        best_D = -res.fun
        best_preds = {col: predict_quadratic(models[col], np.array([best_ratio])).item()
                       for col in specs}

        group_results.append({
            **dict(zip(group_cols, key if isinstance(key, tuple) else (key,))),
            factor_col: best_ratio,
            "Composite D": best_D,
            **best_preds,
        })

    result_df = pd.DataFrame(group_results).sort_values("Composite D", ascending=False)
    return result_df, group_models


# ----------------------------------------------------------------------
# 5. Plots
# ----------------------------------------------------------------------
def plot_desirability_profiles(df, specs, group_models, factor_col=FACTOR_COL,
                                 group_cols=GROUP_COLS, out_path="desirability_profiles.png"):
    weights = {col: spec["weight"] for col, spec in specs.items()}
    groups = list(df.groupby(group_cols))
    n = len(groups)
    fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.5), sharey=True)
    if n == 1:
        axes = [axes]

    x_lo, x_hi = df[factor_col].min(), df[factor_col].max()
    xg = np.linspace(x_lo, x_hi, 100)

    for ax, (key, sub) in zip(axes, groups):
        models = group_models[key]
        d_curves = {}
        for col in specs:
            preds = predict_quadratic(models[col], xg)
            d_curves[col] = individual_desirability(preds, specs[col])
            ax.plot(xg, d_curves[col], "--", alpha=0.6, label=f"d({col})")

        D_curve = composite_desirability(d_curves, weights)
        ax.plot(xg, D_curve, "k-", linewidth=2.5, label="Composite D")

        best_idx = np.argmax(D_curve)
        ax.scatter([xg[best_idx]], [D_curve[best_idx]], color="red", zorder=5,
                    label=f"optimum ({xg[best_idx]:.1f})")

        title = key if isinstance(key, str) else " / ".join(map(str, key))
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(factor_col)
        ax.set_ylim(-0.05, 1.05)

    axes[0].set_ylabel("Desirability")
    axes[-1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)
    fig.suptitle("Individual & Composite Desirability vs Ratio (per Matrix/Process group)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out_path}")
    return fig


def plot_group_summary(result_df, group_cols=GROUP_COLS, out_path="desirability_summary.png"):
    labels = result_df[group_cols].astype(str).agg(" / ".join, axis=1)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, result_df["Composite D"], color="#4C72B0")
    ax.bar_label(bars, fmt="%.3f")
    ax.set_ylabel("Best achievable Composite Desirability")
    ax.set_ylim(0, 1.05)
    ax.set_title("Optimal Composite Desirability by Matrix / Process")
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out_path}")
    return fig


# ----------------------------------------------------------------------
# 6. Main
# ----------------------------------------------------------------------
def main(excel_path):
    df = pd.read_excel(excel_path)
    specs = fill_auto_bounds(df, RESPONSE_SPECS)

    print("=" * 70)
    print("Response bounds used for desirability transforms:")
    for col, spec in specs.items():
        print(f"  {col:20s} goal={spec['goal']:6s} low={spec.get('low'):.4f}  "
              f"high={spec.get('high'):.4f}" +
              (f"  target={spec.get('target'):.4f}" if spec["goal"] == "target" else ""))
    print("=" * 70)

    # (A) Score the raw experimental runs actually tested
    scored = score_raw_data(df, specs)
    print("\nExperimental runs ranked by composite desirability:\n")
    show_cols = GROUP_COLS + [FACTOR_COL] + list(specs.keys()) + ["Composite D"]
    print(scored[show_cols].to_string(index=False))

    best_run = scored.iloc[0]
    print(f"\nBest TESTED run: {dict(best_run[GROUP_COLS + [FACTOR_COL]])}, "
          f"D = {best_run['Composite D']:.4f}")

    # (B) Fit response surfaces per group and optimize Ratio continuously
    result_df, group_models = optimize_groups(df, specs)
    print("\nOptimized (continuous Ratio) result per Matrix/Process group:\n")
    print(result_df.to_string(index=False))

    best_overall = result_df.iloc[0]
    print(f"\nBEST OVERALL RECOMMENDATION:")
    print(f"  Matrix  = {best_overall['Matrix']}")
    print(f"  Process = {best_overall['Process']}")
    print(f"  Ratio   = {best_overall[FACTOR_COL]:.2f}")
    print(f"  Composite D = {best_overall['Composite D']:.4f}")
    for col in specs:
        print(f"  predicted {col} = {best_overall[col]:.4f}")

    # (C) Plots
    plot_desirability_profiles(df, specs, group_models)
    plot_group_summary(result_df)
    plt.show()

    # (D) Save tables
    scored.to_csv("desirability_scored_raw_data.csv", index=False)
    result_df.to_csv("desirability_optimized_results.csv", index=False)
    print("\nSaved: desirability_scored_raw_data.csv, desirability_optimized_results.csv")

    return scored, result_df


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "SpreadSheet.xlsx"
    main(path)
