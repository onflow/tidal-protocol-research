# Technical Domain Knowledge

Last updated: 2026-02-07

## Terminology

| Term | Definition | Source | Status |
|------|------------|--------|--------|
| Health Factor | `HF = (BTC_amount × P_BTC × 0.85) / (Debt_MOET × P_MOET)`; <1 triggers liquidation | `high_tide_agent.py:462-472, 478-488` | verified |
| Tri-Health Factor | Initial HF (position sizing + leverage trigger), Rebalancing HF (defensive trigger), Target HF (rebalancing goal) | `high_tide_agent.py:25-27` | verified |
| MOET | Tidal Protocol's stablecoin; backed by basket of loan collateral assets; price = k × geometric_mean(backing_assets) | Auditor directive | verified |
| MOET ($1 peg) | **INVALIDATED** - Prior assumption that MOET is pegged to $1 USD | Codebase (outdated) | invalidated |
| Yield Token (YT) | Token representing future yield; value accrues over time | `yield_tokens.py` | unverified |
| Tick | Uniswap V3 price discretization unit; price = 1.0001^tick | `uniswap_v3_math.py` | unverified |
| Q64.96 | Fixed-point format: 64 integer bits, 96 fractional bits | `uniswap_v3_math.py` | unverified |
| Collateral Factor | Max borrowing power as fraction of collateral | `protocol.py` | unverified |
| Liquidation Threshold | HF level below which liquidation occurs | `protocol.py` | unverified |
| Bonder | MOET system participant who provides liquidity via bonds | `moet.py` | unverified |
| Reserve Ratio | Target backing reserves as fraction of MOET supply (10%) | `moet.py` | unverified |

## Core Formulas

### Yield Token Value
- **Expression**: `V(t) = V₀ × (1 + APR)^(t / 525600)`
- **Variables**: 
  - V₀: initial price
  - APR: annual percentage rate
  - t: time in minutes
  - 525600: minutes per year
- **Code ref**: `yield_tokens.py`
- **Status**: unverified

### Uniswap V3 Tick-to-Price
- **Expression**: `price = 1.0001^tick`
- **Variables**:
  - tick: integer tick index
  - price: token0/token1 price ratio
- **Code ref**: `uniswap_v3_math.py`
- **Status**: unverified

### Health Factor (High Tide)
- **Expression**: `HF = (BTC_amount × P_BTC × 0.85) / (Debt_MOET × P_MOET)`
- **Variables**:
  - BTC_amount: agent's supplied BTC collateral
  - P_BTC: current BTC price
  - 0.85: BTC liquidation threshold (hardcoded, `high_tide_agent.py:487`)
  - Debt_MOET: agent's current MOET debt (including accrued interest)
  - P_MOET: MOET price (defaults to 1.0 in asset_prices)
- **Code ref**: `high_tide_agent.py:462-472` (`_update_health_factor`), `high_tide_agent.py:478-488` (`_calculate_effective_collateral_value`)
- **Status**: verified (auditor confirmed 2026-02-07)

### Debt Reduction (Rebalancing)
- **Expression**: `Debt_reduction = Debt_current - (BTC_amount × P_BTC × 0.85) / HF_target`
- **Variables**:
  - Debt_current: agent's current MOET debt
  - HF_target: Target Health Factor (post-rebalancing goal)
- **Trigger**: `HF < Rebalancing_HF`
- **Code ref**: `high_tide_agent.py:255-260` (`_execute_rebalancing`)
- **Status**: verified (auditor confirmed 2026-02-07)

## Algorithmic Abstractions

### High Tide Agent Rebalancing
**Purpose**: Maintain health factor within target bounds through automated position management
**Inputs**: Current HF, tri-health factor thresholds, asset prices, YT holdings
**Outputs**: Sell YT → repay MOET debt → reduce leverage
**Core Logic**:
1. Every simulated minute: recalculate HF from current BTC price and debt
2. If `HF < Rebalancing_HF`: compute `debt_reduction = debt - collateral/HF_target`, sell YT for MOET, repay debt
3. Iterate up to 3 cycles; stop when `HF ≥ Rebalancing_HF`
4. If `HF > Initial_HF` (checked every 10 min): borrow more MOET, buy YT (leverage increase)
5. If `HF ≤ 1.0`: emergency — sell ALL remaining YT
**Default thresholds** (full_year_sim): Initial=1.3, Rebalancing=1.1, Target=1.2
**Checking frequency**: Every minute (automatic); compare AAVE: periodic manual (`leverage_frequency_minutes`, default weekly)
**Code ref**: `high_tide_agent.py:124-180` (`decide_action`), `high_tide_agent.py:249-266` (`_execute_rebalancing`), `high_tide_agent.py:268-378` (`_execute_iterative_rebalancing`)
**Status**: verified (auditor confirmed 2026-02-07)

