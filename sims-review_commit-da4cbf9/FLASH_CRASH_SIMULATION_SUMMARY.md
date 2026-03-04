# Flash Crash Simulation Summary

**Date** of last update: 2026-02-20  
**Source**: `run_flash_crash.py` → `sim_tests/flash_crash_simulation.py`

---

## What It Tests

A **25-minute simultaneous crash** of YT and BTC prices with cascading market-structure effects (liquidity evaporation, oracle attacks, forced liquidations), followed by a 2-hour recovery and ~1.5 days of observation.

Single scenario type at **three severity levels** (mild / moderate / severe).

---

## Timeline

| Phase | Window | Duration |
|---|---|---|
| Normal operations | Day 1, 00:00–14:55 | 895 min |
| Oracle attack (pre-crash) | Day 1, 14:55–15:00 | 5 min |
| Flash crash | Day 1, 15:00–15:25 | 25 min |
| Recovery | Day 1, 15:25–17:25 | 120 min |
| Long-term observation | Day 1, 17:25 → Day 3 | ~1,835 min |

Oracle attack starts 5 min before BTC drops (`oracle_crash_offset_minutes = -5`, line 68). Agent rebalancing is **blocked** during this oracle-only window (line 814).

---

## Scenario Parameters

| Parameter | Mild | Moderate | Severe |
|---|---|---|---|
| YT crash magnitude | 20% → $0.80 | 32% → $0.68 | 45% → $0.55 |
| YT wick (intra-crash low) | −10% further | −15% further | −20% further |
| BTC crash magnitude | 12% | 20% | 25% |
| Peak liquidity reduction | 60% | 70% | 80% |
| Oracle volatility | ±5% | ±8% | ±12% |

Config: `FlashCrashSimConfig.__init__`, lines 72–92.

---

## System Setup

- **150 agents**, ~$133k MOET debt each ($20M total), HF: initial 1.15 / rebalancing 1.05 / target 1.08
- **BTC**: starts at $100k, collateral factor 0.80
- **MOET:BTC pool**: $5M; **MOET:YT pool**: $500k (95% concentrated at peg)
- **10 MOET arbitrage agents** ($50k each) for peg maintenance
- YT continues rebasing at 10% APR throughout crash

Agent creation: `_create_large_debt_agents` (line 682); position setup: `_setup_large_system_positions` (line 704).

---

## Core Stress Mechanisms

### 1. BTC Price 

code: `_calculate_btc_price_during_crash` (line 921 in `flash_crash_simulation.py`)

- **Pre-crash**: stable at $100k
- **Crash**: linear drop over 5 min to floor (`base_price × (1 − btc_crash_magnitude)`), then holds at floor for remaining 20 min
- **Recovery**: exponential curve `recovery_factor = 1 − (1 − progress)^1.5` back to $100k, with ±2% random volatility per minute

### 2. Oracle Manipulation 
code: `OracleMispricingEngine.get_manipulated_yt_price` (line 337)

- **During crash**: `oracle_price = true_yt_price × (1 − yt_crash_magnitude × crash_progress)`, floored at `yt_floor_price`, plus uniform random volatility ±`oracle_volatility`
- **Wicks**: ~12% chance per minute (`_should_inject_wick`, line 377); wick magnitude = `current_price × (1 − yt_wick_magnitude)` (line 388)
- **Recovery**: exponential `recovery_factor = 1 − (1 − progress)^2` from floor back to true price (line 403–427)

### 3. Liquidity Evaporation 
code: `LiquidityEvaporationManager.update_liquidity_during_crash` (line 183)

**Modelling goal**: liquidity evaporation, i.e. market makers pulling quotes, one-sided order flow, reflexive slippage spirals, and slow cautious re-entry. The simulation does **not** remove LP positions from the Uniswap V3 pool directly; instead it emulates the effect by throttling the **rebalancers** (terminology in the code), which are two agents that emulate (simplified) arbitrageurs maintaining MOET:YT pool price accuracy.

**Arbitrageur model**:
- **Two agents** (`ALMRebalancer`, `AlgoRebalancer`) with **fixed capital** replace the competitive anonymous arbitrageur market. `ALMRebalancer` acts on a 12-hour schedule; `AlgoRebalancer` acts whenever pool-oracle deviation exceeds 25 bps. In comparison, real arbitrage is driven purely by profit opportunity across a field of competing actors with dynamic capital.
- **Frictionless external exit**: when a rebalancer buys underpriced YT from the pool, it assumes it can immediately sell at full oracle price externally with no slippage. Real arbitrageurs face execution risk on both legs.
- **No strategic behavior**: rebalancers always act when their trigger fires; they don't reason about crash duration, counterparty risk, or opportunity cost. Real arbitrageurs might deliberately hold off during extreme volatility.
- **Liquidity evaporation is exogenous**: the market conditions change irrespective of how good or bad the lending protocol and the user agents handle the situation. Specifically, the throttling curve is a predetermined schedule, not driven by realized P&L or balance-sheet constraints. Real arbitrage capacity shrinks endogenously as losses accumulate (including system-internal feedback that is not modelled here).

