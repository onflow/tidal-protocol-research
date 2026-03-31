# FCM Position Maintenance — Cost Estimate Framework

## 1. Objective

Quantify the total number of on-chain **Flow transactions** FCM's automated position manager executes to maintain a single leveraged BTC position over the 2022 bear market year (BTC $46k → $17k, −64%, 365 days), so that a dollar cost can be computed once per-transaction compute costs are provided.

---

## 2. Execution Model — FlowActions

FCM uses [FlowActions](https://github.com/onflow/FlowActions), a system of composable on-chain DeFi primitives built on Flow. The key architectural property is **atomic bundling**: all steps within a single rebalance event are composed into one Flow transaction and either complete entirely or revert together. There is no separate per-step transaction cost.

This means FCM's cost is expressed in **transactions**, not individual steps. There are exactly three transaction types:

| Transaction Type | Triggered when | Contains |
|-----------------|---------------|----------|
| **HC** — Health Check | Hourly, always | Oracle price read + HF evaluation |
| **SR** — Safety Rebalance | HC finds HF < safety threshold | Source withdrawal + YT→MOET swap + debt repayment (bundled) |
| **ER** — Efficiency Rebalance | HC finds HF > efficiency threshold | MOET borrow + Sink deposit + MOET→YT swap (bundled, including ER-3) |

When a rebalance is triggered, the HC and the rebalance execute as a single transaction (the health check is the trigger condition, not a separate round-trip). So there is no "HC + SR" double-count: a triggered check costs one SR transaction, not one HC plus one SR.

---

## 3. The Two Cost Components

### Component A — Baseline cost (no rebalancing needed)

Over 365 days at hourly checks: **8,760 HC transactions maximum**. For checks where HF is within the valid band, the HC is the only transaction. This is the cost floor — the minimum a user pays for having their position managed by FCM.

### Component B — Active maintenance cost

When HF falls outside the valid band, the HC escalates to a SR or ER transaction instead. The total transaction count is:

```
N_total = N_HC_no_action + N_SR + N_ER
```

Where `N_HC_no_action + N_SR + N_ER = 8,760` (every hourly slot produces exactly one transaction of some type).

---

## 4. Rebalancing Flows

### 4.1 Safety Rebalance (SR) — HF too low → deleverage

Triggered when BTC price has fallen enough that HF drops below the safety threshold. FCM reduces debt by converting Yield Token holdings back to MOET.

```
FCM detects: HF < rebalancing_hf (1.1)

One atomic Flow transaction bundles:
  SR-1  Pull YT from Source          (VaultSource.withdrawAvailable)
  SR-2  Swap YT → MOET               (Swapper.swap via Uniswap V3)
  SR-3  Repay MOET debt               (lending protocol repay call)
```

### 4.2 Efficiency Rebalance (ER) — HF too high → leverage up

Triggered when BTC price has risen, leaving excess collateral capacity. FCM borrows more MOET and deploys it into additional Yield Token exposure.

```
FCM detects: HF > initial_hf (1.5)

One atomic Flow transaction bundles:
  ER-1  Borrow additional MOET        (lending protocol borrow call)
  ER-2  Push MOET to Sink             (VaultSink.deposit)
  ER-3  Sink swaps MOET → YT          (internal to Sink — bundled with ER-2)
```

Both SR and ER are each exactly **1 Flow transaction**.

---

## 5. Cost Formula

```
Total Cost = N_HC_no_action × cost_HC
           + N_SR           × cost_SR
           + N_ER           × cost_ER
```

| Variable | Meaning | Source |
|----------|---------|--------|
| `N_HC_no_action` | Hourly checks where no rebalance was needed | Simulation output |
| `N_SR` | Safety rebalances executed (1 per trigger, max 1 cycle) | Simulation output |
| `N_ER` | Efficiency rebalances executed (1 per trigger, max 1 cycle) | Simulation output |
| `cost_HC` | Compute units for a health-check-only transaction | To be provided |
| `cost_SR` | Compute units for a safety rebalance transaction | To be provided |
| `cost_ER` | Compute units for an efficiency rebalance transaction | To be provided |

Once compute unit rates are provided, total USD cost = `Total_compute_units × cost_per_compute_unit`.

---

## 6. Known Exclusions

### `_check_deleveraging` (Weekly Profit Harvest)

The High Tide agent includes a `_check_deleveraging` action: when HF > `initial_hf`, the agent sells rebased YT gains back to MOET and repays a portion of debt (weekly harvest of yield token appreciation). This is **disabled for this cost estimate**.

**Why excluded**: `_check_deleveraging` maps to a distinct fourth transaction type — call it **DR (Deleverage/Harvest)** — that fires on a time schedule (weekly) rather than in response to HF threshold crossings. Including it would require a separate cost input (`cost_DR`) and complicates the first cost measurement. The SR/ER/HC triangle is the core FCM position maintenance cost.

**Future work**: Add DR as a fourth transaction type. Count weekly harvest events over 2022, obtain `cost_DR` compute units, and include `N_DR × cost_DR` in the total cost formula.

---

## 7. Required Simulation Changes

Two changes to `tidal_protocol_sim/agents/high_tide_agent.py` are required to match FCM's implementation before running the cost estimate:

### Change 1 — Health check frequency: every minute → every hour

**Current:** `decide_action` is called every simulation minute.
**Required:** FCM checks hourly. Gate all decision logic to hourly boundaries.

```python
# At the top of decide_action(), before any HF evaluation:
if current_minute % 60 != 0:
    return (AgentAction.HOLD, {})
```

This also applies to the efficiency-threshold check, which currently runs every 10 minutes (`current_minute % 10 == 0`) and must move to the same hourly gate.

### Change 2 — Max rebalancing cycles per trigger: 3 → 1

**Current:** `_execute_iterative_rebalancing` loops up to 3 sell-repay cycles per trigger.
**Required:** FCM executes exactly one rebalancing pass per trigger (one atomic transaction).

```python
# Line 282 in _execute_iterative_rebalancing:
# Change:   rebalance_cycle < 3
# To:       rebalance_cycle < 1
```

---

## 8. Simulation Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Year | 2022 | BTC $46k → $17k, −64%, 365 days |
| Study | S4 (2022 bear, symmetric) | Symmetric: both HT and AAVE use historical AAVE rates |
| Agents | 1 HT agent | Single position |
| Initial HF / ER trigger (`initial_hf`) | 1.5 | `maxHealth` in FlowCreditMarket.cdc |
| Safety threshold / SR trigger (`rebalancing_hf`) | 1.1 | `minHealth` in FlowCreditMarket.cdc |
| Target HF post-rebalance (`target_hf`) | 1.3 | `targetHealth` in FlowCreditMarket.cdc |
| Health check frequency | Hourly (`% 60 == 0`) | **Changed** |
| Max rebalancing cycles | 1 | **Changed** |
| BTC price oracle | Historical 2022 daily data, interpolated to minute level | |

---

## 9. Simulation Output Required

The simulation reports the following counts for the single HT agent over the full 2022 year:

```
# Transaction counts (the cost inputs)
N_HC_no_action:   int    # Hourly checks where HF was within valid band → HC transaction
N_SR:             int    # Hourly checks that triggered a safety rebalance → SR transaction
N_ER:             int    # Hourly checks that triggered an efficiency rebalance → ER transaction
N_total:          int    # = N_HC_no_action + N_SR + N_ER (≤ 8,760)

# Validation outputs
liquidation_events:         int    # Must be 0 — position should never be liquidated
final_hf:                   float  # Health factor at Dec 31, 2022
btc_collateral_remaining:   float  # BTC remaining after year of rebalancing
moet_debt_remaining:        float  # MOET debt at year end
```

---

## 10. FlowActions Architecture Notes

From the [FlowActions repository](https://github.com/onflow/FlowActions):

- **Source** (`VaultSource`): Withdraws tokens above a minimum balance threshold — used in SR-1
- **Sink** (`VaultSink`): Deposits tokens up to a maximum balance threshold — used in ER-2/ER-3
- **Swapper**: Exchanges one token for another; supports single-path and sequential routing — used in SR-2
- **AutoBalancer**: The orchestrating resource that detects thresholds and composes Source/Swapper/Sink into a single atomic execution — the FCM controller
- **PriceOracle**: Provides real-time asset pricing used in HF evaluation — used in HC

All composition happens inside one Cadence transaction's `execute` phase. The inclusion fee is fixed (0.0001 FLOW) per transaction; execution cost scales with code path complexity (compute units).

> ⚠️ FlowActions is currently in beta. Interfaces are subject to change and production deployment is not yet recommended by the repository.

---

## 11. How to Reproduce

All scripts live in `sim_tests/`. Run them from the repository root.

### Step 1 — Install dependencies

```bash
pip3 install -r requirements.txt
```

### Step 2 — Run the simulation

```bash
python3 sim_tests/run_cost_estimate_2022.py
```

Runs a single High Tide agent over the full 2022 year with FCM's exact operational constraints (hourly checks, max 1 rebalance cycle per trigger, `_check_deleveraging` disabled). Produces:

| Output file | Contents |
|-------------|----------|
| `tidal_protocol_sim/results/FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3/fcm_rebalance_detail_report.csv` | Per-event log: type, day, hour, BTC price, % price change from previous event, HF before and immediately after rebalance |
| `.../fcm_hf_history.csv` | HF at every hourly health-check slot (HC, SR, ER, SR_after, ER_after) — ~8,770 rows |

### Step 3 — Generate visualization figures

```bash
python3 sim_tests/plot_cost_estimate_report.py
```

Reads both CSVs and writes two figures to the results folder:

| Figure | Contents |
|--------|----------|
| `fig1_rebalance_dashboard.png` | Top: 2022 BTC price with SR/ER event markers. Bottom: continuous HF line at every hourly check with arrows showing threshold → restored HF at each rebalance event |
| `fig2_event_analytics.png` | TL: monthly SR/ER event counts. TR: % BTC price change distribution by rebalance type. BL: rebalance transition bar chart (ER→SR, ER→ER, SR→SR, SR→ER). BR: HF-at-trigger distribution with broken y-axis (ER near 1.5, SR near 1.1) and 90th/10th percentile lines |

### Step 4 — Generate cost estimate table

```bash
python3 sim_tests/generate_cost_table.py
```

Reads `fcm_hf_history.csv`, applies the cost formula, and writes:

| Output file | Contents |
|-------------|----------|
| `fcm_cost_estimate_table.csv` | Machine-readable cost table with symbolic unit costs (c_hc, c_sr, c_er) |
| `fig3_cost_estimate_table.png` | Formatted table figure showing counts, unit cost placeholders, and both cost formula variants |

---

## 12. Simulation Results — 2022 Bear Market

Configuration: HF thresholds 1.5 / 1.1 / 1.3 (ER trigger / SR trigger / target), hourly checks, max 1 rebalance cycle per trigger, `_check_deleveraging` disabled.

### Transaction counts

| Transaction | Count | Description |
|-------------|-------|-------------|
| HC — health check, no action | 8,748 | HF within valid band (1.1 – 1.5) |
| SR — safety rebalance | 8 | HF dropped below 1.1 (BTC price fell ~15% between events) |
| ER — efficiency rebalance | 3 | HF rose above 1.5 (BTC price rose ~16% between events) |
| **Total** | **8,759** | ≤ 8,760 hourly slots in 365 days |

### Cost formula (fill in compute unit costs to get USD total)

```
Health Check Cost    = 8,748 × c_hc
Total Rebalance Cost = 8,748 × c_hc  +  8 × c_sr  +  3 × c_er
```

### Validation

| Metric | Value | Requirement |
|--------|-------|-------------|
| Liquidation events | 0 | Must be 0 ✓ |
| Survived full year | True | ✓ |
| Final HF (Dec 31) | 1.228 | Within valid band ✓ |
| BTC collateral remaining | 1.000000 BTC | No collateral consumed ✓ |
| MOET debt remaining | $11,493.34 | — |

### Observed rebalance pattern

- Each SR was triggered by a BTC price drop of approximately **−14.3% to −15.3%** from the previous event.
- Each ER was triggered by a BTC price rise of approximately **+16.3% to +16.5%** from the previous event.
- After every rebalance (SR or ER), HF was restored to the target of **1.3**. SR events achieved ≈1.29 (one-cycle limit) and ER events achieved exactly 1.3 (borrow amount is computed precisely).
- The most active period was **Days 163–168** (mid-June 2022), where BTC fell from ~$28k to ~$20k in rapid succession, triggering 4 SR events in 5 days.
