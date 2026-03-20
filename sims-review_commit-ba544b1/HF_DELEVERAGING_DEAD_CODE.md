# HT Check 1 (HF Deleveraging): Dead Code Analysis

**Date**: 2026-03-18
**Scope**: [`_execute_hf_deleveraging` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L744) in `high_tide_agent.py`, triggered by [`_check_deleveraging` (line 723)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L723)
**Status**: Dead code — three compounding errors prevent execution and contradict stated intent
**Impact**: None on simulation results (code never fires). Affects documentation accuracy only.
**Simulations affected**: All simulations that instantiate `HighTideAgent` contain this code path, but it never executes. See [Affected simulations](#affected-simulations).

---

## Sources of intent

Check 1 has **no external documentation** — not in `reports/`, `docs/`, or the whitepaper. The only intent signals come from the code itself:

| Source | What it says | Location |
|--------|-------------|----------|
| `_check_deleveraging` docstring | "Health factor > initial HF + 5% (crazy price moves)" | [line 725](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L725) |
| `_execute_hf_deleveraging` docstring | "Execute deleveraging when HF is >5% above initial HF" | [line 745](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L745) |
| Inline comment | "Sell enough YT to bring HF back to initial HF + 2% (safety buffer)" | [line 753](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L753) |
| Print statement | "Selling ${yt_to_sell} YT to reduce debt by ${debt_reduction_needed}" | [line 766](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L766) |
| Variable name | `debt_reduction_needed` | [line 757](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L757) |
| Return action type | `"delever_hf"` | [line 768](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L768) |

**Inferred intent**: When a large BTC price spike pushes HF far above initial (>5%), sell some YT to reduce leverage back to a safer level (initial + 2%). The mechanism should reduce debt exposure.

---

## Three layers of contradiction

### Layer 1: Sizing logic is self-defeating

The sizing math ([lines 754–757](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L754-L757)):

```python
target_hf = initial_health_factor * 1.02
collateral_value = BTC × P_BTC × 0.85            # numerator of HF
target_debt = collateral_value / target_hf
debt_reduction_needed = moet_debt - target_debt
```

HF is defined as `collateral_value / (moet_debt × P_MOET)` ([line 475](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L475)), so `moet_debt = collateral_value / (HF × P_MOET)`.

At P_MOET ≈ 1.0:

```
debt_reduction_needed = collateral_value/HF − collateral_value/(initial×1.02)
                      = collateral_value × (1/HF − 1/(initial×1.02))
```

The trigger requires HF > initial × 1.05. Since initial × 1.05 > initial × 1.02, we always get `1/HF < 1/(initial×1.02)`, making `debt_reduction_needed < 0`. The guard at [line 759](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L759) returns `no_action`.

**The sizing math asks "how much debt must I shed to reach target_hf?" — but when HF is already above target_hf, the answer is negative.**

Edge case: `target_debt` is computed in USD-like units (via `collateral_value / target_hf`), while `moet_debt` is in MOET units. If P_MOET drops below ~0.97, the unit mismatch could make `debt_reduction_needed` positive. But this depends on a MOET depeg, not on the intended "crazy price moves" trigger.

### Layer 2: Execution path contradicts the stated purpose

Even if the sizing logic produced a positive value, the execution path is [`execute_deleveraging` (line 841)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L841) → [`_execute_deleveraging_swap_chain` (line 904)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L904):

```
YT → MOET → USDC/USDF → BTC → deposit as collateral
```

This **adds BTC collateral** without reducing MOET debt:
- Numerator (BTC × P_BTC × 0.85) goes **up**
- Denominator (moet_debt × P_MOET) stays **unchanged**
- Net: HF **increases**

But the stated purpose is to bring HF **down** from >initial×1.05 to initial×1.02. The execution does the opposite.

To actually reduce HF from above, the code would need to either reduce collateral (withdraw BTC) or increase debt (borrow more MOET) — the latter is what the leverage-increase path already does.

### Layer 3: Priority ordering preempts execution

In [`decide_action` (line 124)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L124), leverage increase (step 2) is evaluated every 10 minutes *before* `_check_deleveraging` (step 4):

1. **At 10-minute marks**: HF > initial triggers leverage increase → borrows MOET, buys YT → HF pushed back toward initial → `decide_action` returns early, `_check_deleveraging` never reached
2. **At non-10-minute marks**: `_check_deleveraging` runs, but Layer 1 ensures it returns `no_action`

So Check 1 is unreachable from both directions: preempted by leverage increase at 10-minute boundaries, and self-defeating at all other times.

---

## Summary

| Aspect | Intent (from code comments) | Code behavior |
|--------|----------------------------|---------------|
| When | HF > initial × 1.05 ("crazy price moves") | Trigger fires, but sizing returns `no_action` |
| What | Sell YT to "reduce debt" | Execution path adds collateral, doesn't touch debt |
| Effect | "Bring HF back to initial × 1.02" | Would increase HF if it fired |
| Reach | Independent safety mechanism | Preempted by leverage increase at 10-min marks |

**Check 1 is dead code with three compounding errors**: the sizing arithmetic is self-defeating at P_MOET ≈ 1, the execution path contradicts the stated direction, and the priority ordering preempts it. The weekly harvest (Check 2) and the leverage-increase path are the mechanisms that actually handle the HF > initial case.

---

## Affected simulations

`_check_deleveraging` is called from `HighTideAgent.decide_action`, which runs every simulated minute in all simulations that instantiate HT agents. Since Check 1 never produces an action (Layer 1), the bug has **zero impact on any simulation output**. The affected code is present but inert in:

| Simulation | HT Agents? | Check 1 reachable? | Impact |
|-----------|------------|-------------------|--------|
| `full_year_sim.py` + Studies 1–10 | ✓ | Evaluated every non-10-min minute, always returns `no_action` | None |
| `balanced_scenario_monte_carlo.py` | ✓ | Same | None |
| `flash_crash_simulation.py` | ✓ | Same | None |
| `hourly_test_with_rebalancer.py` | ✓ | Same | None |
| `comprehensive_ht_vs_aave_analysis.py` | ✓ | Same | None |
| `base_case_ht_vs_aave_comparison.py` | ✓ | Same | None |
| `diagnostic_base_case.py`, `test_hf_update.py`, `test_hf_with_decide.py` | ✓ | Same | None |
| `longterm_scenario_analysis.py`, `tri_health_factor_analysis.py` | ✓ | Same | None |
| `comprehensive_realistic_pool_analysis.py`, `rebalance_liquidity_test.py` | ✓ (via engine) | Same | None |
| `stress_testing/runner.py`, `stress_testing/comparison_scenarios.py` | ✓ (via engine) | Same | None |

**Not affected** (AAVE-only, no HighTideAgent): Studies 11–14, `aave_leverage_strategy_sim_v2.py`

No code outside `high_tide_agent.py` calls `_check_deleveraging` or `_execute_hf_deleveraging` directly.

---

## Verification

Verified on the remote GitHub repo at commit `ba544b1` (origin/main). The dead code exists identically there, with slightly shifted line numbers due to prior edits on the validation branch:

| Item | `ba544b1` (main) | `bdc93ff` (HEAD, validation branch) |
|------|-------------------|--------------------------------------|
| `_check_deleveraging` | line 720 | line 723 |
| `_execute_hf_deleveraging` | line 741 | line 744 |
| `debt_reduction_needed` guard | line 756 | line 759 |

No edits have been made to these methods on either branch. The logic is byte-identical.

---

## Cross-References

- **YIELD_HARVESTING_AUDIT.md** — Check 1 row in the entry point table annotated as dead code, referencing this document
- **SIMULATION_STUDY_CATEGORIZATION.md** (da4cbf9, line 24) — describes `_check_deleveraging` but only mentions Check 2 (weekly harvest); Check 1 was never documented externally
