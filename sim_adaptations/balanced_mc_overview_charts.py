"""
Overview and per-run charts for balanced_scenario_monte_carlo results.

Replaces performance_matrix_heatmap.png with:
  - overview_bars.png: grouped bar charts (survival rate, liquidated collateral value, position degradation)
  - per_run_lollipops.png: per-run lollipop charts for the same metrics

Usage:
    python sim_adaptations/balanced_mc_overview_charts.py [--results-dir DIR] [--output-dir DIR]
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

DEFAULT_RESULTS_DIR = "tidal_protocol_sim/results_commit-ba544b1/Balanced_Scenario_Monte_Carlo"
DEFAULT_DPI = 1000


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_csv(results_dir: Path) -> pd.DataFrame:
    return pd.read_csv(results_dir / "comprehensive_agent_comparison.csv")


def load_json_survival_fields(results_dir: Path) -> tuple[pd.DataFrame, float]:
    """Extract per-agent HT survival fields and initial BTC price from the JSON.

    Returns:
        (DataFrame[agent_id, scenario, min_hf_before_rebalance, emergency_liquidations],
         initial_btc_price)
    """
    with open(results_dir / "comprehensive_ht_vs_aave_results.json") as f:
        data = json.load(f)

    rows = []
    initial_prices = set()
    for scenario in data["scenario_results"]:
        scenario_name = scenario["scenario_name"]

        # Extract initial_btc_price from whichever run type has protocol_metrics
        for run_type in ("high_tide_runs", "aave_runs"):
            for run in scenario["detailed_runs"].get(run_type, []):
                pm = run.get("protocol_metrics", {})
                if "initial_btc_price" in pm:
                    initial_prices.add(pm["initial_btc_price"])

        for run in scenario["detailed_runs"]["high_tide_runs"]:
            for agent in run["agent_outcomes"]:
                events = agent.get("rebalancing_events_list", [])
                hf_values = [e["health_factor_before"] for e in events if "health_factor_before" in e]
                rows.append({
                    "Agent_ID": agent["agent_id"],
                    "Scenario": scenario_name,
                    "min_hf_before_rebalance": min(hf_values) if hf_values else np.nan,
                    "emergency_liquidations": agent.get("emergency_liquidations", 0),
                })

    if len(initial_prices) != 1:
        raise ValueError(f"Expected exactly one initial_btc_price across runs, got {initial_prices}")
    btc_initial_price = initial_prices.pop()

    return pd.DataFrame(rows), btc_initial_price


# ---------------------------------------------------------------------------
# Metric computation (vectorized)
# ---------------------------------------------------------------------------

def compute_metrics(csv_df: pd.DataFrame, json_df: pd.DataFrame,
                    btc_initial_price: float) -> pd.DataFrame:
    """Compute per-agent metrics, returning one row per agent with all metrics."""
    df = csv_df.copy()

    # Merge JSON-derived HT survival fields
    df = df.merge(json_df, on=["Agent_ID", "Scenario"], how="left")

    # --- Survival metrics ---
    # "Survived" = agent's entire principal was NOT reduced by liquidation events.
    #   AAVE (aave_protocol_engine.py:376): len(liquidation_history) == 0
    #   HT: two tiers, tracked separately:
    #     (a) rebalancing sufficiency — min HF before any rebalancing stayed > 1.0
    #     (b) no collateral liquidation — emergency_liquidations == 0
    # Overview charts use (b) for FCM and the engine's Survived flag for AAVE.
    df["survived_rebal_suff"] = np.where(
        df["Strategy"] == "High_Tide",
        df["min_hf_before_rebalance"].isna() | (df["min_hf_before_rebalance"] > 1.0),
        df["Survived"],
    )
    df["survived_no_collat_liq"] = np.where(
        df["Strategy"] == "High_Tide",
        df["emergency_liquidations"].fillna(0) == 0,
        df["Survived"],
    )

    # --- Liquidated collateral value ---
    df["liquidated_collateral_value"] = df["Cost_of_Liquidation"].fillna(0.0)

    # --- Position degradation (at crash bottom) ---
    df["position_degradation"] = df["Final_BTC_Price"] - df["Final_Net_Position"]

    # --- Recovery degradation (after full BTC price recovery to P_0) ---
    # FCM: slippage is stablecoin-denominated → unchanged with price
    # AAVE: all value is BTC-denominated (YT=0, debt=0 post-sim) → scales with price
    P_0 = btc_initial_price
    P_bottom = df["Final_BTC_Price"]
    effective_btc = df["Final_Net_Position"] / P_bottom
    recovery_net = effective_btc * P_0
    recovery_degrad_aave = P_0 - recovery_net

    df["recovery_degradation"] = np.where(
        df["Strategy"] == "High_Tide",
        df["position_degradation"],  # FCM: fixed cost, no change
        recovery_degrad_aave,
    )

    return df


def per_run_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-agent metrics to per (Strategy, Scenario) level."""
    base = df.groupby(["Strategy", "Scenario"], sort=False).agg(
        survival_rate_rebal_suff=("survived_rebal_suff", "mean"),
        survival_rate_no_collat_liq=("survived_no_collat_liq", "mean"),
        mean_liq_collat_all=("liquidated_collateral_value", "mean"),
        mean_position_degradation=("position_degradation", "mean"),
        mean_recovery_degradation=("recovery_degradation", "mean"),
        n_agents=("Agent_ID", "count"),
    ).reset_index()

    # Mean liquidated collateral across only liquidated agents (value > 0)
    liquidated = df[df["liquidated_collateral_value"] > 0]
    if not liquidated.empty:
        liq_only = liquidated.groupby(["Strategy", "Scenario"], sort=False).agg(
            mean_liq_collat_liquidated=("liquidated_collateral_value", "mean"),
        ).reset_index()
        base = base.merge(liq_only, on=["Strategy", "Scenario"], how="left")
    else:
        base["mean_liq_collat_liquidated"] = np.nan

    base["mean_liq_collat_liquidated"] = base["mean_liq_collat_liquidated"].fillna(0.0)

    # --- AAVE survived/liquidated split for position degradation ---
    aave = df[df["Strategy"] == "AAVE"]
    aave_survived = aave[aave["Survived"] == True]  # noqa: E712
    aave_liquidated = aave[aave["Survived"] == False]  # noqa: E712

    for subset, suffix in [(aave_survived, "_aave_surv"), (aave_liquidated, "_aave_liq")]:
        if not subset.empty:
            sub_agg = subset.groupby("Scenario", sort=False).agg(
                **{f"mean_pos_degrad{suffix}": ("position_degradation", "mean"),
                   f"mean_recov_degrad{suffix}": ("recovery_degradation", "mean")},
            ).reset_index()
            base = base.merge(sub_agg, on="Scenario", how="left")
        else:
            base[f"mean_pos_degrad{suffix}"] = np.nan
            base[f"mean_recov_degrad{suffix}"] = np.nan

    for col in ["mean_pos_degrad_aave_surv", "mean_recov_degrad_aave_surv",
                "mean_pos_degrad_aave_liq", "mean_recov_degrad_aave_liq"]:
        base[col] = base[col].fillna(0.0)

    return base


