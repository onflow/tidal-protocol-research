# Primer-Compatible Run: `balanced_scenario_monte_carlo.py`

**Date:** 2026-03-03
**Analyst:** AI (reviewed by AlexH)
**Commit under analysis:** `ba544b1`
**Script:** `sim_tests/archive_tests/balanced_scenario_monte_carlo.py`
**Primer figure:** §4.2, Figure 2 — "Performance Matrix Heatmap: High Tide vs AAVE"
**Prior analysis:** [`sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`](../sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md)

---

## Context

`ba544b1` introduced no substantive code changes — only file reorganization (scripts moved to `archive_tests/` and `comprehensive_tests/` subdirectories). `balanced_scenario_monte_carlo.py` is byte-identical to its `da4cbf9` counterpart. All bugs and post-delivery changes identified in the prior analysis persist unchanged.

This document records the minimal set of edits required to produce a Primer-compatible run at `ba544b1`, and the results achieved.

---

## Edits Applied

### Edit 1 — Broken import removal
**File:** `sim_tests/archive_tests/balanced_scenario_monte_carlo.py` (lines 33–35)

```python
# Before
from target_health_factor_analysis import create_custom_agents_for_hf_test

# After (comment stub)
# target_health_factor_analysis was removed in commit 684c007;
# create_custom_agents_for_hf_test was imported but never used in this script.
```

**Rationale:** `target_health_factor_analysis.py` was deleted in commit `684c007`. The imported function `create_custom_agents_for_hf_test` is never called anywhere in the script — the import is dead code. Without this fix: `ModuleNotFoundError` on launch. **Not a logic change.**

---

### Edit 2 — Restore `btc_final_price` (D7)
**File:** `sim_tests/archive_tests/balanced_scenario_monte_carlo.py` (line 204)

```python
# Before
self.btc_final_price = 90_000.0  # 25.00% decline (consistent with previous analysis)

# After
self.btc_final_price = 76_342.50  # 23.66% decline (original value before 684c007)
```

**Rationale:** Commit `684c007` (2025-09-25) silently changed this value while moving the file. The comment is wrong on both counts — 90,000 is a 10% decline from 100,000, not 25%. The original value `76_342.50` is consistent with the Primer's stated scenario (BTC −23.66%). Without this fix: BTC drop is too mild to trigger any AAVE liquidations → 100/100% survival across all runs.

Details: [`FCM_PRIMER_FIGURE_MAPPING.md §D7`](../sims-review_commit-da4cbf9/FCM_PRIMER_FIGURE_MAPPING.md).

---

### Edit 3 — Fix AAVE cascading liquidation (F4)
**File:** `tidal_protocol_sim/agents/aave_agent.py` (`execute_aave_liquidation`, lines 196–208)

```python
# Before: BTC → MOET swap via Uniswap V3 pool
pool = create_moet_btc_pool(pool_size_usd, btc_price)
calculator = UniswapV3SlippageCalculator(pool)
swap_result = calculator.calculate_swap_slippage(btc_value_to_swap, "BTC")
actual_moet_received = swap_result["amount_out"]

# After: direct debt repayment (no AMM intermediary)
# (Original swap replaced because the MOET:BTC pool scaling bug causes
# LIQUIDITY COVERAGE FAILURE, returning amount_out=0, which seizes BTC
# without repaying debt and causes cascading liquidations.)
actual_moet_received = debt_reduction
swap_result = {"slippage_amount": 0, "trading_fees": 0, "price_impact_percentage": 0}
```