**Two levers**:
1. **Capital reduction** — rebalancer `moet_balance` (total MOET the rebalancer can deploy) and `max_single_rebalance` (cap on a single swap transaction) scaled by `liquidity_factor = 1 − reduction` (line 209, applied at line 234–254)
2. **Profit threshold inflation** — `min_profit_threshold` multiplied by `1 + reduction × 10` (line 278), making rebalancers unwilling to buy the falling asset

**Crash-phase reduction curve** (lines 196–209):
- **First half** (0–50% crash progress): linear from `liquidity_reduction_start` (30%) → `liquidity_reduction_peak` (60/70/80% by scenario)
- **Second half** (50–100%): exponential acceleration `peak × (1 + ((progress−0.5)×2)² × 0.2)`, capped at 95%


**Recovery** (lines 297–321)
*  piecewise-linear restoration — 50% by +60 min, 90% by +120 min, full after 2 hours. Both `ALMRebalancer`  and `AlgoRebalancer` are throttled during recovery (unlike the crash where `AlgoRebalancer` was exempt).
* `restored_factor` starts at `min_liquidity` (e.g. `0.3` in moderate scenario — the crash trough) and climbs back toward `1.0`
* This `restored_factor` is passed to `_apply_liquidity_reduction` (line 321), which during recovery applies the same throttling to both `ALMRebalancer` and Alg`AlgoRebalancer`o (lines 248–254, i.e. the else branch where `is_crash_window` is false).

**Modelling the most conservative / worst case Arbitrageur behavior** (lines 221–262)

* **During crash**: `AlgoRebalancer` has full capital and freely moves the pool price toward the (crashing, manipulated) oracle, i.e. it actively *drives the pool price down*. Meanwhile `ALMRebalancer, which might otherwise provide stabilizing buys, is throttled and can't counteract this.

* **During recovery**: `AlgoRebalancer` is throttled, so it can't efficiently push the pool price *back up* toward the recovering oracle. `ALMRebalancer` is also still impaired (liquidity of arbitrageurs restores gradually, starting at crash-trough level, reaching 50% after 60 min, 90% after 120 min), so both arbitrageurs operate at reduced capital throughout. Recovery is slow.

This is a deliberate worst-case modeling choice: automated market infrastructure *amplifies* the crash by faithfully tracking a manipulated oracle at full power, then can't undo the damage quickly because the same infrastructure is throttled in the opposite direction.


**Not modeled**: actual LP position withdrawal from pool tick ranges; external arbitrageur exits; endogenous feedback (real evaporation is driven by realized losses — here the curve is predetermined).

### 4. Forced Liquidations 

code: `ForcedLiquidationEngine.process_crash_liquidations` (line 460)

Active only during crash window. For any agent with `HF < 1.0`:
- Liquidates 50% of BTC collateral, 5% liquidation bonus (line 487–488)
- **Crash slippage**: 2× base (2% base × 2 = 4% total) (line 491–493)
- Debt reduced by `min(btc_value_net, moet_debt)` (line 501)
- Agent deactivated if residual debt ≤ $100 (line 505–506)

---

## Main Simulation Loop

code: `_run_crash_simulation_with_tracking` (line 757)

Per-minute loop for 2,880 minutes. Each tick:

1. **BTC price**: override via `_calculate_btc_price_during_crash` (line 784)
2. **YT price**: `calculate_true_yield_token_price` → `oracle_engine.get_manipulated_yt_price` (lines 789–791)
3. **Liquidity**: `liquidity_manager.update_liquidity_during_crash` (line 795)
4. **Protocol interest**: `engine.protocol.accrue_interest()` (line 799)
5. **Agent processing**: `engine._process_high_tide_agents(minute)` — standard HT agent decision loop (line 825)
6. **Forced liquidations**: during crash only (lines 832–836)
7. **Pool rebalancing**: ALM + Algo with oracle price override; deviation calculated in $/YT units (lines 839–889)
8. **Arbitrage agents**: MOET peg maintenance (lines 892–893)
9. **Metrics recording**: every minute during crash, every 15 min otherwise (line 897)

---

## Key Metrics Tracked

| Metric | Source |
|---|---|
| Agent survival rate | `results["agent_performance"]["survival_rate"]` |
| Liquidation events | `results["liquidation_events"]` |
| Oracle manipulation events | `results["oracle_events"]` |
| Pool state snapshots (price, liquidity) | `results["pool_state_snapshots"]` |
| Rebalancing events (ALM, Algo, agent) | `results["rebalancing_events"]` |
| BTC/YT price histories | `results["simulation_results"]["btc_price_history"]` / `yt_price_history` |

---

## Notable Design Choices

1. **BTC price is deterministic** (linear crash, exponential recovery + uniform noise) — not driven by historical data or stochastic model.
2. **Oracle attack precedes the crash** by 5 min, with agent rebalancing blocked during this window — simulates information asymmetry / front-running.
3. **Algo rebalancer is asymmetrically treated**: full power during crash (drives pool toward oracle), throttled during recovery — this amplifies the crash and slows recovery by design.
4. **Only HT agents** — no AAVE agent comparison. This is a pure protocol resilience test, not a comparative study.
5. **YT rebasing continues at 10% APR** throughout the crash — tests whether accrual offsets value destruction.
6. **Forced liquidation engine runs in parallel** with the normal HT agent emergency logic — both `process_crash_liquidations` (line 460) and the HT agent's own `_execute_emergency_yield_sale` can trigger.
