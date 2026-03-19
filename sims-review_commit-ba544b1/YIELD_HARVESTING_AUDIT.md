# Yield Harvesting — Exhaustive Codebase Audit

**Date**: 2026-03-18  
**Scope**: All code, docs, reports, and prior review artifacts at commit `ba544b1`  
**Context**: The real-world FCM implementation (Flow Yield Vaults) performs a weekly `_check_deleveraging` call that can harvest rebased Yield Token (YT) gains — selling accrued yield, converting it to BTC, and depositing it as additional collateral. This is separate from efficiency rebalancing (which borrows more MOET to grow the YT position). This document maps that mechanism exhaustively across the simulation codebase. Note: the real-world trigger condition (HF > initial HF) differs from the simulation's HT implementation, where the weekly harvest is purely time-based; see [Key differences from HT harvest](#key-differences-from-ht-harvest).

---

## Terminology

**Yield harvesting** (working term): The process of selling accrued Yield Token yield and converting the proceeds into BTC collateral. In conventional DeFi usage, "harvesting" refers narrowly to collecting (claiming) accrued farming rewards — a routine operational step within yield farming. Our usage extends beyond this: the harvested yield is not merely claimed but actively converted cross-asset and redeployed as collateral. We retain the term for convenience while noting this distinction.

Distinguished from:
- **Efficiency rebalancing** (leverage increase): borrowing more MOET to buy more YT when HF > initial (grows the position)
- **Defensive deleveraging**: selling YT to repay MOET debt when HF < rebalancing threshold (shrinks debt)
- **HF deleveraging**: intended ~~to sell YT to reduce HF when it exceeds initial × 1.05~~ — self-contradictory logic, dead code, never fires (→ [HF_DELEVERAGING_DEAD_CODE.md](HF_DELEVERAGING_DEAD_CODE.md))

What makes this go beyond conventional harvest-and-reinvest:
1. **Cross-asset conversion**: accrued yield (YT-denominated) is converted through a multi-hop swap chain into BTC, a different token type, before being deposited as collateral
2. **Collateral reinforcement loop**: the deposited BTC raises the health factor, which can then trigger the separate leverage-increase path (10-minute check), creating a compounding cycle between two independent mechanisms

---

## Implementation: High Tide Agent Simulation

**Source**: [`tidal_protocol_sim/agents/high_tide_agent.py` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py)

### Entry point: [`_check_deleveraging` (line 723)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L723)

Called unconditionally every simulated minute from [`decide_action` (line 165)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L165). Two branches:

| Branch | Trigger | Action | Purpose |
|--------|---------|--------|---------|
| ~~Check 1 — HF deleveraging~~ | ~~`HF > initial_HF × 1.05`~~ | ~~Sell YT → BTC → deposit as collateral; sized to bring HF down to initial × 1.02~~ | ~~Position reduction~~ |
| Check 2 — Weekly harvest | Every 10,080 minutes (7 days) | Sell accrued yield → BTC → deposit as collateral | **Yield harvesting** |

~~Check 1 takes priority (evaluated first).~~ Check 1 is **dead code** — its sizing logic is self-contradictory (produces negative `debt_reduction_needed` when the trigger fires) and its execution path would increase HF rather than reduce it. Never fires in any simulation. Full analysis: → [HF_DELEVERAGING_DEAD_CODE.md](HF_DELEVERAGING_DEAD_CODE.md). Check 2 is skipped if the agent holds no YT.

### Weekly harvest: [`_execute_weekly_deleveraging` (line 775)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L775)

**Yield calculation** ([lines 800–812](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L800-L812)):
```
current_yt_price = calculate_true_yield_token_price(current_minute, 0.10, 1.0)
yt_price_increase = current_yt_price - last_weekly_yt_price
yt_yield_value = yt_price_increase × total_yt_quantity
```

The function uses the **global** YT price (all tokens share the same price at any moment, determined by the 10% APR rebasing formula). It sells only the yield accrued since the last weekly check, not principal.

First-week behavior: records the starting price but does not sell (no yield accrued yet).

Returns `("delever_weekly", {yt_amount, reason: "weekly_yt_yield_harvest", ...})`.

### Swap chain: [`execute_deleveraging` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L841) → [`_execute_deleveraging_swap_chain` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L904)

**Path** ([lines 841–1059](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L841-L1059)):

```
YT → MOET          (via engine pool, with Uniswap V3 slippage)
MOET → USDC/USDF   (random choice, via engine pool, with Uniswap V3 slippage)
USDC/USDF → BTC    (simplified market execution: 0.1% fee + 0.05% slippage)
BTC → collateral    (engine.protocol.supply(), updates btc_amount)
```

