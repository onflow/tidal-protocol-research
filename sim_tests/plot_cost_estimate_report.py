#!/usr/bin/env python3
"""
FCM Cost Estimate — Rebalance Event Visualisation

Reads  fcm_rebalance_detail_report.csv  and the raw BTC price CSV, then
produces two figures:

Figure 1 — Main dashboard (2 panels)
  Top   : BTC price (2022 daily) with SR / ER markers
  Bottom: Health Factor at each event with band boundaries (1.1 / 1.5)

Figure 2 — Event analytics (2 × 2)
  TL: Monthly SR / ER event counts
  TR: Distribution of % price change from previous rebalance (SR vs ER)
  BL: Transition matrix — what rebalance type follows what
  BR: HF-before distribution (SR vs ER)
"""

import sys
import csv
from pathlib import Path
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")           # non-interactive backend for script use
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
REPORT_CSV = ROOT / "tidal_protocol_sim/results/FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3/fcm_rebalance_detail_report.csv"
HF_CSV     = ROOT / "tidal_protocol_sim/results/FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3/fcm_hf_history.csv"
BTC_CSV    = ROOT / "btc-usd-max.csv"
OUT_DIR    = ROOT / "tidal_protocol_sim/results/FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3"

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
C_SR   = "#e74c3c"   # red  — safety rebalance
C_ER   = "#27ae60"   # green — efficiency rebalance
C_BTC  = "#2c3e50"   # dark — BTC price line
C_HF   = "#2980b9"   # blue — HF line
C_BAND = "#ecf0f1"   # light grey — valid band fill


# ---------------------------------------------------------------------------
# Load rebalance event log
# ---------------------------------------------------------------------------
def load_events(path: Path) -> list[dict]:
    events = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            events.append({
                "event_id":   int(row["event_id"]),
                "type":       row["type"],
                "day":        int(row["day"]),
                "hour":       int(row["hour_of_day"]),
                "minute":     int(row["minute"]),
                "btc_price":  float(row["btc_price"]) if row["btc_price"] else None,
                "pct_chg":    float(row["pct_price_change_from_prev"]) if row["pct_price_change_from_prev"] else None,
                "prev_type":  row["prev_type"] if row["prev_type"] else None,
                "hf_before":  float(row["hf_before"]) if row["hf_before"] else None,
                "hf_after":   float(row["hf_after"])  if row["hf_after"]  else None,
            })
    return events


