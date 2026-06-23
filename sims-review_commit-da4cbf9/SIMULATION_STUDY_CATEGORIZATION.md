# Simulation Study Categorization

**Date**: 2026-02-07  
**Source**: `sim_tests/run_all_studies.py` (10 studies), configs extracted from `run_study_*.py`

---

## Protocol Agent Overview

All 10 studies compare two protocol agents head-to-head on identical BTC price histories. Each agent starts with 1.0 BTC and operates for the study's duration.

### High Tide Agent

**Source**: `tidal_protocol_sim/agents/high_tide_agent.py` (single file)

- **Setup**: Deposits BTC as collateral → borrows MOET → buys Yield Tokens (YT)
- **Decision loop**: `decide_action` (line 124) runs **every simulated minute**
  1. Recalculate HF from current BTC price and debt (`_update_health_factor`, line 462)
  2. If `HF < Rebalancing_HF`: sell YT → repay MOET → reduce leverage (`_execute_rebalancing`, line 249; up to 3 cycles, line 282)
  3. If `HF > Initial_HF` (checked every 10 min): borrow more MOET → buy more YT (`_execute_leverage_increase`, line 225)
  4. If `HF ≤ 1.0`: emergency — sell ALL remaining YT (`_execute_emergency_yield_sale`, line 380)
- **Rebalancing formula**: `Debt_reduction = Debt_current − (BTC_amount × P_BTC × 0.85) / HF_target` (line 255-260)
- **Swap execution**: Uniswap V3 via engine (`high_tide_vault_engine.py:502`)
- **Yield harvesting**: Weekly deleveraging chain (`_check_deleveraging`, line 712)

### AAVE Agent

**Source**: `tidal_protocol_sim/agents/aave_agent.py` (single file), called externally from `sim_tests/full_year_sim.py`

- **Setup**: Deposits BTC as collateral → borrows MOET → buys YT (same as HT)
- **Decision loop**: `decide_action` (line 67) runs every minute but **always returns HOLD**
- **Periodic rebalancing**: `execute_weekly_rebalancing` (line 318) called externally by `full_year_sim.py:1776` at `leverage_frequency_minutes` intervals (default: weekly)
  1. If `HF < Initial_HF × 0.99`: sell YT → MOET → repay debt (max 50% of YT per period, line 368)
  2. If `HF ≥ Initial_HF`: harvest accrued yield only → MOET → BTC → deposit (line 390-433)
- **Liquidation**: `execute_aave_liquidation` (line 159) — 50% debt reduction, BTC seized, 5% bonus
- **Swap execution**: Uniswap V3 (with slippage)
- **Yield harvesting**: Weekly (within periodic rebalancing)


! Caution: an agent is limited to **selling at most 50%** of **YT** per **weekly** intervention! This also prevents the agent from correcting larger displaces before liquidation. Ideally, whether this effect is significant should be empirically studied on the simulated data. 


### Key Structural Differences

| Aspect | High Tide | AAVE |
|--------|-----------|------|
| **Autonomy** | Automatic, internal (protocol-driven) | Manual, external (user-initiated) |
| **HF check frequency** | Every minute | Every `leverage_frequency_minutes` (weekly) |
| **Rebalancing trigger** | `HF < Rebalancing_HF` threshold | Periodic schedule (regardless of HF) |
| **Rebalancing goal** | Restore to `Target_HF` | Restore to `Initial_HF` |
| **Leverage increase** | Automatic when `HF > Initial_HF` (10-min check) | At periodic rebalancing only |
| **Max rebalance cycles** | 3 per minute (hard cap) | 1 per scheduled check |
| **YT sale cap** | Fraction of portfolio per cycle | N/A (no YT concept) |
| **Liquidation** | Emergency sell at HF ≤ 1.0 | Protocol liquidation at HF < 1.0 (5% penalty) |
| **Collateral factor for HF** | 0.85 (liquidation threshold) | 0.85 for HF calc, but 0.80 for debt target in rebalancing (*inconsistency*) |

**Notable**: AAVE's `execute_weekly_rebalancing` (`aave_agent.py:361`) uses a 0.80 collateral factor to compute its debt target, while its `_calculate_effective_collateral_value` (`aave_agent.py:120`) uses 0.85. This means AAVE targets a more conservative debt level when deleveraging than its HF formula implies. Status: *evidence-supported* [AI collected], *not yet fully verified*.

---

## The 10 Studies

- **Study 1 — 2021 Mixed Market, Symmetric**
  - *Setup*: Both protocols use historical AAVE rates (2021). Equal initial HF = 1.3. Single agent. BTC: $29,002 → $46,306 (+59.6%), 365 days.
  - *What it tests*: Baseline HT vs AAVE comparison in a year with both rallies and corrections, under identical rate conditions.

- **Study 2 — 2024 Bull Market, Symmetric (Equal HF)**
  - *Setup*: Both protocols use historical AAVE rates (2024). Equal initial HF = 1.3. Single agent. BTC: $42,208 → $92,627 (+119%), 365 days.
  - *What it tests*: HT vs AAVE in a strong bull market with equal starting risk. Whether HT's automated leverage increase captures more upside.