Each step tracks slippage individually. The final step ([lines 1017–1041](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L1017-L1041)) deposits the received BTC back into the Tidal protocol as collateral via `engine.protocol.supply(agent_id, Asset.BTC, btc_received)`, and updates `self.state.btc_amount`.

### State tracking

- `agent.state.last_weekly_delever_minute` — minute of last weekly check
- `agent.state.last_weekly_yt_price` — YT price at last weekly check
- `agent.state.deleveraging_events` — list of all deleveraging events (both HF and weekly)
- `agent.state.total_deleveraging_sales` — cumulative YT sold via deleveraging
- `agent.state.total_deleveraging_slippage` — cumulative slippage from deleveraging swaps

**Known gap (B5)**: Deleveraging YT sales are recorded in `agent.state.deleveraging_events` and `engine.deleveraging_events`, but are **not** consolidated into `engine.yield_token_trades`. Downstream consumers (`real_slippage_cost`, `total_rebalancing_sales`, chart functions) miss deleveraging trades. Pre-existing; does not affect short sims. → `FCM_PRIMER_FIGURE_MAPPING.md §B5`

---

## Implementation: AAVE Agent

**Source**: [`tidal_protocol_sim/agents/aave_agent.py` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/aave_agent.py)

### Entry point: [`execute_weekly_rebalancing` (line 307)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/aave_agent.py#L307)

