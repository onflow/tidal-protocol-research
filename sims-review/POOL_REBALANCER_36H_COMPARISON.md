# Pool Rebalancer 36H Test: Arb-Delay OFF vs ON

> **Audit runs** (Feb 2026): two fresh runs executed during this audit, results in `results/Pool_Rebalancer_36H_Test_-_no-Arb-Delay/` and `results/Pool_Rebalancer_36H_Test_-_with-Arb-Delay/`.  
> **Prior work**: `reports/High_Tide_Capacity_Study_w_Arbing.md` (Sep 2025) presents findings from the same simulation under a different parameter set — see [§ Pre-existing report](#pre-existing-report-reportshigh_tide_capacity_study_w_arbingmd).

**Simulation**: `sim_tests/hourly_test_with_rebalancer.py`
**Scenario** (audit runs):
  - 120 agents,
  - BTC $100k→$50k (50% decline, 36h), 
  - Tri-HF profile: initial HF 1.1 (entry leverage) / rebalancing trigger 1.025 / target Health factor 1.04

## What the `arb delay` controls

The delay governs **pool rebalancer settlement only** — the ALM and Algo rebalancers arbitrage to correct MOET:YT price deviations by buying underpriced YT from the pool and selling it externally at the true price. The delay determines whether the acquired YT is sold back to MOET immediately or held pending (1h queue). See `pool_rebalancer.py` lines 435–455 (ALM) and 719–741 (Algo).

Agent rebalancing (YT→MOET sales to maintain health factor) is **completely independent** of this setting.

## Quantitative comparison (audit runs)

| Metric | No Arb Delay | With Arb Delay |
|---|---|---|
| Survival rate | 100% (120/120) | 100% (120/120) |
| Agent rebalances | 15,480 | 15,480 |
| Total slippage | $71.36 | $71.36 |
| Avg final HF | 1.035 | 1.035 |
| Total YT sold (agents) | $8,687,815 | $8,687,815 |
| Per-agent YT sold | $72,398.46 | $72,398.46 |
| ALM rebalances | 2 | 2 |
| Algo rebalances | 8 | 8 |
| Pool arb profit | $0.00 | $0.00 |
| Liquidations | 0 | 0 |

**All agent-level and trigger-level metrics are identical.**

## Only observable difference: ALM balance sheet

The delay changes how the ALM carries inventory between trades:

| ALM State | No Arb Delay | With Arb Delay |
|---|---|---|
| After 12h ALM event | MOET $500,004 / YT $0 | MOET $487,341 / YT $12,662 |
| After 24h ALM event | MOET $500,714 / YT $0 | MOET $205,709 / YT $307,585 |

Without delay, YT is immediately sold externally at true price → ALM stays MOET-denominated.
With delay, YT accumulates on balance sheet → by hour 24, ~60% of ALM capital is in pending YT.

Visible in: `charts/pool_balance_evolution_analysis.png` (both variants).

## Modeling note: negligible yield token price fluctuations

The delay queues pending YT sales as `(available_time, yt_amount, true_price)` and settles at the **acquisition-time true price**, not the true price at settlement (`pool_rebalancer.py` lines 118–128, 161). This makes the delay a pure capital lockup with no price risk. The assumption is harmless here — true YT price changes ~0.001 bps/hour — but means the delay does not model real execution/market risk.

## Core observation

The arb delay toggle has **no impact on simulation outcomes** in this scenario. It only changes intermediate ALM inventory composition. Both runs produce identical agent behavior, identical pool deviation patterns, and zero arbitrage profit.

## Observed inconsistencies warranting further investigation

AI-identified, pending expert confirmation

### F1: Algo rebalancer — $0 profit and $0 balance change on $3.6M cumulative volume

All 8 Algo rebalancer events show zero MOET balance change, zero YT balance change, and zero profit — despite trading $400k–$500k per event (~$3.6M cumulative). The ALM rebalancer shows small but real balance movements ($4, $714 MOET gains; YT accumulation with delay enabled). The Algo shows literally nothing.

Either the Algo adjusts pool price without committing its own capital (making it a price oracle, not an arbitrageur), or its settlement/PnL logic is broken. Both runs exhibit the same pattern.

**Evidence**: compare Algo events (e.g. Event 1 at Hour 7.8: Amount Traded $500,000, MOET change $0, YT change $0) with ALM Event 3 at Hour 12.0 (Amount Traded $12,659, MOET change −$12,659, YT change +12,662) in either log file.

**Code to investigate**: `pool_rebalancer.py` `AlgoRebalancer.execute_rebalance()` (line ~660), specifically the balance update path and how it differs from `ALMRebalancer.execute_rebalance()` (line ~353).

### F2: Off-by-one — 3rd ALM trigger at hour 36 never fires

The simulation loop runs `range(2160)` (minutes 0–2159). The ALM rebalancer is scheduled at 720-minute intervals, so triggers are expected at minutes 720 (12h), 1440 (24h), and 2160 (36h). Since minute 2160 is excluded by `range()`, only 2 of 3 expected ALM events fire.

**Evidence**: both audit runs show exactly 2 ALM events (at 12h and 24h). The config (`alm_rebalance_interval_minutes = 720`) and print banner ("expect 3 triggers: 12h, 24h, 36h") explicitly anticipate 3.

**Code**: `hourly_test_with_rebalancer.py` line 328: `for minute in range(self.config.simulation_duration_minutes)`.

## Audit run files

| Variant | Date | Log | Results |
|---|---|---|---|
| No delay | 2026-02-24 | `results/Pool_Rebalancer_36H_Test_-_no-Arb-Delay_20260224_143644.log` | `results/Pool_Rebalancer_36H_Test_-_no-Arb-Delay/` |
| With delay | 2026-02-20 | `results/Pool_Rebalancer_36H_Test_-_with-Arb-Delay_20260220_171904.log` | `results/Pool_Rebalancer_36H_Test_-_with-Arb-Delay/` |


---

## Pre-existing report: `reports/High_Tide_Capacity_Study_w_Arbing.md`

This report purports to document a run of the same simulation (with arb delay enabled). Its numbers **do not match** either of our runs:

| Metric | Report | Our `with-Arb-Delay` run |
|---|---|---|
| Initial HF | **1.25** | 1.1 (current code line 50) |
| Total rebalances | **12,240** | 15,480 |
| Avg slippage / rebalance | **$2.09** | $0.005 |
| Total slippage | **$25,586** | $71.36 |
| Avg final HF | **1.029** | 1.035 |
| Algo rebalances | **6** | 8 |
| Peak single trade | **$476,556** | $465,830 |

The root cause is the initial HF discrepancy: the report uses **1.25**, the current code uses **1.1** (`PoolRebalancer24HConfig.agent_initial_hf`, line 50). A higher initial HF means agents start with more collateral buffer, rebalancing less frequently but by larger amounts each time — consistent with the report's lower rebalance count and higher per-event slippage. The source run predates the current code and its result files have been overwritten. The report's chart references (`Pool_Rebalancer_36H_Test/charts/`) point to the old unversioned output directory.