**Root cause chain:**
1. `execute_aave_liquidation` creates a fresh MOET:BTC Uniswap V3 pool and tries to swap seized BTC → MOET
2. The pool has a scaling bug in `_initialize_btc_pair_positions`: uses `total_liquidity × 1e6` as L regardless of token price ratios, producing ~1:1 raw-unit output instead of the correct ~79,000:1 for BTC:MOET
3. Pool exhausts liquidity → `LIQUIDITY COVERAGE FAILURE` → `amount_out = 0`
4. BTC seized but zero debt repaid → HF crashes (1.0 → 0.55 → 0.10 → 0) → 3 cascading liquidations per agent → ~$78k total cost (vs Primer's ~$33k)

**Rationale:** In real AAVE, the liquidator supplies stablecoins directly to repay debt — there is no AMM swap in the liquidation path. Modeling it as direct debt repayment is both mechanically correct and unblocks the simulation. The MOET:BTC pool scaling bug itself is a separate finding tracked in the prior analysis.

Details: [`DISCREPANCY-ANALYSIS §F4`](../sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md#f4-current-engine-triggers-multiple-aave-liquidation-events-per-agent).

---

### Edit 4 — Swap simulation order
**File:** `sim_tests/archive_tests/balanced_scenario_monte_carlo.py` (lines 425–431)

```python
# Before: HT first, then AAVE
ht_result = self._run_high_tide_scenario(...)
aave_result = self._run_aave_scenario(...)

# After: AAVE first, then HT
aave_result = self._run_aave_scenario(...)
ht_result = self._run_high_tide_scenario(...)
```

**Rationale:** `_run_high_tide_scenario` resets the RNG seed internally (line 472: `random.seed(seed); np.random.seed(seed)`), making HT agent health factors invariant to execution order. `_run_aave_scenario` does not reset the seed — AAVE agent HFs are determined by the RNG state at the moment the AAVE engine constructor runs, which depends on how many draws were consumed before it. In the original order, the HT simulation loop consumes `np.random` draws (BTC price path), shifting the RNG state before AAVE agent creation and producing HFs that do not match the Primer pattern. Running AAVE first gives it the initial-seed RNG state, improving survival rate alignment.

Details: [`DISCREPANCY-ANALYSIS §F2, §F6, §F7, Attempt 4`](../sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md).

---

### Edit 5 — Revert swap formula to standard Uniswap V3 (D9)
**File:** `tidal_protocol_sim/core/uniswap_v3_math.py` (`compute_swap_step`, lines 335–346)

```python
# Before: floating-point "economic" formula for YT→MOET output
if exact_in and amount_remaining_less_fee > 0:
    amount_out = get_amount0_delta_economic(
        sqrt_price_current_x96, sqrt_price_next_x96, liquidity, amount_remaining_less_fee
    )
else:
    amount_out = get_amount0_delta(
        sqrt_price_current_x96, sqrt_price_next_x96, liquidity, False
    )

# After: standard Uniswap V3 Q96 integer formula for all cases
amount_out = get_amount0_delta(
    sqrt_price_current_x96, sqrt_price_next_x96, liquidity, False
)
```

**Rationale:** Commit `48a9ff2` (2025-09-29) replaced the standard Uniswap V3 output formula (`get_amount0_delta`, Q96 integer math) with a floating-point shortcut (`get_amount0_delta_economic`) for YT→MOET swaps. The shortcut computes `output = input / (1 + input/(L×√P))` directly, bypassing the two-step integer pipeline (amount→price→output) and its associated truncation. This collapses HT rebalancing slippage from ~$2 per trade to ~$0.005, making HT costs appear zero.

The standard formula IS the real Uniswap V3 formula — same Q96 fixed-point arithmetic as `SqrtPriceMath.sol` on-chain, including round-down-for-output behavior. The "5.66% efficiency loss" cited in the original comment is not a bug — it reflects AMM price impact and integer rounding that real swaps incur. The magnitude is likely amplified by the simulation's pool scaling (smaller liquidity values than real-world pools), but the direction is correct: swaps have non-zero friction. The economic formula eliminates this friction entirely, making the HT vs AAVE cost comparison non-representative.

Details: [`FCM_PRIMER_FIGURE_MAPPING.md §D9`](../sims-review_commit-da4cbf9/FCM_PRIMER_FIGURE_MAPPING.md).

---

## Summary Table

| Edit | File | Type | Required to run? | Required for Primer alignment? |
|------|------|------|-----------------|-------------------------------|
| 1. Import stub removal | `balanced_scenario_monte_carlo.py` | Dead-code removal | **Yes** (crashes otherwise) | — |
| 2. `btc_final_price` restore | `balanced_scenario_monte_carlo.py` | Config correction (D7) | No | **Yes** (zero liquidations otherwise) |
| 3. Direct debt repayment | `aave_agent.py` | Bug fix (F4) | No | **Yes** (3× liquidations, 2.4× cost otherwise) |
| 4. Simulation order swap | `balanced_scenario_monte_carlo.py` | Ordering fix | No | **Yes** (reduces survival error 0/5 → 1/5) |
| 5. Revert swap formula | `uniswap_v3_math.py` | Formula revert (D9) | No | **Yes** (HT cost $0 vs $19–22 otherwise) |

## Results

*Pending re-run after Edit 5. Prior results (Edits 1–4 only) showed HT cost ~$0 due to D9.*

---

## Known Remaining Gaps

| Gap | Root cause | Status |
|-----|-----------|--------|
| AAVE survival 1/5 match | F2: HFs deterministic at current RNG position; no committed code version produces Primer's pattern | Open — likely requires uncommitted seed/config |
| AAVE cost +5% residual | Collateral factor 0.80→0.85 (`2fd742d`) | Known, quantified, not fixed |