Called externally by [`full_year_sim.py:1775` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/sim_tests/full_year_sim.py#L1775) at `leverage_frequency_minutes` intervals (default: weekly / 10,080 minutes). Not called from `decide_action` (which always returns HOLD for AAVE agents).

| Condition | Action | Purpose |
|-----------|--------|---------|
| `HF < initial_HF × 0.99` | Sell YT → MOET → repay debt (max 50% of YT per period) | Defensive deleveraging (debt reduction) |
| `HF ≥ initial_HF` (else branch) | Sell incremental yield → MOET → BTC → deposit as collateral | **Yield harvesting** |

### Harvest path ([lines 379–422](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/aave_agent.py#L379-L422))

**Yield calculation**:
```
incremental_yield = current_yt_value - last_harvest_yt_value
```

Baseline set to `total_initial_value_invested` on first harvest. Sells 100% of new yield each week.

**BTC conversion** ([line 404](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/aave_agent.py#L404)): Simple division `moet_received / btc_price` — no AMM, no multi-hop. Adds directly to `supplied_balances[Asset.BTC]` and `btc_amount`.

### Key differences from HT harvest

| Aspect | High Tide | AAVE |
|--------|-----------|------|
| Trigger | Internal timer (every minute checks if 7 days elapsed) | External call from sim loop at configured frequency |
| Yield basis | Price increase × quantity (rebasing) | Total value − last harvest value (mark-to-market) |
| BTC conversion | Full Uniswap V3 multi-hop swap chain with slippage | Simple division at market price |
| HF condition | None (fires regardless of HF, purely time-based) | Only when HF ≥ initial (else deleverages) |
| Collateral deposit | `engine.protocol.supply()` | Direct state mutation |

---

## Engine Integration

**Source**: [`tidal_protocol_sim/engine/high_tide_vault_engine.py` ](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/engine/high_tide_vault_engine.py)

The engine handles HT deleveraging actions at [line 394](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/engine/high_tide_vault_engine.py#L394):

```python
elif action_type in ["delever_hf", "delever_weekly"]:
    success = self._execute_deleveraging_action(agent, action_type, params, minute)
```

Both action types route through [`_execute_deleveraging_action` (line 591)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/engine/high_tide_vault_engine.py#L591), which calls `agent.execute_deleveraging()`. The engine records the event in `engine.deleveraging_events`.

AAVE's harvest is handled entirely within `aave_agent.execute_weekly_rebalancing` — the engine is only involved as a parameter (`engine` kwarg for pool access).

---

## Simulation Coverage

### Exercised (year-long simulations)

| Script | Duration | HT Harvest | AAVE Harvest | Notes |
|--------|----------|------------|--------------|-------|
| `full_year_sim.py` | ~365 days | ✓ (automatic, ~52 weekly checks) | ✓ (external call at `leverage_frequency_minutes`) | Base framework |
| Studies 1–10 (`run_study_*.py`) | 268–365 days | ✓ | ✓ | All set `enable_weekly_yield_harvest = True` |
| Study 11 (weekly min HF) | 365 days | ✓ | ✓ | |
| Study 12 (daily min HF) | 365 days | ✓ | ✓ (config sets False, but flag is dead — harvest fires regardless) | |
| Study 13 (monthly min HF) | 365 days | ✓ | ✓ (config sets False, but flag is dead — harvest fires regardless) | |
| Study 14 (liquidation cascade) | ~1 day | ✗ (too short) | ✗ | |

### Not exercised (too short for weekly timer)

| Script | Duration | Why |
|--------|----------|-----|
| `balanced_scenario_monte_carlo.py` | 60 minutes | Far below 10,080-minute threshold |
| `flash_crash_simulation.py` | ~2 days | Below threshold |
| `hourly_test_with_rebalancer.py` | 36 hours | Below threshold |

### Dead config flag: `enable_weekly_yield_harvest`

Set in all 14 study scripts on the `FullYearSimConfig` object. **Never read** by `full_year_sim.py`, any engine class, or any agent class. Zero references in the entire `tidal_protocol_sim/` package.

Impact: The flag has no gating effect. HT's weekly harvest fires unconditionally (internal timer in `_check_deleveraging`). AAVE's harvest fires whenever the external `execute_weekly_rebalancing` call reaches the else branch (HF ≥ initial). Studies 12 and 13 set it to `False` intending to disable harvest, but the setting is inert.

---

## Documentation Coverage

| Document | What it covers | Gaps |
|----------|----------------|------|
| `reports/High_Tide_vs_AAVE_Comparative_Analysis_Whitepaper.md` (lines 1556–1690) | Most detailed: Study 11 pseudocode for both deleverage and harvest branches, design choices (HF-based triggers, incremental yield, rebasing approximation), comparison tables | Describes design intent; does not note the dead config flag |
| `sims-review_commit-da4cbf9/SIMULATION_STUDY_CATEGORIZATION.md` (lines 24, 32–37) | Both agents documented: HT "Yield harvesting: Weekly deleveraging chain (`_check_deleveraging`, line 712)", AAVE "harvest accrued yield only → MOET → BTC → deposit (line 390-433)" | Line ref 712 is stale (now 723 after B4 fix) |
| `docs/HIGH_TIDE_VAULT_ENGINE_README.md` (lines 508–525) | Documents `_check_leverage_opportunity` (HF > initial → borrow more) | **Does not document** the weekly harvest path at all |
| `docs/BASE_CASE_README.md` (line 52) | Mentions "Delevering when HF drops (YT → MOET → Stable → BTC → redeposit)" | Defensive deleveraging context, not yield harvesting |
| `sim_tests/archive_tests/base_case_ht_vs_aave_comparison.py` (line 686) | Comment: "High Tide agents have built-in weekly deleveraging... triggered in agent.decide_action() -> _check_deleveraging()" | Brief comment, no detail |

---

## Interaction with Other Mechanisms

The [`decide_action` method (line 124)](https://github.com/onflow/tidal-protocol-research/blob/bdc93ff/tidal_protocol_sim/agents/high_tide_agent.py#L124) evaluates actions in this priority order:

1. **Minute 0**: Initial YT purchase
2. **Every 10 min**: If HF > initial → leverage increase (borrow more MOET, buy YT)
3. **Every min**: If HF < rebalancing_HF → defensive deleveraging (sell YT, repay debt)
4. **Every min**: `_check_deleveraging` → HF deleveraging OR weekly harvest
5. **Every min**: If HF ≤ 1.0 → emergency sale / liquidation

Because leverage increase (step 2) is checked *before* `_check_deleveraging` (step 4), the following interaction occurs:
- If BTC price rises → HF increases above initial → step 2 fires first (borrows more, buys YT)
- ~~This borrowing reduces HF back toward initial, which may prevent the HF deleveraging branch (Check 1) from firing~~ Check 1 is dead code regardless of priority ordering (→ [HF_DELEVERAGING_DEAD_CODE.md](HF_DELEVERAGING_DEAD_CODE.md))
- The weekly harvest (Check 2) still fires on schedule regardless, since it's purely time-based

This means both mechanisms can fire in the same week: leverage increase consumes the HF headroom every 10 minutes, while the weekly harvest sells accrued yield and deposits BTC once per week.

---

## Cross-References

- **Check 1 dead code**: [HF_DELEVERAGING_DEAD_CODE.md](HF_DELEVERAGING_DEAD_CODE.md) — three compounding errors make HF deleveraging inert
- **B5 (deleveraging tracking gap)**: `FCM_PRIMER_FIGURE_MAPPING.md §B5` — deleveraging YT sales not in `engine.yield_token_trades`
- **Dead config flag**: New finding; tracked in `SESSION_LOG.md` Open Questions
- **Rebalancing limits (no cooldown, no gas)**: `TECHNICAL.md § High Tide Rebalancing Limitations`
- **AAVE collateral factor inconsistency (0.85 vs 0.80)**: `SIMULATION_STUDY_CATEGORIZATION.md` (da4cbf9), `CONCLUSIONS.md`
