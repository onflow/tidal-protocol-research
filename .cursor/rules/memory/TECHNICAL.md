# Technical Domain Knowledge

Last updated: 2026-02-03

## Terminology

| Term | Definition | Source | Status |
|------|------------|--------|--------|
| Health Factor | Ratio of collateral value to debt; <1 triggers liquidation | `protocol.py` | unverified |
| Tri-Health Factor | System with initial, rebalancing, and target HF thresholds | `high_tide_agent.py` | unverified |
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

### Health Factor
- **Expression**: `HF = (collateral × liquidation_threshold) / debt`
- **Variables**:
  - collateral: USD value of deposited assets
  - liquidation_threshold: protocol parameter
  - debt: USD value of borrowed assets
- **Code ref**: `protocol.py`, `base_agent.py`
- **Status**: unverified

## Algorithmic Abstractions

### High Tide Agent Rebalancing
**Purpose**: Maintain health factor within target bounds through leverage adjustment
**Inputs**: Current HF, target HF, rebalancing threshold, position state
**Outputs**: Rebalance action (increase/decrease leverage, swap YT, etc.)
**Core Logic**:
1. Check if HF below rebalancing threshold
2. If below, initiate deleveraging chain: YT → MOET → BTC → Stablecoin
3. If above target with capacity, may increase leverage
4. Execute swaps with slippage awareness
**Code ref**: `high_tide_agent.py`
**Status**: unverified

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
| Simulation runs minute-by-minute | Codebase exploration | stated | Time granularity |

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
1. Health factor formula exact implementation
2. Liquidation penalty percentage
3. Reserve ratio target value
4. YT value accrual formula
5. Tick-to-price implementation details
