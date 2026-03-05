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

**Rationale:** Commit `684c007` (2025-09-25) silently changed this value while moving the file. The comment is wrong on both counts — 90,000 is a 10% decline from 100,000, not 25%. The original value `76_342.50` matches the Primer's stated scenario (BTC −23.66%). Without this fix: BTC drop is too mild to trigger any AAVE liquidations → 100/100% survival across all runs.

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

## Results

Config: `ComprehensiveComparisonConfig` — 5 scenarios × 5 agents, BTC $100k → $76,342.50 (−23.66%), 60 min.

### AAVE Survival Rate

| Run | Sim | Primer | Δ |
|-----|-----|--------|---|
| 1 | 60% | 40% | +20pp |
| 2 | 40% | 60% | −20pp |
| 3 | **80%** | **80%** | **0 ✓** |
| 4 | 40% | 60% | −20pp |
| 5 | 60% | 80% | −20pp |

- HT survival: 100% all runs ✓
- Exact match: Run 3 only. Others off by exactly 20pp (one agent each). Total error: 80pp.
- This is the best achievable result from committed code — identical to da4cbf9 Attempt 4.
- Remaining gap: AAVE agent HFs are deterministic at this RNG position and cannot match the Primer's (40%, 60%, 80%, 60%, 80%) pattern without either a different seed, a different HF draw range, or a code path that consumes a different number of RNG draws before AAVE agent creation. See [`DISCREPANCY-ANALYSIS §F2`](../sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md) for the mathematical proof that no single liquidation threshold can explain the Primer's pattern given the HFs produced by this code.

### AAVE Cost per Liquidation

| Run | Sim | Primer | Δ |
|-----|-----|--------|---|
| 1 | $34,678 | $32,956 | +5.2% |
| 2 | $34,677 | $32,884 | +5.5% |
| 3 | $34,516 | $32,946 | +4.8% |
| 4 | $34,719 | $32,931 | +5.4% |
| 5 | $34,326 | $32,315 | +6.2% |

Residual ~+5%: explained by collateral factor change (0.80 → 0.85 in commit `2fd742d`). A higher collateral factor means more debt is borrowed at a given HF, so 50% debt repayment seizes proportionally more BTC.

### HT Cost per Agent

~$0 across all runs vs Primer's $19–22. This is D9 (commit `48a9ff2`, 2025-09-29): `compute_swap_step` was changed from `get_amount0_delta` (Q96 integer math, ~$2 slippage per $842 trade) to `get_amount0_delta_economic` (floating-point, ~$0.005 slippage). The Primer was generated in the 4-day window before this change. Reverting D9 is not applied here — tracked as a separate open item.

Full provenance: [`FCM_PRIMER_FIGURE_MAPPING.md §D9`](../sims-review_commit-da4cbf9/FCM_PRIMER_FIGURE_MAPPING.md).

---

## Summary Table

| Edit | File | Type | Required to run? | Required for Primer alignment? |
|------|------|------|-----------------|-------------------------------|
| 1. Import stub removal | `balanced_scenario_monte_carlo.py` | Dead-code removal | **Yes** (crashes otherwise) | — |
| 2. `btc_final_price` restore | `balanced_scenario_monte_carlo.py` | Config correction (D7) | No | **Yes** (zero liquidations otherwise) |
| 3. Direct debt repayment | `aave_agent.py` | Bug fix (F4) | No | **Yes** (3× liquidations, 2.4× cost otherwise) |
| 4. Simulation order swap | `balanced_scenario_monte_carlo.py` | Ordering fix | No | **Yes** (reduces survival error 0/5 → 1/5) |

## Known Remaining Gaps

| Gap | Root cause | Status |
|-----|-----------|--------|
| HT cost ~$0 vs Primer $19–22 | D9: swap formula changed post-Primer (`48a9ff2`) | Open — requires reverting `compute_swap_step` |
| AAVE survival 1/5 match | F2: HFs deterministic at current RNG position; no committed code version produces Primer's pattern | Open — likely requires uncommitted seed/config |
| AAVE cost +5% residual | Collateral factor 0.80→0.85 (`2fd742d`) | Known, quantified, not fixed |
