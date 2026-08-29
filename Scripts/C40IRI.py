"""
Heatmap with Discrete Value Categories
----------------------------------------
Bins values into 4 categories:
    < 0.3
    0.3 - 1
    1 - 2
    > 2

Rows = Parameters, Columns = T_F, T_PF, DI_F, DI_PF (or any columns you have).

USAGE:
    python heatmap_binned.py your_data.xlsx
    python heatmap_binned.py your_data.xlsx --sheet "Sheet1"

If no file is given, the script falls back to the sample data shown
in your screenshot so you can test it immediately.
"""

import sys
import argparse
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import seaborn as sns


# ------------------ Sample data (fallback / demo) ------------------
SAMPLE_DATA = {
    "T_F":   [0.014927, 0.189135, 6.347664, 0.300036, 6.071685, 1.2519, 0.21978, 2.517052, 1.903894, 3.074897 ],
    "T_PF":  [1.467105, 1.281776, 0.144527, 0.131146, 0.144131, 0.097371, 5.138194, 2.242953, 0.594504, 1.411869 ],
    "DI_F":  [0.057321, -0.03004, 18.69323, 0.227954, 13.99099, 0.369102, 5.217391, 0.088271, 0.228002, 0.698885 ],
    "DI_PF": [1.263415, 2.827818, 0.287102, 0.695777, 0.317305, 0.734597, -0.24324, 0.097591, 2.079791, 1.000287 ],
}
SAMPLE_INDEX = [
    "Colour", "Turbidity", "TDS", "TSS", "TS", "Chloride",
    "Sulphate", "COD", "Amm. N", "Nitrate",
]


def load_data(path, sheet, index_col=0) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, index_col=index_col)
    df = df.dropna(how="all").dropna(how="all", axis=1)
    return df.apply(pd.to_numeric, errors="coerce")


def plot_binned_heatmap(df: pd.DataFrame, output: str, title: str, base_fontsize: int = 16):
    # Bin edges and matching colors (adjust colors as you like)
    bounds = [-np.inf, 0.3, 1, 2, np.inf]
    colors = ["#2ca02c", "#ffdd57", "#ff9933", "#d62728"]  # green, yellow, orange, red
    labels = ["< 0.3", "0.3 - 1", "1 - 2", "> 2"]

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, cmap.N)

    n_rows, n_cols = df.shape
    fig_w = max(6, 1.3 * n_cols + 3)
    fig_h = max(4, 0.55 * n_rows + 2)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    hm = sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap=cmap,
        norm=norm,
        linewidths=0.5,
        linecolor="white",
        cbar=False,          # we'll add a custom discrete legend instead
        annot_kws={"fontsize": base_fontsize - 4},
        ax=ax,
    )

    ax.set_xlabel("Sample & Treatment Type", fontsize=base_fontsize - 2, fontweight="bold")
    ax.set_ylabel("Wastewater Parameter", fontsize=base_fontsize - 2, fontweight="bold")
    ax.set_title(title, fontsize=base_fontsize, fontweight="bold")
    ax.tick_params(axis="both", labelsize=base_fontsize - 5)

    # Custom discrete legend (patches) instead of a continuous colorbar
    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=c, edgecolor="white", label=l) for c, l in zip(colors, labels)]
    ax.legend(
        handles=legend_handles,
        title="Categories Range",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=base_fontsize - 5,
        title_fontsize=base_fontsize - 4,
        frameon=False,
    )

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches="tight")
    print(f"Heatmap saved to: {output}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Generate a binned/categorical heatmap.")
    parser.add_argument("file", nargs="?", help="Path to Excel file (.xlsx)")
    parser.add_argument("--sheet", default=0, help="Sheet name or index")
    parser.add_argument("--index-col", type=int, default=0, help="Column index for row labels")
    parser.add_argument("--output", default="heatmap_binned.png", help="Output PNG filename")
    parser.add_argument("--title", default="Heatmap for Incremental Response Index (IRI)", help="Chart title")
    parser.add_argument("--fontsize", type=int, default=16, help="Base font size")
    args = parser.parse_args()

    if args.file:
        df = load_data(args.file, args.sheet, args.index_col)
    else:
        candidates = glob.glob("data101.xlsx")
        if candidates:
            print(f"No file given — using detected file: {candidates[0]}")
            df = load_data(candidates[0], args.sheet, args.index_col)
        else:
            print("No file given and none found — using sample data from screenshot.")
            df = pd.DataFrame(SAMPLE_DATA, index=SAMPLE_INDEX)

    print("\nLoaded data preview:")
    print(df.head())

    plot_binned_heatmap(df, args.output, args.title, args.fontsize)


if __name__ == "__main__":
    main()