def overview_summary(run_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-run metrics to per-Strategy overview (mean ± std across runs)."""
    return run_df.groupby("Strategy", sort=False).agg(
        mean_surv_rebal=("survival_rate_rebal_suff", "mean"),
        std_surv_rebal=("survival_rate_rebal_suff", "std"),
        mean_surv_no_liq=("survival_rate_no_collat_liq", "mean"),
        std_surv_no_liq=("survival_rate_no_collat_liq", "std"),
        mean_liq_all=("mean_liq_collat_all", "mean"),
        std_liq_all=("mean_liq_collat_all", "std"),
        mean_liq_liquidated=("mean_liq_collat_liquidated", "mean"),
        std_liq_liquidated=("mean_liq_collat_liquidated", "std"),
        mean_pos_degrad=("mean_position_degradation", "mean"),
        std_pos_degrad=("mean_position_degradation", "std"),
        mean_recov_degrad=("mean_recovery_degradation", "mean"),
        std_recov_degrad=("mean_recovery_degradation", "std"),
        # AAVE survived/liquidated split for position degradation charts
        mean_pos_degrad_aave_surv=("mean_pos_degrad_aave_surv", "mean"),
        std_pos_degrad_aave_surv=("mean_pos_degrad_aave_surv", "std"),
        mean_recov_degrad_aave_surv=("mean_recov_degrad_aave_surv", "mean"),
        std_recov_degrad_aave_surv=("mean_recov_degrad_aave_surv", "std"),
        mean_pos_degrad_aave_liq=("mean_pos_degrad_aave_liq", "mean"),
        std_pos_degrad_aave_liq=("mean_pos_degrad_aave_liq", "std"),
        mean_recov_degrad_aave_liq=("mean_recov_degrad_aave_liq", "mean"),
        std_recov_degrad_aave_liq=("mean_recov_degrad_aave_liq", "std"),
    ).reset_index()


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------

FCM_COLOR = "#2E86AB"
FCM_COLOR = "#68B8D7"
AAVE_COLOR = "#D3D3D3"
AAVE_DARK_COLOR = "#9E9E9E"

RUN_LABELS_MAP = {
    "Balanced_Run_1": "Run 1",
    "Balanced_Run_2": "Run 2",
    "Balanced_Run_3": "Run 3",
    "Balanced_Run_4": "Run 4",
    "Balanced_Run_5": "Run 5",
}


def _run_label(scenario: str) -> str:
    return RUN_LABELS_MAP.get(scenario, scenario)


# ---------------------------------------------------------------------------
# Overview bar charts
# ---------------------------------------------------------------------------

def plot_overview_bars(overview: pd.DataFrame, aave_surv_pct: float,
                      output_path: Path) -> None:
    """Two-panel bar chart: survival rate (left) and liquidated collateral (right).

    Layout techniques:
    - X-tick labels hidden; bar identity conveyed via per-panel legend boxes
      placed below each chart (bbox_to_anchor in axes coords).
    - Right panel y-axis on right side — panels read outward from center.
    - Error bars drawn selectively via ax.errorbar() rather than ax.bar(yerr=...)
      to avoid matplotlib drawing cap remnants on zero-error bars.
    - FCM $0 bar in right panel made visible via colored hlines at baseline.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.5),
                              gridspec_kw={"width_ratios": [1, 1.2]})

    ht = overview.loc[overview["Strategy"] == "High_Tide"].iloc[0]
    aave = overview.loc[overview["Strategy"] == "AAVE"].iloc[0]

    aave_liq_pct = 100 - aave_surv_pct

    # --- Panel 1: Survival Rate (FCM "no collateral liquidation" only + AAVE) ---
    # FCM is 100% across all runs (zero variance) — no error bar.
    # AAVE varies across runs — error bar on AAVE only (index 1).
    ax = axes[0]
    labels = ["FCM", "AAVE"]  # bar x-positions: 0=FCM, 1=AAVE
    vals = [ht["mean_surv_no_liq"] * 100, aave["mean_surv_rebal"] * 100]
    colors = [FCM_COLOR, AAVE_COLOR]
    bars = ax.bar(labels, vals, color=colors, edgecolor="white", width=0.5)
    # `pyplot.errorbar` is designed as a general-purpose function for plotting data points with error bar. 
    # We re-use this function here to selectively plot error bars for the `AAVE` survival rate. 
    # The datapoint itself is already represented by the Aave bar, so we only need to plot the errors.
    # Hence we use the parameter fmt=`none` to suppresses the point marker and draw only whisker+caps.
    # errorbar(x, y, yerr): x is bar position, y is bar height (whisker center),
    ax.errorbar(1, vals[1], yerr=aave["std_surv_rebal"] * 100,
                fmt="none", capsize=4, color="black")
    ax.set_ylabel("Survival Rate [%]")
    ax.set_title("Survival Rate", fontsize=12, pad=18)
    ax.text(0.5, 1.02, "(fraction of agents with principal unaffected by liquidations)",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color="0.4")

    ax.set_ylim(0, 115)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, 2, f"{v:.0f}%",
                ha="center", va="bottom", fontsize=12, fontweight="bold")

    surv_legend = [
        Patch(facecolor=FCM_COLOR, edgecolor="white",
              label="FCM: no collateral liquidated"),
        Patch(facecolor=AAVE_COLOR, edgecolor="white",
              label=f"AAVE: {aave_surv_pct:.0f}% of agents unaffected by liquidation"),
    ]
    ax.legend(handles=surv_legend, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.05), frameon=True, edgecolor="0.8", fancybox=False)

    # --- Panel 2: Liquidated Collateral Value (per agent) ---
    # Three bars: FCM ($0), AAVE all-agents avg, AAVE liquidated-only avg.
    ax = axes[1]
    labels2 = ["FCM", "AAVE\n(all agents)", "AAVE\n(liquidated\nonly)"]  # x: 0, 1, 2
    vals2 = [ht["mean_liq_all"], aave["mean_liq_all"], aave["mean_liq_liquidated"]]
    colors2 = [FCM_COLOR, AAVE_COLOR, AAVE_DARK_COLOR]
    bars2 = ax.bar(labels2, vals2, color=colors2, edgecolor="white", width=0.6)
    # Error bars on 0=FCM and 1=AAVE-all only; 2=AAVE-liquidated-only omitted
    # (near-zero variance — all liquidated agents face same 50% debt + 5% penalty).
    # `pyplot.errorbar` is designed as a general-purpose function for plotting data points with error bar. 
    # We re-use this function here to selectively plot error bars for the `AAVE` survival rate. 
    # The datapoint itself is already represented by the Aave bar, so we only need to plot the errors.
    # Hence we use the parameter fmt=`none` to suppresses the point marker and draw only whisker+caps.
    # errorbar(x, y, yerr): x is bar position, y is bar height (whisker center),
    for i, err in [(0, ht["std_liq_all"]), (1, aave["std_liq_all"])]:
        ax.errorbar(i, vals2[i], yerr=err, fmt="none", capsize=4, color="black")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Average Liquidated Collateral [$/agent]")
    ax.set_title("Liquidated Collateral Value")
    for bar, v in zip(bars2, vals2):
        ax.text(bar.get_x() + bar.get_width() / 2, 200, f"${v:,.0f}",
                ha="center", va="bottom", fontsize=12, fontweight="bold")
    fcm_bar = bars2[0]
    ax.hlines(y=0, xmin=fcm_bar.get_x(), xmax=fcm_bar.get_x() + fcm_bar.get_width(),
              color=FCM_COLOR, linewidth=3, zorder=3)

    liq_legend = [
        Patch(facecolor=FCM_COLOR, edgecolor="white",
              label="FCM: no collateral liquidated"),
        Patch(facecolor=AAVE_COLOR, edgecolor="white",
              label="AAVE: average across all agents (including unaffected)"),
        Patch(facecolor=AAVE_DARK_COLOR, edgecolor="white",
              label=f"AAVE: average across liquidated agents only ({aave_liq_pct:.0f}%)"),
    ]
    ax.legend(handles=liq_legend, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.05), frameon=True, edgecolor="0.8", fancybox=False)

    for ax in axes:
        ax.tick_params(axis="x", length=0, pad=6)
        ax.set_xticklabels([])

    fig.suptitle("FCM vs AAVE: Liquidation Prevention During Synthetic Flash Crash Scenario",
                 fontsize=13, fontweight="bold", y=0.93)
    fig.tight_layout(rect=[0, 0.12, 1, 0.95])
    fig.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_position_degradation(overview: pd.DataFrame, aave_surv_pct: float,
                              output_path: Path) -> None:
    """Grouped dual-scenario bar chart: crash bottom vs. full recovery.

    Three bar groups (FCM, AAVE survived, AAVE liquidated) × two scenarios.
    """
    ht = overview.loc[overview["Strategy"] == "High_Tide"].iloc[0]
    aave = overview.loc[overview["Strategy"] == "AAVE"].iloc[0]

    scenarios = ["At crash bottom", "After full recovery"]
    aave_liq_pct = 100 - aave_surv_pct
    groups = [
        "FCM agents (rebalancing cost only, no liquidation losses)",
        f"AAVE agents unaffected by liquidation ({aave_surv_pct:.0f}%)",
        f"AAVE agents with collateral liquidated ({aave_liq_pct:.0f}%)",
    ]
    colors = [FCM_COLOR, AAVE_COLOR, AAVE_DARK_COLOR]

    bottom_vals = [ht["mean_pos_degrad"],
                   aave["mean_pos_degrad_aave_surv"],
                   aave["mean_pos_degrad_aave_liq"]]
    bottom_errs = [ht["std_pos_degrad"],
                   aave["std_pos_degrad_aave_surv"],
                   aave["std_pos_degrad_aave_liq"]]
    recovery_vals = [ht["mean_recov_degrad"],
                     aave["mean_recov_degrad_aave_surv"],
                     aave["mean_recov_degrad_aave_liq"]]
    recovery_errs = [ht["std_recov_degrad"],
                     aave["std_recov_degrad_aave_surv"],
                     aave["std_recov_degrad_aave_liq"]]

    vals_by_scenario = [bottom_vals, recovery_vals]
    errs_by_scenario = [bottom_errs, recovery_errs]

    n_groups = len(groups)
    n_scenarios = len(scenarios)
    bar_width = 0.22
    group_gap = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))

    for s_idx in range(n_scenarios):
        group_center = s_idx * (n_groups * bar_width + group_gap)
        for g_idx in range(n_groups):
            x = group_center + (g_idx - 1) * bar_width
            v = vals_by_scenario[s_idx][g_idx]
            e = errs_by_scenario[s_idx][g_idx]
            ax.bar(x, v, width=bar_width, yerr=e, capsize=3,
                   color=colors[g_idx], edgecolor="white")
            ax.text(x, 10, f"${v:,.0f}",
                    ha="center", va="bottom", fontsize=12, fontweight="bold")

    # Scenario labels on x-axis
    scenario_centers = [s * (n_groups * bar_width + group_gap)
                        for s in range(n_scenarios)]
    ax.set_xticks(scenario_centers)
    ax.set_xticklabels(scenarios)

    # Dashed horizontal reference line at FCM degradation level
    fcm_val = bottom_vals[0]
    ax.axhline(y=fcm_val, color=FCM_COLOR, linestyle="--", linewidth=1, zorder=0)

    # AAVE liquidated "+$X from recovery" arrow annotation
    aave_liq_bottom = bottom_vals[2]
    aave_liq_recov = recovery_vals[2]
    delta = aave_liq_recov - aave_liq_bottom
    liq_bottom_x = scenario_centers[0] + bar_width
    liq_recov_x = scenario_centers[1] + bar_width
    mid_x = (liq_bottom_x + liq_recov_x) / 2
    mid_y = (aave_liq_bottom + aave_liq_recov) / 2
    # ax.annotate(f"+${delta:,.0f} from recovery",
    #             xy=(liq_recov_x, aave_liq_recov * 0.85),
    #             xytext=(mid_x, mid_y),
    #             fontsize=9, color=AAVE_DARK_COLOR, fontweight="bold",
    #             ha="center",
    #             arrowprops=dict(arrowstyle="->", color=AAVE_DARK_COLOR, lw=1.2))

    ax.set_ylabel("Average Position Degradation [$/agent]")
    ax.set_title("Permanent Position Loss", fontsize=12, pad=18)
    ax.text(0.5, 1.02,
            "FCM cost is fixed; AAVE liquidation losses grow as collateral value recovers",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color="0.4")

    legend_handles = [Patch(facecolor=c, edgecolor="white", label=g.replace("\n", " "))
                      for g, c in zip(groups, colors)]
    ax.legend(handles=legend_handles, fontsize=8, loc="upper left")

    # Footnote
    ax.text(0.99, -0.10,
            "Gas costs not modeled.",
            transform=ax.transAxes, ha="right", va="top", fontsize=7, color="0.5")

    ax.tick_params(axis="x", length=0, pad=6)
    ax.set_ylim(bottom=0)

    fig.suptitle("FCM vs AAVE: Position Degradation During Synthetic Flash Crash",
                 fontsize=13, fontweight="bold", y=0.91)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


