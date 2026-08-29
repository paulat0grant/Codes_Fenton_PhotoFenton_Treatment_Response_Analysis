"""
Response Surface construction for SOR data.

Response variable : % COD removal
Independent vars   : Ratio, CTCI
Grouping features  : Matrix (class)  -> shown as marker color
                      Process (division) -> one fitted surface per Process

Model
-----
For each Process group a quadratic response-surface model is fitted:

    z = b0 + b1*x + b2*x^2 + b3*y + b4*x*y

    x = Ratio, y = CTCI, z = % COD removal

(A pure y^2 term is skipped because CTCI only takes two distinct values per
 dataset - the two Matrix classes - so a quadratic term in y cannot be
 estimated independently of the intercept/linear term. If your data has
 more than two CTCI levels, uncomment the y**2 column below to fit a full
 quadratic surface.)

Usage
-----
    python response_surface.py /path/to/SOR102.xlsx
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D projection)

import plotly.graph_objects as go
import plotly.express as px

def load_data(path, sheet_name=0):
    df = pd.read_excel(path, sheet_name=sheet_name)
    required = {"Matrix", "Process", "Ratio", "CTCI", "% COD removal"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in the sheet: {missing}")
    return df


def design_matrix(x, y, full_quadratic=False):
    """Build the regression design matrix for the response-surface model."""
    cols = [np.ones_like(x), x, x ** 2, y, x * y]
    if full_quadratic:
        cols.append(y ** 2)
    return np.column_stack(cols)


def fit_surface(x, y, z, full_quadratic=False):
    """Least-squares fit of the quadratic response surface. Returns coeffs, R2."""
    X = design_matrix(x, y, full_quadratic)
    coeffs, *_ = np.linalg.lstsq(X, z, rcond=None)
    z_pred = X @ coeffs
    ss_res = np.sum((z - z_pred) ** 2)
    ss_tot = np.sum((z - z.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return coeffs, r2


def predict_surface(coeffs, xg, yg, full_quadratic=False):
    Xg = design_matrix(xg.ravel(), yg.ravel(), full_quadratic)
    zg = Xg @ coeffs
    return zg.reshape(xg.shape)


def build_and_plot(df, out_path="response_surface.png"):
    processes = sorted(df["Process"].unique())
    matrices = sorted(df["Matrix"].unique())

    # distinct colors per Matrix (class), distinct surface colormaps per Process (division)
    matrix_colors = plt.cm.Set1(np.linspace(0, 0.5, len(matrices)))
    surface_cmaps = ["viridis", "plasma", "cividis", "magma"]

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    all_x = df["Ratio"].values.astype(float)
    all_y = df["CTCI"].values.astype(float)

    x_pad = (all_x.max() - all_x.min()) * 0.1 or 1
    y_pad = (all_y.max() - all_y.min()) * 0.15 or 0.01

    results = {}

    for i, proc in enumerate(processes):
        sub = df[df["Process"] == proc]
        x = sub["Ratio"].values.astype(float)
        y = sub["CTCI"].values.astype(float)
        z = sub["% COD removal"].values.astype(float)

        coeffs, r2 = fit_surface(x, y, z)
        results[proc] = {"coeffs": coeffs, "r2": r2}

        xg, yg = np.meshgrid(
            np.linspace(all_x.min() - x_pad, all_x.max() + x_pad, 30),
            np.linspace(all_y.min() - y_pad, all_y.max() + y_pad, 30),
        )
        zg = predict_surface(coeffs, xg, yg)

        ax.plot_surface(
            xg, yg, zg,
            cmap=surface_cmaps[i % len(surface_cmaps)],
            alpha=0.45, linewidth=0, antialiased=True,
        )

        # scatter the raw points for this Process, colored by Matrix
        for j, mat in enumerate(matrices):
            m = sub[sub["Matrix"] == mat]
            if len(m) == 0:
                continue
            ax.scatter(
                m["Ratio"], m["CTCI"], m["% COD removal"],
                color=matrix_colors[j],
                marker="o" if proc == processes[0] else "^",
                s=60, edgecolor="k", depthshade=True,
                label=f"Matrix {mat} - Process {proc}",
            )

    ax.set_xlabel("Fe2+/H2O2 Ratio")
    ax.set_ylabel("CTCI")
    ax.set_zlabel("% COD removal")
    ax.set_title("Response Surface: % COD removal vs Ratio & CTCI\n(surfaces = Process, markers colored by Matrix)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1.0), fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {out_path}")

    for proc, res in results.items():
        b0, b1, b2, b3, b4 = res["coeffs"]
        print(f"\nProcess {proc} response surface (R^2 = {res['r2']:.4f}):")
        print(
            f"  Residual_CTCI = {b0:.5f} + {b1:.5f}*Ratio + {b2:.6f}*Ratio^2 "
            f"+ {b3:.5f}*CTCI + {b4:.5f}*Ratio*CTCI"
        )

    return results, fig

def build_and_plot(df):

    processes = sorted(df["Process"].unique())
    matrices = sorted(df["Matrix"].unique())

    # Colors for Matrix
    colors = px.colors.qualitative.Set1

    # Different surface colors
    surface_colors = ["Viridis", "Plasma", "Cividis", "Magma"]

    fig = go.Figure()

    all_x = df["Ratio"].values.astype(float)
    all_y = df["CTCI"].values.astype(float)

    x_pad = (all_x.max() - all_x.min()) * 0.10
    y_pad = (all_y.max() - all_y.min()) * 0.10

    results = {}

    for i, proc in enumerate(processes):

        sub = df[df["Process"] == proc]

        x = sub["Ratio"].values.astype(float)
        y = sub["CTCI"].values.astype(float)
        z = sub["% COD removal"].values.astype(float)

        coeffs, r2 = fit_surface(x, y, z)
        results[proc] = {"coeffs": coeffs, "r2": r2}

        # Prediction grid
        xg, yg = np.meshgrid(
            np.linspace(all_x.min()-x_pad,
                        all_x.max()+x_pad, 50),
            np.linspace(all_y.min()-y_pad,
                        all_y.max()+y_pad, 50)
        )

        zg = predict_surface(coeffs, xg, yg)

        # Response surface
        fig.add_trace(
            go.Surface(
                x=xg,
                y=yg,
                z=zg,
                colorscale=surface_colors[i % len(surface_colors)],
                opacity=0.55,
                showscale=False,
                name=f"Process {proc}"
            )
        )

        # Scatter points
        for j, mat in enumerate(matrices):

            m = sub[sub["Matrix"] == mat]

            if len(m) == 0:
                continue

            fig.add_trace(
                go.Scatter3d(
                    x=m["Ratio"],
                    y=m["CTCI"],
                    z=m["% COD removal"],

                    mode="markers",

                    marker=dict(
                        size=7,
                        color=colors[j],
                        symbol="circle" if proc == processes[0] else "diamond",
                        line=dict(color="black", width=1)
                    ),

                    name=f"Matrix {mat} | Process {proc}"
                )
            )

    fig.update_layout(

        title="Interactive Response Surface",

        width=1000,
        height=750,

        scene=dict(

            xaxis_title="Fe2+:H2O2 Ratio",
            yaxis_title="CTCI",
            zaxis_title="% COD removal",

            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2)
            )
        ),

        legend=dict(
            x=0.02,
            y=0.98
        )
    )

    fig.show()

    # Print regression equations
    for proc, res in results.items():

        b0, b1, b2, b3, b4 = res["coeffs"]

        print(f"\nProcess {proc} (R² = {res['r2']:.4f})")

        print(
            f"% COD removal = "
            f"{b0:.5f} + "
            f"{b1:.5f}·Ratio + "
            f"{b2:.5f}·Ratio² + "
            f"{b3:.5f}·CTCI + "
            f"{b4:.5f}·Ratio×CTCI"
        )

    return results

if __name__ == "__main__":
    excel_path = sys.argv[1] if len(sys.argv) > 1 else "CTCI.xlsx"
    data = load_data(excel_path)
    build_and_plot(data)