### High Tide Rebalancing Limitations
**Purpose**: Document constraints (and absence thereof) on rebalancing frequency
**Findings**:
1. **Max 3 sell-repay cycles per minute** — hard cap in iterative loop (`high_tide_agent.py:282`)
2. **Engine gate** — `allow_agent_rebalancing` flag, defaults to `True`; only set to `False` during oracle manipulation window in flash crash tests (`flash_crash_simulation.py:814`)
3. **No YT remaining** — natural exhaustion stops rebalancing
4. **No inter-minute cooldown** — no `last_rebalance_minute` tracking exists (grep confirmed zero matches)
5. **No minimum amount threshold** — any debt reduction > 0 triggers rebalancing
6. **No gas/tx cost simulation** — no on-chain friction modeled
**Implication**: Agent can rebalance every minute indefinitely (up to 525,600×/year, 3 cycles each)
**Status**: evidence-supported (2026-02-07)

### MOET Bond Auction
**Purpose**: Dynamically price bonds to maintain reserve ratio
**Inputs**: Current reserve ratio, target ratio, EMA parameters
**Outputs**: Bond APR
**Core Logic**:
1. Calculate deviation from target reserve ratio
2. Apply EMA smoothing to rate changes
3. Adjust bond APR to incentivize deposits/withdrawals
**Code ref**: `moet.py`
**Status**: unverified

## Assumptions

| Assumption | Basis | Status | Notes |
|------------|-------|--------|-------|
| Liquidation penalty is 5% | Codebase exploration | stated | Needs verification in code |
| Reserve ratio target is 10% | Codebase exploration | stated | Needs verification |
| Simulation runs minute-by-minute | Code trace of engine loop | verified | `high_tide_vault_engine.py:169`; agents decide every minute |
| BTC liquidation threshold is 0.85 | `high_tide_agent.py:487` | verified | Hardcoded in `_calculate_effective_collateral_value` |
| High Tide checks HF every minute | `decide_action` called per minute from engine loop | verified | Structural advantage over AAVE's periodic checks |
| AAVE rebalancing is periodic | `full_year_sim.py:1761-1762` | verified | Controlled by `leverage_frequency_minutes` (default: weekly) |
| AAVE collateral factor inconsistency | `aave_agent.py:120` vs `aave_agent.py:361` | evidence-supported | HF uses 0.85 (`_calculate_effective_collateral_value`) but rebalancing debt target uses 0.80 (`execute_weekly_rebalancing`). Effect: AAVE targets more conservative debt level when deleveraging than its HF formula implies. Possible bug or intentional conservatism — not yet fully analyzed. |

## Code Map

| File | Purpose | Key Functions |
|------|---------|---------------|
| `tidal_protocol_sim/core/protocol.py` | Core lending mechanics | TidalProtocol class |
| `tidal_protocol_sim/core/moet.py` | MOET stablecoin system | Bonder, Redeemer |
| `tidal_protocol_sim/core/uniswap_v3_math.py` | Uniswap V3 calculations | tick_to_price, liquidity calcs |
| `tidal_protocol_sim/core/yield_tokens.py` | Yield token system | YieldToken class |
| `tidal_protocol_sim/engine/high_tide_vault_engine.py` | High Tide simulation | Main engine class |
| `tidal_protocol_sim/engine/tidal_engine.py` | Base Tidal engine | Core simulation loop |
| `tidal_protocol_sim/agents/high_tide_agent.py` | HT strategy agents | Decision algorithms |
| `tidal_protocol_sim/agents/liquidator.py` | Liquidation logic | Liquidation execution |

---

## Verification Queue

Items needing code verification:
1. ~~Health factor formula exact implementation~~ → verified 2026-02-07
2. Liquidation penalty percentage
3. Reserve ratio target value
4. YT value accrual formula
5. Tick-to-price implementation details