- **Study 3 — 2024 Capital Efficiency, Symmetric (Divergent HF)**
  - *Setup*: Both protocols use historical AAVE rates (2024). HT at aggressive HF 1.1; AAVE at conservative HF 1.95. Single agent. BTC: $42,208 → $92,627 (+119%), 365 days.
  - *What it tests*: Whether HT's automation allows safe operation at much higher leverage (HF 1.1) vs AAVE's necessarily conservative HF (1.95). Capital efficiency — same collateral, vastly different utilization.

- **Study 4 — 2022 Bear Market, Symmetric**
  - *Setup*: Both protocols use historical AAVE rates (2022). HT starts at HF 1.2 (slightly more aggressive); AAVE at 1.3. Single agent. BTC: $46,320 → $16,604 (−64.2%), 365 days.
  - *What it tests*: Survival and loss mitigation during a severe drawdown. HT starts slightly more aggressive (1.2 vs 1.3). Rebalancing robustness under sustained price decline.

- **Study 5 — 2025 Low Volatility, Symmetric**
  - *Setup*: Both protocols use historical AAVE rates (2025). Equal initial HF = 1.3. Single agent. BTC: $93,508 → $113,321 (+21.2%), 268 days.
  - *What it tests*: Behavior in a calm, mildly bullish market. Fewer rebalancing events expected. Steady-state performance and yield accumulation.

- **Study 6 — 2021 Mixed Market, Asymmetric (Advanced MOET)**
  - *Setup*: HT uses Advanced MOET dynamic rates; AAVE uses historical rates (2021). Equal HF = 1.3. 100 agents. BTC: $29,002 → $46,306 (+59.6%), 365 days.
  - *What it tests*: Same market as Study 1, but HT uses its own dynamic rate mechanism. Multi-agent to capture diversity. Mirrors Study 1.

- **Study 7 — 2024 Bull Market, Asymmetric (Advanced MOET, Equal HF)**
  - *Setup*: HT uses Advanced MOET dynamic rates; AAVE uses historical rates (2024). Equal HF = 1.3. 100 agents. BTC: $42,208 → $92,627 (+119%), 365 days.
  - *What it tests*: Same market as Study 2, now with HT's own rate mechanism. Multi-agent. Mirrors Study 2.

- **Study 8 — 2024 Capital Efficiency, Asymmetric (Advanced MOET, Divergent HF)**
  - *Setup*: HT uses Advanced MOET dynamic rates at aggressive HF 1.1; AAVE uses historical rates at conservative HF 1.95. 100 agents. BTC: $42,208 → $92,627 (+119%), 365 days.
  - *What it tests*: Capital efficiency with HT's own rate mechanism. Mirrors Study 3. The strongest test of HT's core thesis: can automation enable vastly higher utilization safely?

- **Study 9 — 2022 Bear Market, Asymmetric (Advanced MOET)**
  - *Setup*: HT uses Advanced MOET dynamic rates; AAVE uses historical rates (2022). Equal HF = 1.3. 100 agents. BTC: $46,320 → $16,604 (−64.2%), 365 days.
  - *What it tests*: Bear market survival with HT's own rate mechanism. Mirrors Study 4 — but note S9 uses HT Initial HF 1.3 while S4 used 1.2. The bear pair is **not perfectly controlled**.

- **Study 10 — 2025 Low Volatility, Asymmetric (Advanced MOET)**
  - *Setup*: HT uses Advanced MOET dynamic rates; AAVE uses historical rates (2025). Equal HF = 1.3. 50 agents. BTC: $93,508 → $113,321 (+21.2%), 268 days.
  - *What it tests*: Low-volatility performance with HT's own rate mechanism. 50 agents (fewer than other asymmetric studies). Mirrors Study 5.

**Advanced MOET dynamic rates**: When enabled, HT's borrowing rate is `r_MOET = r_floor + r_bond_cost`, where `r_floor` (2%) is a governance-set minimum and `r_bond_cost` is the cost of capital from bond auctions that dynamically price to maintain a 10% reserve ratio (EMA-smoothed, 12h half-life). When disabled, both protocols use the same historical AAVE rates from CSV. Symmetric studies isolate the rebalancing mechanism difference; asymmetric studies test the full protocol difference (mechanism + rate model).


### Configuration Parameter Table

