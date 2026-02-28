# Session Log

Technical insights, artifacts, bugs, open questions. Snippets over prose; cross-reference artifacts instead of duplicating content.

## Audit State (living summary — update each session)

**Phase:** Reproducibility assessment of FCM Primer §4 claims via source simulation scripts.

**Covered so far:**
- All 8 Primer §4 figures mapped to source scripts → `FCM_PRIMER_FIGURE_MAPPING.md`
- All sim scripts catalogued by runnability → `RUNNABILITY_AUDIT.md`
- `hourly_test_with_rebalancer.py` executed (modes 1 + 3), partial reproduction (3/6 panels match)
- `balanced_scenario_monte_carlo.py` executed (after import fix), reproduction fails due to post-delivery config change
- Flash crash simulation analyzed (not executed to completion — B2 leverage loop blocks)
- Core formulas verified: Health Factor, Debt Reduction, Rebalancing algorithm

**Key audit artifacts:** `sims-review/` — `FCM_PRIMER_FIGURE_MAPPING.md`, `RUNNABILITY_AUDIT.md`, `POOL_REBALANCER_36H_COMPARISON.md`, `FLASH_CRASH_SIMULATION_SUMMARY.md`, `DISCREPANCY_CHECK_BUG_ANALYSIS.md`, `MOET_DOLLAR_PEG_INSTANCES.md`

**Natural next steps:**
- Fix D8 (snapshot frequency + chart x-axis) and re-run `hourly_test_with_rebalancer.py` for full §4.3 reproduction
- Revert D7 config and re-run `balanced_scenario_monte_carlo.py` for §4.2 reproduction
- Fix `comprehensive_ht_vs_aave_analysis.py` import and test Figure 5
- Resolve open questions F1 (algo profit), F2 (ALM off-by-one), B2 (leverage loop)

---

## 2026-02-03: System Genesis

Memory system created. Codebase overview: lending protocol + MOET stablecoin + High Tide yield vaults + Uniswap V3 + agent-based sim + stress testing.

MOET pricing corrected: ≠ $1 peg; correct is `MOET_price = k × geometric_mean(backing_assets)`.
→ `sims-review/MOET_DOLLAR_PEG_INSTANCES.md`, `TECHNICAL.md` updated

---

## 2026-02-06: Discrepancy Check Bug — verified

`full_year_sim.py:2951` false "ACCOUNTING ERROR" ($541.96). Root cause: `total_interest_accrued` never decremented on debt repayment. Sim accounting correct; check flawed.
→ `sims-review/DISCREPANCY_CHECK_BUG_ANALYSIS.md`

---

## 2026-02-07: Process Correction — Validation Gate

Committed finding without auditor sign-off. Fixed: validation gate added to `00-memory-system.mdc` and `01-audit-interaction.mdc`.

---

## 2026-02-20: Pool Rebalancer & FCM Primer Mapping

→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` — all 8 FCM Primer §4 figures mapped to source scripts
→ `sims-review/RUNNABILITY_AUDIT.md` — all sim scripts catalogued by runnability
Ran `hourly_test_with_rebalancer.py` mode 3 (arb delay) — first audit execution

---

## 2026-02-20: Flash Crash Simulation Analysis

→ `sims-review/FLASH_CRASH_SIMULATION_SUMMARY.md`

**Key insights**:
- Single compound scenario (YT+BTC crash), 3 severity levels, 150 agents/$20M, 2-day sim
- Liquidity evaporation modeled *exogenously* (predetermined throttling, not realized P&L)
- Arbitrageurs: 2 stylized agents (ALM 12h + Algo 25bps); fixed capital, no strategic behavior
- **Asymmetric Algo treatment**: full power during crash, throttled during recovery

**Bugs found**:
- B1: `oracle_outlier_magnitude` — stale reference. Fixed → `oracle_volatility` + `yt_wick_magnitude`
- B2: Infinite leverage loop at min 920 — `moet_debt` resets to $0 after borrow. **Open**.

---

## 2026-02-27: Pool Rebalancer Comparison

Ran mode 1 (no arb delay), compared with mode 3 run.
→ `sims-review/POOL_REBALANCER_36H_COMPARISON.md`

**Bugs/findings**:
- `enable_arb_delay` prompt missing `else` branch — mode 1 always ran with delay. Fixed.
- Arb delay: frozen acquisition-time price for settlement (no market risk during hold)
- **F1**: Algo rebalancer $0 profit on $3.6M volume — open
- **F2**: off-by-one in `range(2160)` prevents 3rd ALM trigger — open
- `reports/High_Tide_Capacity_Study_w_Arbing.md` stale (HF 1.25 vs code's 1.1)

---

## 2026-02-27: Figure 2 Reproduction Failure — Root Cause Identified

Ran `balanced_scenario_monte_carlo.py` (after import fix). Result: 100/100% survival, ~$0 costs — completely divergent from Primer claims.

**Root cause:** Commit `684c007` (2025-09-25) changed `btc_final_price` from `76_342.50` (−23.66%) to `90_000.0` (−10%) during file move. Same commit deleted `target_health_factor_analysis.py`, breaking imports. Comment falsely claims "25.00% decline."

**Impact:** All §4.2 headline claims non-reproducible from committed code.
→ `FCM_PRIMER_FIGURE_MAPPING.md` updated: D7, D4 resolved, Reproducibility Status table added.

**Also found (D8):** §4.3 time-series panels fail due to: (1) engine defaulting `agent_snapshot_frequency_minutes = 1440` for a 36h sim, (2) chart code using enumerate index instead of snapshot's minute field.
Git origin: commit `2fd742d` (2025-09-26) introduced the 1440 gate + bundled substantive agent behavioral changes under message "updates."

---

## 2026-02-27: Pattern Extraction — Simulation Reproduction Debugging

6-step debugging pattern extracted from FCM Primer reproduction failures → `WORKING_STYLE.md § Simulation Reproduction Debugging`.
Concrete examples: `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` (D6–D8).

Also: WORKING_STYLE.md compacted — removed directions that duplicate always-applied rules, consolidated communication directions, tightened structure.

---

## 2026-02-27: Memory System Iteration

Three changes from self-evaluation:
1. Added "Audit State" living summary to top of SESSION_LOG — reduces session-start orientation time
2. Brought CONCLUSIONS.md current — added "Evidence-Supported" tier, populated with D7/D8/rebalancing-limits/AAVE-collateral findings, refreshed open questions
3. Added "Principles over recollections" rule to `00-memory-system.mdc § How to Update` — directions should state general principles, not specific cases that motivated them
4. Made Active Retrieval in `00-memory-system.mdc` more specific (numbered checklist of what to read at session start)

---

## Open Questions (cross-session)

| ID | Question | Since | Refs |
|----|----------|-------|------|
| F1 | Algo rebalancer $0 profit on $3.6M volume — accounting bug or design? | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger never fires | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| B2 | Flash crash infinite leverage loop — `moet_debt` reset root cause | 2026-02-20 | `FLASH_CRASH_SIMULATION_SUMMARY.md` |