# ---------------------------------------------------------------------------
# Load 2022 daily BTC prices
# ---------------------------------------------------------------------------
def load_hf_history(path: Path) -> tuple[list[int], list[float], list[str]]:
    minutes, hfs, types = [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            minutes.append(int(row["minute"]))
            hfs.append(float(row["hf"]))
            types.append(row["event_type"])
    return minutes, hfs, types


def load_btc_2022(path: Path) -> tuple[list[date], list[float]]:
    dates, prices = [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if "2022-" in row.get("snapped_at", ""):
                day_str = row["snapped_at"].split(" ")[0]
                d = date.fromisoformat(day_str)
                dates.append(d)
                prices.append(float(row["price"]))
    return dates, prices


# ---------------------------------------------------------------------------
# Helper: event date from day-of-year (day 1 = Jan 1 2022)
# ---------------------------------------------------------------------------
JAN1 = date(2022, 1, 1)

def day_to_date(day: int) -> date:
    return JAN1 + timedelta(days=day - 1)


# ===========================================================================
# FIGURE 1 — Main dashboard
# ===========================================================================
def plot_figure1(events, btc_dates, btc_prices, hf_minutes, hf_values, hf_types, out_dir: Path):
    sr = [e for e in events if e["type"] == "SR"]
    er = [e for e in events if e["type"] == "ER"]

    fig, (ax_btc, ax_hf) = plt.subplots(
        2, 1, figsize=(14, 8), sharex=False,
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.35},
    )

    # ------------------------------------------------------------------
    # Top panel — BTC price + event markers
    # ------------------------------------------------------------------
    ax_btc.plot(btc_dates, btc_prices, color=C_BTC, linewidth=1.2,
                label="BTC price (daily)")

    # Project event minute → calendar date for plotting
    er_dates  = [day_to_date(e["day"]) for e in er]
    er_prices = [e["btc_price"] for e in er if e["btc_price"]]
    sr_dates  = [day_to_date(e["day"]) for e in sr]
    sr_prices = [e["btc_price"] for e in sr if e["btc_price"]]

    ax_btc.scatter(er_dates, er_prices, color=C_ER, marker="^", s=28, zorder=3,
                   label=f"ER — efficiency rebalance ({len(er)})")
    ax_btc.scatter(sr_dates, sr_prices, color=C_SR, marker="v", s=40, zorder=4,
                   label=f"SR — safety rebalance ({len(sr)})")

    ax_btc.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax_btc.set_ylabel("BTC / USD")
    ax_btc.set_title("2022 BTC Price — FCM Rebalancing Events", fontsize=13, fontweight="bold")
    ax_btc.legend(fontsize=9, loc="upper right")
    ax_btc.grid(axis="y", linestyle="--", alpha=0.4)

    # Month tick labels
    import matplotlib.dates as mdates
    ax_btc.xaxis.set_major_locator(mdates.MonthLocator())
    ax_btc.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # ------------------------------------------------------------------
    # Bottom panel — Health Factor at every hourly health check
    # ------------------------------------------------------------------
    # Separate HC points from SR/ER trigger+after points
    hc_min  = [m for m, t in zip(hf_minutes, hf_types) if t == "HC"]
    hc_hf   = [h for h, t in zip(hf_values,  hf_types) if t == "HC"]
    sr_min  = [m for m, t in zip(hf_minutes, hf_types) if t == "SR"]
    sr_hf   = [h for h, t in zip(hf_values,  hf_types) if t == "SR"]
    er_min  = [m for m, t in zip(hf_minutes, hf_types) if t == "ER"]
    er_hf   = [h for h, t in zip(hf_values,  hf_types) if t == "ER"]
    sr_after_min = [m for m, t in zip(hf_minutes, hf_types) if t == "SR_after"]
    sr_after_hf  = [h for h, t in zip(hf_values,  hf_types) if t == "SR_after"]
    er_after_min = [m for m, t in zip(hf_minutes, hf_types) if t == "ER_after"]
    er_after_hf  = [h for h, t in zip(hf_values,  hf_types) if t == "ER_after"]

    # Valid band + threshold lines
    ax_hf.axhspan(1.1, 1.5, color=C_BAND, alpha=0.6, label="Valid band (1.1 – 1.5)")
    ax_hf.axhline(1.3, color="#7f8c8d", linewidth=0.9, linestyle=":", alpha=0.8, label="Target HF (1.3)")
    ax_hf.axhline(1.1, color=C_SR, linewidth=0.9, linestyle="--", alpha=0.7, label="SR threshold (1.1)")
    ax_hf.axhline(1.5, color=C_ER, linewidth=0.9, linestyle="--", alpha=0.7, label="ER threshold (1.5)")
    ax_hf.axhline(1.0, color="black", linewidth=1.0, linestyle="-",  alpha=0.5, label="Liquidation (1.0)")

    # Continuous HF line through all HC points
    ax_hf.plot(hc_min, hc_hf, color=C_HF, linewidth=0.8, alpha=0.7, zorder=1, label="HF (no action)")

    # Draw vertical drop/rise lines at each rebalance: trigger → after
    # Arrows from threshold → target (arrowhead at target end)
    arrow_props_sr = dict(arrowstyle="-|>", color=C_SR, lw=1.8, mutation_scale=12)
    arrow_props_er = dict(arrowstyle="-|>", color=C_ER, lw=1.8, mutation_scale=12)
    for m_trig, hf_trig, hf_aft in zip(sr_min, sr_hf, sr_after_hf):
        ax_hf.annotate("", xy=(m_trig, hf_aft), xytext=(m_trig, hf_trig),
                       arrowprops=arrow_props_sr, zorder=3)
    for m_trig, hf_trig, hf_aft in zip(er_min, er_hf, er_after_hf):
        ax_hf.annotate("", xy=(m_trig, hf_aft), xytext=(m_trig, hf_trig),
                       arrowprops=arrow_props_er, zorder=3)

    # Trigger dots (SR / ER at threshold)
    ax_hf.scatter(sr_min, sr_hf, color=C_SR, marker="o", s=40, zorder=4, label=f"SR trigger ({len(sr_min)})")
    ax_hf.scatter(er_min, er_hf, color=C_ER, marker="o", s=40, zorder=4, label=f"ER trigger ({len(er_min)})")
    # After-rebalance dots (at target)
    ax_hf.scatter(sr_min, sr_after_hf, color=C_SR, marker="o", s=40, zorder=4, edgecolors="white", linewidths=0.8)
    ax_hf.scatter(er_min, er_after_hf, color=C_ER, marker="o", s=40, zorder=4, edgecolors="white", linewidths=0.8)

    # x-axis: convert minutes to month labels
    month_minutes = [0, 31*1440, 59*1440, 90*1440, 120*1440,
                     151*1440, 181*1440, 212*1440, 243*1440,
                     273*1440, 304*1440, 334*1440, 365*1440]
    month_labels  = ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec",""]
    ax_hf.set_xticks(month_minutes)
    ax_hf.set_xticklabels(month_labels)
    ax_hf.set_xlim(0, 365 * 1440)

    ax_hf.set_ylabel("Health Factor")
    ax_hf.set_title("Health Factor — Every Hourly Check (SR/ER show trigger → restored HF)", fontsize=11)
    ax_hf.legend(fontsize=8, loc="upper right", ncol=3)
    ax_hf.set_ylim(0.95, 1.65)
    ax_hf.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    out = out_dir / "fig1_rebalance_dashboard.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ===========================================================================
# FIGURE 2 — Event analytics
# ===========================================================================
def plot_figure2(events, out_dir: Path):
    import matplotlib.gridspec as gridspec

    sr = [e for e in events if e["type"] == "SR"]
    er = [e for e in events if e["type"] == "ER"]

    fig = plt.figure(figsize=(13, 9))
    fig.suptitle("FCM 2022 — Rebalance Event Analytics", fontsize=14, fontweight="bold", y=1.01)

    outer = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
    ax_tl = fig.add_subplot(outer[0, 0])
    ax_tr = fig.add_subplot(outer[0, 1])
    ax_bl = fig.add_subplot(outer[1, 0])
    # BR: broken y-axis — top sub-ax for ER (near 1.5), bottom for SR (near 1.1)
    inner_br = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[1, 1], hspace=0.08)
    ax_br_top = fig.add_subplot(inner_br[0])
    ax_br_bot = fig.add_subplot(inner_br[1])

    # ------------------------------------------------------------------
    # TL — Monthly event counts (SR and ER stacked bars)
    # ------------------------------------------------------------------
    ax = ax_tl
    months = list(range(1, 13))
    sr_by_month = [sum(1 for e in sr if day_to_date(e["day"]).month == m) for m in months]
    er_by_month = [sum(1 for e in er if day_to_date(e["day"]).month == m) for m in months]

    x = np.arange(12)
    ax.bar(x, er_by_month, color=C_ER, label="ER", alpha=0.85)
    ax.bar(x, sr_by_month, bottom=er_by_month, color=C_SR, label="SR", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                         "Jul","Aug","Sep","Oct","Nov","Dec"], fontsize=8)
    ax.set_ylabel("Event count")
    ax.set_title("Monthly Rebalance Counts (SR + ER)")
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Annotate totals
    for i, (e_cnt, s_cnt) in enumerate(zip(er_by_month, sr_by_month)):
        total = e_cnt + s_cnt
        if total:
            ax.text(i, total + 0.5, str(total), ha="center", va="bottom", fontsize=7)

    # ------------------------------------------------------------------
    # TR — % price change from previous rebalance (SR vs ER)
    # ------------------------------------------------------------------
    ax = ax_tr
    sr_chg = [e["pct_chg"] for e in sr if e["pct_chg"] is not None]
    er_chg = [e["pct_chg"] for e in er if e["pct_chg"] is not None]

    bins = np.linspace(-15, 15, 40)
    ax.hist(er_chg, bins=bins, color=C_ER, alpha=0.7, label=f"ER (n={len(er_chg)})")
    ax.hist(sr_chg, bins=bins, color=C_SR, alpha=0.7, label=f"SR (n={len(sr_chg)})")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("% BTC price change from previous rebalance")
    ax.set_ylabel("Count")
    ax.set_title("Price Change Triggering Each Rebalance Type")
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Median annotations
    if er_chg:
        ax.axvline(np.median(er_chg), color=C_ER, linewidth=1.2, linestyle=":",
                   label=f"ER median {np.median(er_chg):+.2f}%")
    if sr_chg:
        ax.axvline(np.median(sr_chg), color=C_SR, linewidth=1.2, linestyle=":",
                   label=f"SR median {np.median(sr_chg):+.2f}%")
    ax.legend(fontsize=8)

    # ------------------------------------------------------------------
    # BL — Rebalance transitions as a bar chart
    # ------------------------------------------------------------------
    ax = ax_bl

    # Count the four transition types
    counts = {"ER→SR": 0, "ER→ER": 0, "SR→SR": 0, "SR→ER": 0}
    for e in events:
        if e["prev_type"]:
            key = f"{e['prev_type']}→{e['type']}"
            if key in counts:
                counts[key] += 1

    bar_colours = {
        "ER→SR": "#8e44ad",   # purple
        "ER→ER": "#27ae60",   # green
        "SR→SR": "#e74c3c",   # red
        "SR→ER": "#2980b9",   # blue
    }
    legend_labels = {
        "ER→SR": "ER→SR  Previously ER, followed by SR",
        "ER→ER": "ER→ER  Previously ER, followed by ER",
        "SR→SR": "SR→SR  Previously SR, followed by SR",
        "SR→ER": "SR→ER  Previously SR, followed by ER",
    }

    keys = list(counts.keys())
    vals = [counts[k] for k in keys]
    bars = ax.bar(keys, vals,
                  color=[bar_colours[k] for k in keys],
                  width=0.5, zorder=2)

    # Count labels on top of each bar
    for bar, v in zip(bars, vals):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05,
                    str(v), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylabel("Count")
    ax.set_title("Rebalance Transitions\n(what rebalance type follows what)")
    ax.set_ylim(0, max(vals) + 1.5)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(axis="x", labelsize=9)

    handles = [mpatches.Patch(color=bar_colours[k], label=legend_labels[k]) for k in keys]
    ax.legend(handles=handles, fontsize=7.5, loc="upper left",
              framealpha=0.9, handlelength=1.2, handleheight=1.4)

    # ------------------------------------------------------------------
    # BR — HF-before box plot by event type (broken y-axis)
    #   ax_br_top : ER distribution — tight window around 1.5
    #   ax_br_bot : SR distribution — tight window around 1.1
    # ------------------------------------------------------------------
    hf_sr = [e["hf_before"] for e in sr if e["hf_before"] is not None]
    hf_er = [e["hf_before"] for e in er if e["hf_before"] is not None]

    pad = 0.003   # y-axis padding around the data

    for ax, data, colour, threshold, label, ylim_fn in [
        (ax_br_top, hf_er, C_ER, 1.5, "ER", lambda d: (min(d) - pad, threshold + pad)),
        (ax_br_bot, hf_sr, C_SR, 1.1, "SR", lambda d: (threshold - pad, max(d) + pad)),
    ]:
        if not data:
            continue
        bp = ax.boxplot([data], tick_labels=[label],
                        patch_artist=True, widths=0.4,
                        medianprops={"color": "white", "linewidth": 2})
        bp["boxes"][0].set_facecolor(colour)
        ax.axhline(threshold, color=colour, linewidth=0.9, linestyle="--", alpha=0.7,
                   label=f"Threshold ({threshold})")
        ax.set_ylim(*ylim_fn(data))
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        med = np.median(data)
        ax.text(1.28, med, f"median {med:.4f}", fontsize=8, color=colour, va="center")

        # 90th pct closest to threshold (high tail for ER, low tail for SR)
        pct_val = np.percentile(data, 90 if label == "ER" else 10)
        ax.axhline(pct_val, color=colour, linewidth=1.2, linestyle=":", alpha=0.9)
        offset = +pad * 0.5 if label == "ER" else -pad * 0.5
        ax.text(1.28, pct_val + offset,
                f"{'90' if label == 'ER' else '10'}th pct {pct_val:.4f}",
                fontsize=7.5, color=colour, va="center")

        ax.legend(fontsize=8, loc="upper right")

    # Shared y-label — place on the bottom sub-axis
    ax_br_bot.set_ylabel("Health Factor before rebalance")

    # Shared title — place on the top sub-axis
    ax_br_top.set_title("HF Distribution at Trigger\n(before rebalance executes)", fontsize=10)

    # Remove the bottom spine of top sub-axis and top spine of bottom sub-axis
    ax_br_top.spines["bottom"].set_visible(False)
    ax_br_bot.spines["top"].set_visible(False)
    ax_br_top.tick_params(axis="x", bottom=False, labelbottom=False)

    # Diagonal break marks
    d = 0.018
    kw = dict(color="k", clip_on=False, linewidth=0.9, transform=ax_br_top.transAxes)
    ax_br_top.plot((-d, +d), (-d, +d), **kw)
    ax_br_top.plot((1 - d, 1 + d), (-d, +d), **kw)
    kw["transform"] = ax_br_bot.transAxes
    ax_br_bot.plot((-d, +d), (1 - d, 1 + d), **kw)
    ax_br_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kw)

    fig.tight_layout()
    out = out_dir / "fig2_event_analytics.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ===========================================================================
# Entry point
# ===========================================================================
def main():
    print("Loading data...")
    events = load_events(REPORT_CSV)
    btc_dates, btc_prices = load_btc_2022(BTC_CSV)
    hf_minutes, hf_values, hf_types = load_hf_history(HF_CSV)

    print(f"  {len(events)} rebalance events loaded")
    print(f"  {len(btc_dates)} daily BTC prices loaded (2022)")
    print(f"  {len(hf_minutes)} HF history points loaded")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating Figure 1 — Main dashboard...")
    plot_figure1(events, btc_dates, btc_prices, hf_minutes, hf_values, hf_types, OUT_DIR)

    print("Generating Figure 2 — Event analytics...")
    plot_figure2(events, OUT_DIR)

    print("Done.")


if __name__ == "__main__":
    main()
