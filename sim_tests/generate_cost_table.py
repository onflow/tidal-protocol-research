#!/usr/bin/env python3
"""
FCM Cost Estimate Table — 2022 Bear Market

Reads the simulation output CSVs and produces a cost estimate table
with symbolic placeholder costs (c_hc, c_sr, c_er).

Outputs:
  fcm_cost_estimate_table.csv  — machine-readable table
  fig3_cost_estimate_table.png — formatted table figure
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT       = Path(__file__).parent.parent
RESULTS    = ROOT / "tidal_protocol_sim/results/FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3"
HF_CSV     = RESULTS / "fcm_hf_history.csv"
REPORT_CSV = RESULTS / "fcm_rebalance_detail_report.csv"


# ---------------------------------------------------------------------------
# Read counts from existing CSVs
# ---------------------------------------------------------------------------
def load_counts():
    n_hc, n_sr, n_er = 0, 0, 0
    with open(HF_CSV, newline="") as f:
        for row in csv.DictReader(f):
            t = row["event_type"]
            if t == "HC":
                n_hc += 1
            elif t == "SR":
                n_sr += 1
            elif t == "ER":
                n_er += 1
    return n_hc, n_sr, n_er


# ---------------------------------------------------------------------------
# Build table rows
# ---------------------------------------------------------------------------
def build_table(n_hc, n_sr, n_er):
    """
    Returns a list of row dicts, each with:
      label, count, unit_cost, formula, note
    """
    rows = [
        {
            "component":  "Health Check (HC)",
            "description": "Hourly position check — no rebalance needed",
            "count":       n_hc,
            "unit_cost":   "c_hc",
            "formula":     f"{n_hc:,} × c_hc",
        },
        {
            "component":  "Safety Rebalance (SR)",
            "description": "HF < 1.1 — sell YT, repay MOET debt",
            "count":       n_sr,
            "unit_cost":   "c_sr",
            "formula":     f"{n_sr:,} × c_sr",
        },
        {
            "component":  "Efficiency Rebalance (ER)",
            "description": "HF > 1.5 — borrow MOET, buy more YT",
            "count":       n_er,
            "unit_cost":   "c_er",
            "formula":     f"{n_er:,} × c_er",
        },
    ]
    return rows


# ---------------------------------------------------------------------------
# Write CSV
# ---------------------------------------------------------------------------
def write_csv(rows, n_hc, n_sr, n_er, out_dir: Path):
    path = out_dir / "fcm_cost_estimate_table.csv"
    fieldnames = ["component", "description", "count", "unit_cost", "formula"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        # Summary rows
        writer.writerow({
            "component":  "── HEALTH CHECK COST ──",
            "description": "Total cost of hourly position monitoring",
            "count":       n_hc,
            "unit_cost":   "c_hc",
            "formula":     f"{n_hc:,} × c_hc",
        })
        writer.writerow({
            "component":  "── TOTAL REBALANCE COST ──",
            "description": "Full annual protocol operating cost",
            "count":       n_hc + n_sr + n_er,
            "unit_cost":   "c_hc + c_sr + c_er",
            "formula":     f"{n_hc:,}×c_hc + {n_sr:,}×c_sr + {n_er:,}×c_er",
        })
    print(f"  Saved: {path.name}")
    return path


# ---------------------------------------------------------------------------
# Generate PNG table figure
# ---------------------------------------------------------------------------
def write_figure(rows, n_hc, n_sr, n_er, out_dir: Path):
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.axis("off")

    fig.suptitle(
        "FCM Annual Cost Estimate — 2022 Bear Market\n"
        "HF thresholds: ER trigger 1.5 / SR trigger 1.1 / target 1.3  |  "
        "Hourly health checks  |  Max 1 rebalance cycle per trigger",
        fontsize=11, fontweight="bold", y=0.98,
    )

    col_labels = ["Component", "Description", "Count", "Unit Cost", "Cost Formula"]

    # Detail rows
    detail_data = [
        [r["component"], r["description"], f"{r['count']:,}", r["unit_cost"], r["formula"]]
        for r in rows
    ]

    # Summary rows
    summary_data = [
        [
            "Health Check Cost",
            "Total cost of hourly position monitoring",
            f"{n_hc:,}",
            "c_hc",
            f"{n_hc:,} × c_hc",
        ],
        [
            "Total Rebalance Cost",
            "Full annual protocol operating cost",
            f"{n_hc + n_sr + n_er:,}",
            "c_hc, c_sr, c_er",
            f"{n_hc:,}×c_hc  +  {n_sr:,}×c_sr  +  {n_er:,}×c_er",
        ],
    ]

    all_data = detail_data + [["", "", "", "", ""]] + summary_data

    tbl = ax.table(
        cellText=all_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1, 2.0)

    # Column widths (fractions of figure width)
    col_widths = [0.18, 0.30, 0.07, 0.10, 0.25]
    for (row_idx, col_idx), cell in tbl.get_celld().items():
        cell.set_linewidth(0.5)
        cell.PAD = 0.06
        if col_idx >= 0:
            cell.set_width(col_widths[col_idx])

    # Header row styling
    header_colour = "#2c3e50"
    for col_idx in range(len(col_labels)):
        cell = tbl[0, col_idx]
        cell.set_facecolor(header_colour)
        cell.set_text_props(color="white", fontweight="bold")

    # Detail rows: alternating light background
    row_colours = ["#eaf4fb", "#ffffff"]
    for row_idx in range(1, len(detail_data) + 1):
        for col_idx in range(len(col_labels)):
            tbl[row_idx, col_idx].set_facecolor(row_colours[(row_idx - 1) % 2])

    # Blank separator row
    sep_row = len(detail_data) + 1
    for col_idx in range(len(col_labels)):
        tbl[sep_row, col_idx].set_facecolor("#f8f8f8")
        tbl[sep_row, col_idx].set_linewidth(0)

    # Summary rows: distinct colour
    summary_colours = ["#d5e8d4", "#dae8fc"]   # light green, light blue
    for i, colour in enumerate(summary_colours):
        row_idx = sep_row + 1 + i
        for col_idx in range(len(col_labels)):
            cell = tbl[row_idx, col_idx]
            cell.set_facecolor(colour)
            cell.set_text_props(fontweight="bold")

    # Footer note
    fig.text(
        0.5, 0.01,
        "Placeholder unit costs: c_hc = compute cost per health check  |  "
        "c_sr = compute cost per safety rebalance  |  "
        "c_er = compute cost per efficiency rebalance",
        ha="center", fontsize=8, color="#555555", style="italic",
    )

    out = out_dir / "fig3_cost_estimate_table.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading simulation counts...")
    n_hc, n_sr, n_er = load_counts()
    print(f"  HC: {n_hc:,}  |  SR: {n_sr}  |  ER: {n_er}")

    rows = build_table(n_hc, n_sr, n_er)

    print("\nCost Estimate Table:")
    print(f"  Health Check Cost  = {n_hc:,} × c_hc")
    print(f"  Total Rebalance Cost = {n_hc:,}×c_hc  +  {n_sr}×c_sr  +  {n_er}×c_er")

    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(rows, n_hc, n_sr, n_er, RESULTS)
    write_figure(rows, n_hc, n_sr, n_er, RESULTS)

    print("\nDone.")


if __name__ == "__main__":
    main()
