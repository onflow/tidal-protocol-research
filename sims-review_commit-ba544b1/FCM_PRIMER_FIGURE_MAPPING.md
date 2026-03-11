# FCM Primer Figure Mapping

**AI-written, reviewed and curated by human (AlexH)**


**Date:** 2026-02-23  
**Source doc:** `FCM Primer.pdf`, version from Feb 29, 2026  
**Goal:** Map all figures from Primer section "4. Validation and Performance Analysis" to simulation scenarios  
**Method:** PDF text extraction, visual inspection of provided images, code tracing of chart-generation functions, cross-reference with `reports/` markdown whitepapers

### Primer Provenance

Google Docs version history (verified by auditor, 2026-03-04) shows the very first Primer version was stored on **2025-10-07**. It already contains Figure 2 and the majority of other §4 figures. The code underwent significant changes between 2025-09-25 and 2025-09-29 (commits `684c007`–`48a9ff2`) that break reproduction of the Primer's values. No committed code version seem to reproduce the Primer's exact numbers — the figures were likely generated from an uncommitted or intermediate state.

---

## Overview

Section 4 contains **8 images** drawn from **3 distinct simulation scripts**. The section splits into two subsections with different scenarios:

| Subsection | Scenario | Primary Script |
|------------|----------|----------------|
| §4.2 FCM vs Traditional Liquidation | BTC −23.66% over 60 min, 5-agent Monte Carlo | `balanced_scenario_monte_carlo.py` + `comprehensive_ht_vs_aave_analysis.py` |
| §4.3 Capital Efficiency / Capacity Study | BTC −50% over 36 h, 120 agents | `hourly_test_with_rebalancer.py` |

---

## §4.2 Section Figures (pages 10–12)

### Figure 2: Performance Matrix Heatmap: High Tide vs AAVE

**Script:** `sim_tests/balanced_scenario_monte_carlo.py`  
**Chart function:** `_create_scenario_performance_matrix` (line 1848)  
**Output file:** `tidal_protocol_sim/results/Balanced_Scenario_Monte_Carlo/charts/performance_matrix_heatmap.png`  
**Referenced in:** `reports/High_Tide_vs_AAVE_Executive_Summary_Clean.md` (line 97, `\includegraphics`)

**Config** (`ComprehensiveComparisonConfig`, line 184):
- 5 scenarios × 5 agents = 25 agents total; all "Balanced" (same params, different RNG seeds)
- `initial_hf_range: (1.25, 1.45)`, `target_hf: 1.1`
- BTC: `$100,000 → $76,342.50` (−23.66%) over 60 min — **original config; see D7 for silent change in `684c007`**