# ---------------------------------------------------------------------------
# Per-run lollipop charts
# ---------------------------------------------------------------------------

def plot_per_run_lollipops(run_df: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ht_runs = run_df[run_df["Strategy"] == "High_Tide"].copy()
    aave_runs = run_df[run_df["Strategy"] == "AAVE"].copy()

    ht_runs["run_label"] = ht_runs["Scenario"].map(_run_label)
    aave_runs["run_label"] = aave_runs["Scenario"].map(_run_label)

    x = np.arange(len(ht_runs))
    offset = 0.12

    # --- Panel 1: Survival Rate per Run (FCM "no collat. liq." + AAVE) ---
    ax = axes[0]
    ht_collat = ht_runs["survival_rate_no_collat_liq"].values * 100
    aave_surv = aave_runs["survival_rate_rebal_suff"].values * 100

    ax.vlines(x - offset / 2, 0, ht_collat, color=FCM_COLOR, linewidth=1.5)
    ax.plot(x - offset / 2, ht_collat, "o", color=FCM_COLOR, markersize=7, label="FCM")
    ax.vlines(x + offset / 2, 0, aave_surv, color=AAVE_COLOR, linewidth=1.5)
    ax.plot(x + offset / 2, aave_surv, "D", color=AAVE_COLOR, markersize=6, label="AAVE")

    ax.set_xticks(x)
    ax.set_xticklabels(ht_runs["run_label"].values)
    ax.set_ylabel("Survival Rate (%)")
    ax.set_title("Survival Rate per Run")
    ax.set_ylim(0, 115)
    ax.legend(fontsize=7, loc="lower left")

    # --- Panel 2: Liquidated Collateral Value per Run (per agent) ---
    ax = axes[1]
    ht_liq = ht_runs["mean_liq_collat_all"].values
    aave_liq_all = aave_runs["mean_liq_collat_all"].values
    aave_liq_only = aave_runs["mean_liq_collat_liquidated"].values

    ax.vlines(x - offset, 0, ht_liq, color=FCM_COLOR, linewidth=1.5)
    ax.plot(x - offset, ht_liq, "o", color=FCM_COLOR, markersize=7, label="FCM")
    ax.vlines(x, 0, aave_liq_all, color=AAVE_COLOR, linewidth=1.5)
    ax.plot(x, aave_liq_all, "D", color=AAVE_COLOR, markersize=6, label="AAVE (all)")
    ax.vlines(x + offset, 0, aave_liq_only, color=AAVE_DARK_COLOR, linewidth=1.5)
    ax.plot(x + offset, aave_liq_only, "s", color=AAVE_DARK_COLOR, markersize=6, label="AAVE (liq. only)")

    ax.set_xticks(x)
    ax.set_xticklabels(ht_runs["run_label"].values)
    ax.set_ylabel("Average Liquidated Collateral ($/agent)")
    ax.set_title("Liquidated Collateral Value per Run")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=7, loc="upper left")

    # --- Panel 3: Recovery Degradation per Run (AAVE split) ---
    ax = axes[2]
    ht_recov = ht_runs["mean_recovery_degradation"].values
    aave_surv_recov = aave_runs["mean_recov_degrad_aave_surv"].values
    aave_liq_recov = aave_runs["mean_recov_degrad_aave_liq"].values

    ax.vlines(x - offset, 0, ht_recov, color=FCM_COLOR, linewidth=1.5)
    ax.plot(x - offset, ht_recov, "o", color=FCM_COLOR, markersize=7, label="FCM")
    ax.vlines(x, 0, aave_surv_recov, color=AAVE_COLOR, linewidth=1.5)
    ax.plot(x, aave_surv_recov, "D", color=AAVE_COLOR, markersize=6, label="AAVE (survived)")
    ax.vlines(x + offset, 0, aave_liq_recov, color=AAVE_DARK_COLOR, linewidth=1.5)
    ax.plot(x + offset, aave_liq_recov, "s", color=AAVE_DARK_COLOR, markersize=6, label="AAVE (liquidated)")

    ax.set_xticks(x)
    ax.set_xticklabels(ht_runs["run_label"].values)
    ax.set_ylabel("Average Recovery Degradation ($/agent)")
    ax.set_title("Position Degradation After Full Recovery")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=7, loc="upper left")

    for ax in axes:
        ax.tick_params(axis="x", length=0, pad=6)

    fig.suptitle("FCM vs AAVE: Per-Run Breakdown", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR,
                        help="Directory containing CSV + JSON results")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for charts (default: <results-dir>/charts)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir) if args.output_dir else results_dir / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    csv_df = load_csv(results_dir)
    json_df, btc_initial_price = load_json_survival_fields(results_dir)
    print(f"BTC initial price (from JSON): ${btc_initial_price:,.0f}")

    # Compute metrics
    agent_df = compute_metrics(csv_df, json_df, btc_initial_price)
    run_df = per_run_summary(agent_df)
    overview = overview_summary(run_df)

    # Consistency checks
    ht_overview = overview.loc[overview["Strategy"] == "High_Tide"].iloc[0]
    aave_overview = overview.loc[overview["Strategy"] == "AAVE"].iloc[0]
    print("\n--- Recovery degradation ---")
    print(f"HT recovery degradation: ${ht_overview['mean_recov_degrad']:,.0f}/agent  "
          f"(expected: same as bottom ≈ $387)")
    print(f"AAVE recovery degradation: ${aave_overview['mean_recov_degrad']:,.0f}/agent  "
          f"(expected: > bottom due to BTC recovery)")
    print(f"AAVE survived bottom: ${aave_overview['mean_pos_degrad_aave_surv']:,.0f}/agent")
    print(f"AAVE survived recovery: ${aave_overview['mean_recov_degrad_aave_surv']:,.0f}/agent")
    print(f"AAVE liquidated bottom: ${aave_overview['mean_pos_degrad_aave_liq']:,.0f}/agent")
    print(f"AAVE liquidated recovery: ${aave_overview['mean_recov_degrad_aave_liq']:,.0f}/agent")
    print(f"HT survival (rebal. suff.): {ht_overview['mean_surv_rebal']*100:.1f}%  "
          f"(expected: 100%)")
    print(f"HT survival (no collat. liq.): {ht_overview['mean_surv_no_liq']*100:.1f}%  "
          f"(expected: 100%)")
    print(f"AAVE survival: {aave_overview['mean_surv_rebal']*100:.1f}%  "
          f"(expected: 40–80%, mean ~56%)")
    print(f"HT liquidated collateral: ${ht_overview['mean_liq_all']:,.0f}/agent  "
          f"(expected: $0)")
    print(f"AAVE liquidated collateral (all agents): ${aave_overview['mean_liq_all']:,.0f}/agent  "
          f"(expected: ~$15k — $76k/run ÷ 5 agents)")
    print(f"AAVE liquidated collateral (liquidated only): ${aave_overview['mean_liq_liquidated']:,.0f}/agent  "
          f"(expected: ~$34k per liquidated agent)")
    print(f"HT position degradation: ${ht_overview['mean_pos_degrad']:,.0f}/agent  "
          f"(expected: $96–$620)")
    print(f"AAVE position degradation: ${aave_overview['mean_pos_degrad']:,.0f}/agent  "
          f"(expected: $96–$682)")

    # AAVE survival percentage for chart footnote
    aave_surv_pct = aave_overview["mean_surv_rebal"] * 100

    # Generate charts
    plot_overview_bars(overview, aave_surv_pct, output_dir / "overview_bars.png")
    plot_position_degradation(overview, aave_surv_pct, output_dir / "position_degradation.png")
    plot_per_run_lollipops(run_df, output_dir / "per_run_lollipops.png")


if __name__ == "__main__":
    main()
