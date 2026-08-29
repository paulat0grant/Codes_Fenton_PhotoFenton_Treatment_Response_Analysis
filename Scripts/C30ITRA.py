"""
Heatmap Generator
------------------
Reads an Excel file where:
    - Rows    = Parameters
    - Columns = Removal Increments
    - Values  = Percentages

Produces a color-coded heatmap (PNG) and displays it on screen.

USAGE (command line):
    python heatmap_generator.py your_data.xlsx
    python heatmap_generator.py your_data.xlsx --sheet "Sheet1" --cmap viridis

If no file is given, it will look for the first .xlsx file in the
current folder.
"""

import sys
import argparse
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(path: str, sheet, index_col: int = 0) -> pd.DataFrame:
    """Load Excel data with parameters as the row index."""
    df = pd.read_excel(path, sheet_name=sheet, index_col=index_col)

    # Drop fully empty rows/columns (common in messy Excel exports)
    df = df.dropna(how="all").dropna(how="all", axis=1)

    return df


def clean_percentages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize values to plain numeric percentages (e.g. 85.0 for 85%).
    Handles:
        - Strings like "85%"
        - Fractions like 0.85 (assumed if max value <= 1)
        - Already-numeric percentages like 85
    """
    # Convert string percentages ("85%") to numeric
    if df.dtypes.apply(lambda d: d == object).any():
        df = df.apply(
            lambda col: col.astype(str).str.replace("%", "", regex=False)
            if col.dtype == object else col
        )
        df = df.apply(pd.to_numeric, errors="coerce")

    # If everything looks like a fraction (0-1), scale to 0-100
    numeric_vals = df.values.astype(float)
    finite_vals = numeric_vals[~pd.isnull(numeric_vals)]
    if finite_vals.size and finite_vals.max() <= 1.0:
        df = df * 100

    return df


def plot_heatmap(df: pd.DataFrame, cmap: str, output: str, title: str, base_fontsize: int = 16):
    n_rows, n_cols = df.shape
    fig_w = max(6, 1.1 * n_cols + 3)
    fig_h = max(4, 0.55 * n_rows + 2)

    plt.figure(figsize=(fig_w, fig_h))
    ax = sns.heatmap(
        df,
        annot=True,
        fmt=".1f",
        cmap=cmap,
        linewidths=0.5,
        linecolor="white",
    )
    ax.set_xlabel("Removal Increment", fontsize=base_fontsize - 2, fontweight="bold")
    ax.set_ylabel("Parameter", fontsize=base_fontsize - 2, fontweight="bold")
    ax.set_title(title, fontsize=base_fontsize, fontweight="bold")

    ax.tick_params(axis="both", labelsize=base_fontsize - 5)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=base_fontsize - 5)
    cbar.set_label("Percentage (%)", fontsize=base_fontsize - 3)

    plt.tight_layout()
    plt.savefig(output, dpi=300)
    print(f"Heatmap saved to: {output}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Generate a heatmap from Excel data.")
    parser.add_argument("file", nargs="?", help="Path to Excel file (.xlsx)")
    parser.add_argument("--sheet", default=0, help="Sheet name or index (default: first sheet)")
    parser.add_argument("--index-col", type=int, default=0, help="Column index for row labels (default: 0)")
    parser.add_argument("--cmap", default="RdYlGn", help="Matplotlib/Seaborn colormap (default: RdYlGn)")
    parser.add_argument("--output", default="heatmap.png", help="Output PNG filename")
    parser.add_argument("--title", default="Incremental Treatment Response Heatmap", help="Chart title")
    parser.add_argument("--fontsize", type=int, default=16, help="Base font size for title (axis labels/ticks scale proportionally)")
    args = parser.parse_args()

    # Resolve input file
    file_path = args.file
    if not file_path:
        candidates = glob.glob("T_F.xlsx")
        if not candidates:
            sys.exit("No Excel file specified and none found in current directory.")
        file_path = candidates[0]
        print(f"No file given — using detected file: {file_path}")

    df = load_data(file_path, args.sheet, args.index_col)
    df = clean_percentages(df)

    print("\nLoaded data preview:")
    print(df.head())

    plot_heatmap(df, args.cmap, args.output, args.title, args.fontsize)


if __name__ == "__main__":
    main()