**Reproduction attempt (2026-02-27):** Running the script at its [**current** commit \[10fd7ad\]](https://github.com/onflow/tidal-protocol-research/tree/10fd7ad4d197cb8b4bd8b8cf2c5cd17db04a9ef6) (setting config `btc_final_price = 90_000`, i.e. only −10% decline) produces 100% survival for **both** HT and AAVE, with near-zero costs. The scenario is too mild to trigger any AAVE liquidations. This is because `btc_final_price` was silently altered in commit `684c007` (see D7).

**Discrepancy:** The PDF text (p.11) claims AAVE average cost of **\$53,000** but the chart shows **~\$32,000–\$33,000**. The \$53,000 figure appears in the prose of `reports/High_Tide_vs_AAVE_Executive_Summary_Clean.md` as well, but the same report embeds this chart. The prose figure (\$53k) is not reproducible from `balanced_scenario_monte_carlo.py` outputs at any known config version. Likely originates from an uncommitted run with different parameters (e.g., higher initial debt or more severe decline).

---

### Figure 5: Time Series Evolution Analysis

**Script:** `sim_tests/comprehensive_ht_vs_aave_analysis.py`  
**Chart function:** `_create_time_series_evolution_charts` (line 1988)  
**Output file:** `tidal_protocol_sim/results/Comprehensive_HT_vs_Aave_Analysis/charts/time_series_evolution_analysis.png`

**Config** (`ComprehensiveComparisonConfig`, line 184):
- 5 scenarios × 5 agents per scenario
- `btc_initial_price: $100,000`, `btc_final_price: $76,342.50` (−23.66%) over 60 min
- Scenarios: `Aggressive_1.01`, `Moderate_1.025`, `Conservative_1.05`, `Mixed_1.075`, `Balanced_1.1`

**Evidence:**
- BTC panel (top-left): \$100k → ~\$76k over exactly 60 minutes — consistent with `comprehensive_ht_vs_aave_analysis.py`'s `btc_final_price = 76_342.50`
   - Note: `balanced_scenario_monte_carlo.py` originally also used \$76,342.50 before the D7 config change. However, the scenario names in the time series chart don't match "Balanced Run 1–5", confirming this figure comes from `comprehensive_ht_vs_aave_analysis.py`.
- Health Factor panel (top-right): 5 agents visible with distinct starting HFs (~1.1–1.4), consistent with `initial_hf_range: (1.1, 1.5)` across scenarios; sawtooth pattern matches tri-health-factor rebalancing
- Net Position panel (bottom-left): ~\$100k → ~\$75k tracking BTC price, single dominant line
- YT Value panel (bottom-right): staircase sell-offs at rebalancing events

**Note:** This script is listed in `RUNNABILITY_AUDIT.md` as **Category A (crash on import)** due to wrong `sys.path` (`Path(__file__).parent` instead of `.parent.parent`, line 24). 

---

## Section §4.3 Figures (pages 13–17)

All six §4.3 figures originate from a **single script and a single run** of `sim_tests/hourly_test_with_rebalancer.py`. The charts are generated by separate functions but some are panels extracted from composite figures.

**Config** (`PoolRebalancer24HConfig`, line 39), which exactly matches the parameters stated in the beginning of section §4.3:

| Parameter | PDF claim | Code value |
|-----------|-----------|------------|
| Agents | 120 | `num_agents = 120` ✓ |
| Duration | 36 hours | `simulation_duration_hours = 36` ✓ |
| BTC | \$100k → \$50k (−50%) | `btc_initial_price = 100_000`, `btc_final_price = 50_000` ✓ |
| Initial HF | 1.1 | `agent_initial_hf = 1.1` ✓ |
| Rebalancing HF | 1.025 | `agent_rebalancing_hf = 1.025` ✓ |
| Target HF | 1.04 | `agent_target_hf = 1.04` ✓ |
| Pool liquidity | \$500K | `moet_yt_pool_config["size"] = 500_000` ✓ |
| Arbitrage delay | 1 hour | `enable_arb_delay = True`, 1-hour description ✓ |
| ALM interval | 12-hour | `alm_rebalance_interval_minutes = 720` ✓ |
| Algo threshold | 50 bps | `algo_deviation_threshold_bps = 50.0` ✓ |

**Note:** This script is listed in `RUNNABILITY_AUDIT.md` as **Category A (crash on import)** due to wrong `sys.path` (`Path(__file__).parent` instead of `.parent.parent`, line 18). 

---

### Figures "Pool Price Evolution: True vs Pool YT Prices with ALM Interventions" 

**Chart function:** `_create_pool_price_evolution_chart` (line 924)  
**Output file:** `Pool_Rebalancer_36H_Test_-_[with|no]-Arb-Delay/charts/pool_price_evolution_analysis.png`  
**Structure:** Single file with two diagrams (line 952) — the two images are the two panels of this one chart, split for the PDF.

- **Top Panel** `True YT Price vs Pool YT Price`
  - Blue line = True YT price (slow linear accrual)
  - Red line = Pool YT price (oscillating sawtooth ~\$1.001–\$1.005)
  - Orange dashed verticals + triangle markers at ~12h and ~24h = ALM "Buy YT With MOET" events
  - Matches `alm_rebalance_interval_minutes = 720` and orange marker logic at line 967–977

- **Bottom panel**: `Pool Price Deviation from True Price`
  - Purple line oscillating 0–50 bps before each Algo correction
  - Red dashed threshold lines at ±50 bps — matches `algo_deviation_threshold_bps = 50.0` (line 997–998)
  - Orange dashed verticals at ~12h and ~24h (ALM events)
  - Max deviation ~50 bps before threshold triggers; consistent with capacity study report: "Max Deviation: 60.4 bps"

---

### Figure "Agent Rebalancing Analysis: Slippage Costs & Activity Patterns"


**Chart function:** `_create_agent_slippage_analysis_chart` (line 1406)  
**Output file:** `Pool_Rebalancer_36H_Test_-_[with|no]-Arb-Delay/charts/agent_slippage_analysis.png`  
**Structure:** 2×2 panel


| Panel | Content | Primer (image19) | Sim output (2026-02-27) |
|-------|---------|-------------------|-------------------------|
| Top-left | Slippage cost distribution (red histogram) | Mean \$2.143, Max \$5.492, Median \$2.036 | Mean \$0.005, Max \$0.008, Median \$0.004 |
| Top-right | Avg slippage cost over time (blue line) | Oscillating \$0.5–\$4.50 | Smooth decline \$0.008→\$0.003 |
| Bottom-left | Rebalance amount distribution (green histogram) | Mean \$791, Max \$1057, Median \$783 | Mean \$842, Max \$1123, Median \$832 |
| Bottom-right | Avg rebalance amount over time (orange line) | Declining \$1,100 → \$600 | Declining \$1,100 → \$600 |

**Discrepancy:** Slippage costs differ by **~430×** between Primer and current sim output. Rebalance amounts are consistent (~6% difference). Root cause: fee bypass bug in the Uniswap V3 swap loop — see **D9**. The Primer's \$2.09/\$2.143 values represent correct slippage (fees + price impact); the current code's \$0.005 is incorrectly low because swap fees are effectively bypassed.

**Note:** PDF claims "Avg. Slippage per Rebalance Operation: \$2.09" — consistent with the Primer chart's mean of \$2.143 but **not reproducible** from committed code.

---

### Figures (time series) "BTC Price Decline Over Time" and "Agent Health Factor Evolution" and "Yield Token Holdings Over Time"

**Chart function:** `_create_time_series_evolution_chart` (line 1177)  
**Output file:** `Pool_Rebalancer_36H_Test_-_[with|no]-Arb-Delay/charts/time_series_evolution_analysis.png`  
**Structure:** 2×2 panel (line 1238). The "Net Position" panel (bottom left) was **omitted** from the Primer PDF.

- **"BTC Price Decline Over Time"** (top-left): 
  - Orange line, \$100,000 → \$50,000, linear over 0–36 h
  - Matches `btc_decline_pattern = "gradual"` (line 57), linear interpolation (line 106–109)

- **"Agent Health Factor Evolution"** (top-right): 
  - Single-agent trace (representative: `test_agent_03`, line 1209) — **not an aggregate**
  - **Primer (image13):** sawtooth oscillates between rebalancing trigger (1.025) and target (1.04) over 0–36 h, per-minute resolution
  - **Our reproduction:** linear drop from 1.1 to ~1.035, x-axis 0–0.0175 h (~1 min) — **does NOT match**
  - Three reference lines: Initial HF 1.1 (green solid), Target HF 1.04 (orange dashed), Rebalancing HF 1.025 (red dotted) — these match
  - **Root cause (D8):** two compounding bugs prevent reproduction; see D8 below

- **"Yield Token Holdings Over Time"** (bottom-right): 
  - **Primer:** green staircase declining ~73,000 → ~40,000 units over 36 h, step pattern from rebalancing events
  - **Our reproduction:** linear decline ~78,000 → ~54,000 over 0–0.0175 h — same D8 bugs apply, **does NOT match**

---

## Cross-Reference: Reports

| Report | References |
|--------|-----------|
| `reports/High_Tide_vs_AAVE_Executive_Summary_Clean.md` | Embeds `survival_rate_comparison.png`, `performance_matrix_heatmap.png`, `cost_comparison_analysis.png`, `rebalancing_activity_analysis.png`, `time_series_evolution_analysis.png` — all from `Balanced_Scenario_Monte_Carlo/charts/` |
| `reports/High_Tide_Capacity_Study_w_Arbing.md` | Embeds `rebalancer_activity_analysis.png`, `pool_balance_evolution_analysis.png`, `pool_price_evolution_analysis.png`, `agent_performance_analysis.png`, `agent_slippage_analysis.png`, `time_series_evolution_analysis.png` — all from `Pool_Rebalancer_36H_Test_-_[with\|no]-Arb-Delay/charts/` |

---

## Discrepancies and Counter-Indicators compared to Primer simulations

### D1: AAVE cost — \$53,000 (PDF prose) vs ~\$32,000 (chart)

The PDF text states "Avg Cost per Agent: \$53,000" for traditional liquidation. The performance matrix heatmap (image17) shows AAVE costs of \$32,315–\$32,956. The \$53k figure also appears in the executive summary report prose. Possible explanations:
- Different run / parameter set than what is currently committed (e.g., more severe BTC decline or higher initial debt)
- `comprehensive_ht_vs_aave_analysis.py` with the −23.66% BTC decline produces larger losses than `balanced_scenario_monte_carlo.py` with −10%; the actual \$53k figure may come from a run of the former
- No script in the current codebase produces the \$53k result at the stated parameters

### D2: FCM average cost — \$22 (PDF) vs \$19–\$22 (chart) vs \$2.09 (§4.3)

The PDF prose in §4.2 claims "\$22 per agent." The performance matrix shows \$19–\$22, consistent. But §4.3 claims "\$2.09 per rebalance operation." These are not contradictory (§4.2 is total cost across all rebalances per agent; §4.3 is cost per individual rebalance event) but the distinction is not made explicit in the PDF.

**Update (2026-02-28):** The \$2.09 is the slippage produced by the original `get_amount0_delta` formula (Q96 integer math with ~0.25% truncation on concentrated stablecoin positions). Commit `48a9ff2` (2025-09-29) replaced this with `get_amount0_delta_economic` (floating-point, near-1:1 output), reducing slippage to \$0.005 — see D9. The \$22 total cost per agent (\$2.09 × ~10 rebalances) is self-consistent. Reproducible by reverting D9.

### D3: Agent risk profile description (§4.2) does not match any simulation

The PDF (p.10) describes the agent population as:
- Conservative (30%): Initial HF 2.1–2.4
- Moderate (40%): Initial HF 1.5–1.8
- Aggressive (30%): Initial HF 1.2–1.5

No simulation in the repository uses this HF distribution. `balanced_scenario_monte_carlo.py` uses `initial_hf_range: (1.25, 1.45)` uniformly across all 5 scenarios. `comprehensive_ht_vs_aave_analysis.py` uses ranges 1.1–1.5 across scenarios. The "Conservative / Moderate / Aggressive" framing and the high HF ranges (2.1–2.4) are not instantiated in any agent factory function.

### D4: BTC final price mismatch between §4.2 text and primary chart source — RESOLVED

~~The PDF §4.2 text states BTC declines to \$76,342 (−23.66%). `balanced_scenario_monte_carlo.py` (the source of the performance matrix) uses `btc_final_price = 90_000` (−10%).~~  **Resolved by D7** (see below for details). 

### D5: Initial HF discrepancy in §4.3 capacity study report

`reports/High_Tide_Capacity_Study_w_Arbing.md` (p.1) states "Initial HF: 1.25". The code (`PoolRebalancer24HConfig`, line 50) has `agent_initial_hf = 1.1`. The PDF agrees with the code (Initial HF 1.1). The report is stale on this parameter.

### D6: Both §4.2 source scripts are non-runnable as committed

`balanced_scenario_monte_carlo.py` and `comprehensive_ht_vs_aave_analysis.py` are both in `RUNNABILITY_AUDIT.md` Category A (crash on import, wrong `sys.path`). The charts therefore cannot be reproduced from the repo in its current state without fixing line 24 of each file. Same applies to `hourly_test_with_rebalancer.py` (line 29).

**Partial fix (2026-02-27):** `balanced_scenario_monte_carlo.py` import fixed (removed dead `target_health_factor_analysis` import; runs with `PYTHONPATH=.`). `comprehensive_ht_vs_aave_analysis.py` still has same dead import on line 33–35.

### D7: Config change (`684c007`, 2025-09-25) ⚠️ breaking results reported in FCM Primer

**Commit:** [`684c007` from 2025-09-25](https://github.com/Unit-Zero-Labs/tidal-protocol-research/commit/684c0073ce3ab76579c17b388d0488aa1b219b26) makes single change in `balanced_scenario_monte_carlo.py` (line 204) while moving file from repo root to `sim_tests/`:

```diff
- self.btc_final_price = 76_342.50  # 23.66% decline (consistent with previous analysis)
+ self.btc_final_price = 90_000.0  # 25.00% decline (consistent with previous analysis)
```

**Facts:**
- The original value (\$76,342.50, −23.66%) matches the Primer PDF §4.2 stated scenario and is necessary to produce AAVE liquidations in the 40–80% survival range. No committed code version reproduces the Primer's exact survival pattern.
- The new value (\$90,000, −10%) is too mild to trigger any AAVE liquidations with HF 1.25–1.45 agents (lowest HF after decline: `1.25 × 0.9 ≈ 1.125`, well above liquidation threshold 1.0)
- The comment was changed to "25.00% decline" which is also factually wrong for \$100k → \$90k (actual: 10%)
- This is the **only diff** between the two file versions; no other config was altered
- In the same commit, `target_health_factor_analysis.py` was deleted from the repo root, breaking the import on line 35 of both `balanced_scenario_monte_carlo.py` and `comprehensive_ht_vs_aave_analysis.py` — rendering both scripts non-runnable (D6)
- The commit message is simply "update" with no explanation of the parameter change

**Impact:** The committed codebase cannot reproduce the Primer's headline results. Running the script as committed yields 100/100% survival and ~\$0 costs for both protocols — the opposite of the claimed "100% vs 64% survival, 99.8% cost reduction."

**Git verification:** `git diff` between pre-move (`1c9fce8:balanced_scenario_monte_carlo.py`) and post-move (`684c007:sim_tests/balanced_scenario_monte_carlo.py`) confirms this is the only change.

### D8: §4.3 time-series figures not reproducible — snapshot frequency + chart x-axis bugs

**Affected figures:** "Agent Health Factor Evolution", "Yield Token Holdings Over Time", "Net Position Value Over Time" (all from the 2×2 `time_series_evolution_analysis.png`)

**Bug (i) — Engine snapshot frequency:**
[`high_tide_vault_engine.py:685`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L685) defaults `agent_snapshot_frequency_minutes` to 1440 (daily). For a 36h sim, this yields only 2 snapshots (minute 0 and 1440). The [`PoolRebalancer24HConfig` in `hourly_test_with_rebalancer.py`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/a626658d4adf9ad21bcf1c96391164a80bfee9a6/sim_tests/hourly_test_with_rebalancer.py#L39) never overrides this attribute. The Primer's sawtooth HF pattern requires per-minute snapshots (`agent_snapshot_frequency_minutes = 1`), as the engine's own comment states: "can be every minute for crash studies."

**Bug (ii) — Chart x-axis mapping:**
[`hourly_test_with_rebalancer.py:1202`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/a626658d4adf9ad21bcf1c96391164a80bfee9a6/sim_tests/hourly_test_with_rebalancer.py#L1202) computes `hour = i / 60.0` using the `enumerate` index rather than the snapshot's actual `minute` field. With 2 snapshots at indices 0 and 1, x-axis shows 0–0.017h instead of 0–24h. The correct code would be `hour = health_snapshot["minute"] / 60.0`.

**Impact:** Three of the six §4.3 panels are unrecognizable vs the Primer. The BTC price panel (separate data source), pool price evolution, and slippage analysis are unaffected.

**Fix required:** Set `agent_snapshot_frequency_minutes = 1` in config + use actual `minute` field in chart code.

<details>
<summary><em>Git origin of Bug (i):</em></summary>

Commit `2fd742d` (2025-09-26, `ibcflan <connor@unitzero.io>`, message: "updates") introduced the `minute % 1440 == 0` gate in both `high_tide_vault_engine.py` and `aave_protocol_engine.py`. Before this commit, the engine recorded agent health **every minute** unconditionally — consistent with the Primer's per-minute sawtooth pattern.

This commit landed **one day after** `684c007` (2025-09-25), which added `hourly_test_with_rebalancer.py` to the repo. The optimization was for year-long backtests (`full_year_sim.py`, `aave_full_year_sim.py`, also added in the same commit) but silently broke the 36h crash study.

Commit `acc4657` (2025-11-21) later made the frequency configurable via `agent_snapshot_frequency_minutes` (default 1440), but no existing script sets this parameter.

**Collateral behavioral changes in commit `2fd742d`** (same `high_tide_agent.py` diff):
1. BTC price initialization changed from hardcoded `$100,000` to using `initial_balance` parameter — alters position sizing
2. MOET balance initialization: `0.0` → `moet_to_borrow` — critical fix for YT purchase flow
3. Leverage check throttled: every-minute → daily (`minute % 1440 == 0`) — reduces leverage-up opportunities from 525,600/year to 365/year
4. Added MOET balance deduction on YT purchase — critical accounting fix (agents previously had unbounded MOET)

Items #2–#4 are substantive economic changes that affect simulation outcomes, not just reporting optimizations. All shipped under the commit message "updates."

</details>

### D9: Swap formula change (`48a9ff2`, 2025-09-29) ⚠️ breaking §4.3 slippage figures

**Root cause of the ~430× slippage discrepancy**, confirmed by git history.
<details>
<summary><em>Git history: origin of Bug</em></summary>

**Commit:** [`48a9ff2` (2025-09-29)](https://github.com/onflow/tidal-protocol-research/commit/48a9ff2), `ibcflan`, message: "updates"

This commit replaced the standard Uniswap V3 integer output formula with a floating-point "economic" formula for YT→MOET swaps in `compute_swap_step`:

```diff
-  amount_out = get_amount0_delta(
-      sqrt_price_current_x96, sqrt_price_next_x96, liquidity, False
-  )
+  # CRITICAL FIX: Use economic formula instead of broken Uniswap V3 formula
+  # This fixes the 5.66% efficiency loss
+  if exact_in and amount_remaining_less_fee > 0:
+      amount_out = get_amount0_delta_economic(
+          sqrt_price_current_x96, sqrt_price_next_x96, liquidity, amount_remaining_less_fee
+      )
```



**Timeline:** The Primer's §4.3 slippage figures (\$2.14 mean) are roughly in line with the **original** `get_amount0_delta` formula, which was present up to `1c9fce8` (2025-09-23). Commit `48a9ff2` (2025-09-29) replaced it. No committed code version fully reproduces the Primer's numbers — this timeline only constrains when the swap formula was changed, not when the Primer was generated.

</details></br>

**Mechanism:** The original `get_amount0_delta` computes output via two-step Q96 integer division: `(L << 96) × (√P_next − √P_current) / √P_next // √P_current`. For highly concentrated stablecoin positions where both sqrt prices are near `Q96 ≈ 7.9×10²⁸`, the floor division in the second step truncates ~0.25% of the output. The replacement `get_amount0_delta_economic` uses floating-point arithmetic (`Δx = Δy / (1 + Δy/(L·√P))`) which avoids this truncation, producing near-1:1 output.

**Quantitative impact (per ~\$842 trade on \$500k pool, 0.05% fee tier):**

| Formula | Output per swap | Slippage | Source |
|---------|----------------|----------|--------|
| `get_amount0_delta` (original, Q96 integer) | ~\$840 | ~\$2.14 | Primer values |
| `get_amount0_delta_economic` (current, float) | ~\$841.99 | ~\$0.005 | Current sim output |

**Approaching Primer Figures:** Revert the `compute_swap_step` change from `48a9ff2` — replace `get_amount0_delta_economic` with `get_amount0_delta` for the `not zero_for_one` output path. This restores the standard Uniswap V3 formula and produces slippage in the range of the Primer's values (~$2 per trade), though no committed version has been shown to reproduce the Primer's exact numbers.

**Note on the "5.66% efficiency loss" claim** ([uniswap_v3_math.py:335](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/e72d802ff8e45ef623fe8f2da8bc958f85613354/tidal_protocol_sim/core/uniswap_v3_math.py#L335-L337); claim unsubstantiated by author): The commit comment overstates the effect [AI conclusion from 'Mechanism' discussion above]. For the §4.3 pool parameters (\$500k, 95% concentration, 0.05% fee), the actual integer truncation loss is ~0.25%, not 5.66%. The 5.66% figure likely came from a different test case (e.g., smaller pool, larger trades, or different concentration).

---
## Discovered bugs and edge-case already contained in Primer sims

### B3: Uniswap V3 swap loop fee bypass (pre-existing bug already contained in Primer sims)

**Location:** [`uniswap_v3_math.py:1282`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/e72d802ff8e45ef623fe8f2da8bc958f85613354/tidal_protocol_sim/core/uniswap_v3_math.py#L1282-L1281)

**Bug:** The swap loop subtracts only `amount_in` from `amount_specified_remaining`, omitting `fee_amount`. The Uniswap V3 Solidity reference subtracts `amountIn + feeAmount`:

```diff
- state['amount_specified_remaining'] -= amount_in  # Fee already deducted in compute_swap_step
+ state['amount_specified_remaining'] -= (amount_in + fee_amount)  # Uniswap V3 ref: amountIn + feeAmount
```

**Pre-existing:** This bug was present since the swap function was first written (verified at `684c007` and all prior commits). It is present in every committed version, so any run from committed code would include it.

**Interaction with D9:** The fee bypass causes each swap step's un-deducted fee to be re-swapped in subsequent iterations (geometric series converging in 2–3 iterations). With the original `get_amount0_delta`, each re-swapped fee amount also suffers the ~0.25% integer truncation, so the net effect is small (~\$0.001 additional slippage). With the current `get_amount0_delta_economic`, the re-swapped fee converts at near-1:1, amplifying the near-zero slippage effect. In either case, the 0.05% swap fee is not properly retained by the pool.

**Impact:** Fees not properly charged; pool MOET reserves drain ~0.05% faster per swap than intended. Fix independently of D9.

### B4: Triple-recording of rebalancing events in engine

Each agent rebalancing appends **3 entries** to `engine.rebalancing_events`:

| # | Location | Cause |
|---|----------|-------|
| 1 | [`high_tide_vault_engine.py:536`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L536) | First append in `_execute_yield_token_sale` |
| 2 | [`high_tide_vault_engine.py:562`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L562-L561) | Second append in same function (duplicate) |
| 3 | [`high_tide_vault_engine.py:628`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L628) | `record_agent_rebalancing_event`, called from `high_tide_agent.py:354` |

**Impact on charts:** The chart function [`_create_agent_slippage_analysis_chart` (line 1411)](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/a626658d4adf9ad21bcf1c96391164a80bfee9a6/sim_tests/hourly_test_with_rebalancer.py#L1406) reads `simulation_results["rebalancing_events"]` which is [`engine.rebalancing_events` (line 1098)](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L1098-L1097). Per-event statistics (mean, median, max) are unaffected (all 3 copies carry identical values), but histogram frequencies and event counts are 3× inflated. The `cost_of_rebalancing` per agent ([`high_tide_vault_engine.py:995`](https://github.com/Unit-Zero-Labs/tidal-protocol-research/blob/acc46570060d662c415e6a0ca2dcea4f90dfba7b/tidal_protocol_sim/engine/high_tide_vault_engine.py#L994-L996)) sums slippage across all 3 copies, tripling the reported cost.


---

## Confidence Summary

| Image | Script | Confidence | Limiting factor |
|-------|--------|------------|-----------------|
| "Figure 2: Performance Matrix Heatmap" | `balanced_scenario_monte_carlo.py` | **High** | Visual + code roughly aligned with **original** config (pre-D7); \$53k prose discrepancy (D1); current committed config cannot reproduce (D7) |
| "Figure 5: Time Series Evolution" | `comprehensive_ht_vs_aave_analysis.py` | **High** | BTC price (\$76,342) + scenario names confirm source; import fix needed (D6) |
| "Pool Price Evolution (top panel)" | `hourly_test_with_rebalancer.py` | **Very High** | 10/10 parameter match; visual match |
| "Pool Price Evolution (bottom panel)" | `hourly_test_with_rebalancer.py` | **Very High** | Same output file |
| "Agent Rebalancing Analysis" | `hourly_test_with_rebalancer.py` | **High** (source attribution) / **Low** (reproducibility) | Source script, chart function, and layout confirmed. Slippage ~430× off due to swap formula change (D9, commit `48a9ff2`). Rebalance amounts close (~6% off). Reverting D9 would restore slippage to the range of the Primer's values. |
| "BTC Price Decline Over Time" | `hourly_test_with_rebalancer.py` | **Very High** | Linear \$100k→\$50k exactly matches config |
| "Agent Health Factor Evolution" | `hourly_test_with_rebalancer.py` | **Low** | Threshold lines match but sawtooth absent; only 2 data points due to D8 |
| "Yield Token Holdings Over Time" | `hourly_test_with_rebalancer.py` | **Low** | Linear instead of staircase; same D8 root cause |

## Remediation Status (updated 2026-03-10)

All remediations below are on branch `alex/sim-validation_commit-ba544b1`.

### `balanced_scenario_monte_carlo.py`

| Issue | Status | Commit/Edit | Notes |
|-------|--------|-------------|-------|
| D6 (dead import) | **Fixed** | Edit 1 — comment stub replacing deleted `target_health_factor_analysis` import | |
| D7 (btc_final_price) | **Fixed** | Edit 2 — restored to `76_342.50` (−23.66%) | |
| D9 (swap formula) | **Fixed** | Edit 5 / commit `081a011` — standard `get_amount0_delta` restored for YT→MOET output | |
| F4 (AAVE cascading liquidation) | **Fixed** | Edit 3 — direct debt repayment in `aave_agent.py:execute_aave_liquidation` | |
| Sim order (AAVE HF alignment) | **Fixed** | Edit 4 — AAVE runs before HT (HT resets seed; AAVE doesn't) | |
| B3 (fee bypass) | **Not fixed** | Pre-existing bug; fix is independent of reproduction | |
| B4 (triple-recording) | **Not fixed** | Pre-existing bug; inflates event counts and `cost_of_rebalancing` 3× | |

**Current state:** Runnable. Config matches Primer scenario (−23.66% BTC decline). Results in `results_commit-ba544b1/Balanced_Scenario_Monte_Carlo/` reflect all 5 edits. Full edit details: → `PRIMER-COMPATIBLE_balanced_scenario_monte_carlo.md`.

### `comprehensive_ht_vs_aave_analysis.py`

| Issue | Status | Notes |
|-------|--------|-------|
| D6 (dead import) | **Not fixed** | Same `target_health_factor_analysis` import as above; needs same fix |

### `hourly_test_with_rebalancer.py`

| Issue | Status | Notes |
|-------|--------|-------|
| D8 (snapshot frequency + x-axis) | **Not fixed** | Need `agent_snapshot_frequency_minutes = 1` in config + use `minute` field in chart code |
| D9 (swap formula) | **Fixed** | Commit `081a011` — applies globally to all simulations using `compute_swap_step` |
| B3 (fee bypass) | **Not fixed** | Pre-existing bug; independent fix |
| B4 (triple-recording) | **Not fixed** | Pre-existing bug; independent fix |