| Parameter | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|-----------|----|----|----|----|----|----|----|----|----|----|
| **Market Year** | 2021 | 2024 | 2024 | 2022 | 2025 | 2021 | 2024 | 2024 | 2022 | 2025 |
| **Market Type** | Mixed | Bull | Bull | Bear | Low Vol | Mixed | Bull | Bull | Bear | Low Vol |
| **BTC Δ** | +59.6% | +119% | +119% | −64.2% | +21.2% | +59.6% | +119% | +119% | −64.2% | +21.2% |
| **use_advanced_moet** | no | no | no | no | no | yes | yes | yes | yes | yes |
| **num_agents** | 1 | 1 | 1 | 1 | 1 | 100 | 100 | 100 | 100 | 50 |
| **agent_initial_hf** | 1.3 | 1.3 | 1.1 | 1.2 | 1.3 | 1.3 | 1.3 | 1.1 | 1.3 | 1.3 |
| **agent_rebalancing_hf** | 1.1 | 1.1 | 1.025 | 1.1 | 1.1 | 1.1 | 1.1 | 1.025 | 1.1 | 1.1 |
| **agent_target_hf** | 1.2 | 1.2 | 1.04 | 1.15 | 1.2 | 1.2 | 1.2 | 1.04 | 1.2 | 1.2 |
| **aave_initial_hf** | 1.3 | 1.3 | 1.95 | 1.3 | 1.3 | 1.3 | 1.3 | 1.95 | 1.3 | 1.3 |
| **sim_duration_days** | 365 | 365 | 365 | 365 | 268 | 365 | 365 | 365 | 365 | 268 |
| **Mirrors** | — | — | — | — | — | S1 | S2 | S3 | S4* | S5 |

\* Bear pair not perfectly controlled: S4 uses HT Initial HF 1.2 / Target 1.15; S9 uses 1.3 / 1.2.

---

## Categorization Axes

### Axis 1: Rate Mechanism (Symmetric vs Asymmetric)

| Symmetric (Studies 1–5) | Asymmetric (Studies 6–10) |
|--------------------------|---------------------------|
| `use_advanced_moet = False` | `use_advanced_moet = True` |
| Both HT and AAVE use historical AAVE rates | HT uses Advanced MOET dynamic rates; AAVE uses historical rates |
| **1 agent** per protocol | **100 agents** (50 for Study 10) |

Each asymmetric study mirrors a symmetric study with the same market year.


### Axis 2: Market Regime (BTC Price History)

| Regime | Year | BTC Performance | Symmetric | Asymmetric |
|--------|------|-----------------|-----------|------------|
| Mixed | 2021 | +59.6% | Study 1 | Study 6 |
| Bull | 2024 | +119% | Study 2 | Study 7 |
| Bear | 2022 | −64.2% | Study 4 | Study 9 |
| Low Vol | 2025 | +21.2% (268 days) | Study 5 | Study 10 |

Studies 3 and 8 also use 2024 bull data but with different HF parameters (see Axis 3).

### Axis 3: Health Factor Profile

| Profile | HT Initial | HT Rebal | HT Target | AAVE Initial | Studies |
|---------|-----------|----------|-----------|-------------|---------|
| **Equal HF** | 1.3 | 1.1 | 1.2 | 1.3 | 1, 2, 5, 6, 7, 9, 10 |
| **Bear (slight divergence)** | 1.2 | 1.1 | 1.15 | 1.3 | 4 |
| **Capital Efficiency** | 1.1 | 1.025 | 1.04 | 1.95 | 3, 8 |

The Capital Efficiency studies (3, 8) are the only ones where HT and AAVE start at **different** initial HFs.

---

## Study Pairing Map

```
Market Regime        Symmetric    Asymmetric    HF Profile
─────────────────    ─────────    ──────────    ──────────
2021 Mixed           Study 1   ↔  Study 6      Equal (1.3)
2024 Bull            Study 2   ↔  Study 7      Equal (1.3)
2024 Capital Eff.    Study 3   ↔  Study 8      Divergent (1.1 vs 1.95)
2022 Bear            Study 4   ↔  Study 9      Equal* (1.2/1.3 vs 1.3/1.3)
2025 Low Vol         Study 5   ↔  Study 10     Equal (1.3)
```

*Note: Study 4 (bear symmetric) uses HT Initial HF = 1.2 while Study 9 (bear asymmetric) uses 1.3 — so the bear pair is not perfectly controlled. Study 4 also uses a different target HF (1.15 vs 1.2).

---

## Constant Across All Studies

| Parameter | Value |
|-----------|-------|
| Initial BTC per agent | 1.0 BTC |
| AAVE rebalancing frequency | Weekly (10,080 min) |
| Weekly yield harvest | Enabled |
| Historical BTC prices | Yes |
| Historical AAVE rates | Yes (as base; overridden by MOET in asymmetric) |
| Ecosystem growth | Disabled |
| Comparison mode (both protocols) | Yes |

---

## Notable Observations

1. **Agent count disparity**: Symmetric studies use 1 agent; asymmetric use 100 (50 for S10). Asymmetric studies capture agent diversity effects that symmetric studies cannot.
2. **Bear pair inconsistency**: Study 4 and Study 9 are not perfectly paired — S4 uses HT Initial HF 1.2 while S9 uses 1.3; S4 also uses target HF 1.15 vs 1.2 in S9.
3. **Capital Efficiency is the only divergent-HF test**: Studies 3 and 8 are the only ones testing whether HT can safely run at much lower HF (1.1) than AAVE (1.95).
4. **Low Vol studies are shorter**: 268 days vs 365 for all others (partial 2025 data).
5. **All studies use weekly AAVE rebalancing**: `leverage_frequency_minutes = 10080` throughout.
6. **AAVE collateral factor inconsistency**: `aave_agent.py:361` uses 0.80 for debt target while `aave_agent.py:120` uses 0.85 for HF. Effect not yet fully analyzed.
