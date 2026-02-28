# Session Log

Technical insights, artifacts, bugs, open questions. Snippets over prose; cross-reference artifacts instead of duplicating content.

---

## 2026-02-03: System Genesis

Memory system created. Architecture: file-based Markdown in `.cursor/rules/memory/`, four-level hierarchy, recursive self-evolution.

Files: `00-memory-system.mdc`, `01-audit-interaction.mdc`, `02-technical-domain.mdc`, `WORKING_STYLE.md`, `TECHNICAL.md`, `CONCLUSIONS.md`, `SESSION_LOG.md`

Codebase overview: lending protocol + MOET stablecoin + High Tide yield vaults + Uniswap V3 + agent-based sim + stress testing. Seven abstraction targets identified → see `02-technical-domain.mdc`.

---

## 2026-02-03: MOET Pricing Correction

MOET ≠ $1 USD peg. Correct: `MOET_price = k × geometric_mean(backing_assets)`. Codebase has stale $1 assumptions throughout.
→ Created `sims-review/MOET_DOLLAR_PEG_INSTANCES.md` (tracking file)
→ `TECHNICAL.md`: $1 peg marked **invalidated**

---

## 2026-02-06: Discrepancy Check Bug

`full_year_sim.py:2951` reports false "ACCOUNTING ERROR" ($541.96). Root cause: `total_interest_accrued` never decremented on debt repayment, so `debt - total_interest_accrued ≠ remaining principal` after any repayment. **Simulation accounting is correct; only the check is flawed.**
→ `sims-review/DISCREPANCY_CHECK_BUG_ANALYSIS.md` — status: **verified**

---

## 2026-02-07: Process Correction — Validation Gate

Committed finding to CONCLUSIONS.md without auditor sign-off. Gap: `00-memory-system.mdc` triggers didn't require confirmation; `01-audit-interaction.mdc` did. Fixed: added validation gate to both rule files, added self-evaluation trigger for process failures.

---

## 2026-02-20: Pool Rebalancer & FCM Primer Mapping

→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` — all 8 FCM Primer §4 figures mapped to source scripts
→ `sims-review/RUNNABILITY_AUDIT.md` — all sim scripts catalogued by runnability
Ran `hourly_test_with_rebalancer.py` mode 3 (arb delay) — first audit execution

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

Extracted: "Simulation Execution" directions (5) → `WORKING_STYLE.md`

---

## 2026-02-20: Flash Crash Simulation Analysis

→ `sims-review/FLASH_CRASH_SIMULATION_SUMMARY.md` — full summary with code refs

**Key insights**:
- Single compound scenario (YT+BTC crash), 3 severity levels, 150 agents/$20M, 2-day sim. Protocol resilience test, not HT-vs-AAVE comparison.
- Liquidity evaporation modeled *exogenously* (predetermined throttling curve on rebalancers, not driven by realized P&L). The liquidity drop is an assumption, not a result.
- Arbitrageurs modeled as 2 stylized agents: `ALMRebalancer` (12h schedule) + `AlgoRebalancer` (25bps threshold). Simplifications: fixed capital, frictionless exit, no strategic behavior, no competition.
- **Asymmetric Algo treatment**: full power during crash (drives pool down toward manipulated oracle), throttled during recovery (can't push back up). Deliberate worst-case design.

**Bugs found**:
- B1: `oracle_outlier_magnitude` — stale reference, never implemented. Script unrunnable as received. Fixed → `oracle_volatility` + `yt_wick_magnitude`.
- B2: Infinite leverage loop at min 920 — `moet_debt` resets to $0 after borrow, `HF=inf` re-triggers leverage. Pool drained → `ValueError`. Root cause: likely `protocol.borrow()` not persisting debt under advanced MOET system. **Open**.

**Patterns extracted**:
- Self-contained docs: ground domain terms in general concepts; back claims inline → `WORKING_STYLE.md`
- 3+ iteration signal → extract pattern proactively → `WORKING_STYLE.md` + `00-memory-system.mdc`

**System evolution**: Refined SESSION_LOG purpose, added update triggers, added active retrieval directive, compacted this file.

---

## 2026-02-27: Figure 2 Reproduction Failure — Root Cause Identified

Ran `balanced_scenario_monte_carlo.py` (after import fix). Result: 100/100% survival, ~$0 costs for both HT and AAVE — completely divergent from Primer's image17 (100% vs 64%, $22 vs $32k).

**Root cause:** Commit `684c007` (2025-09-25, contractor `ibcflan`) changed `btc_final_price` from `76_342.50` (−23.66%) to `90_000.0` (−10%) while moving file to `sim_tests/`. Same commit deleted `target_health_factor_analysis.py`, breaking imports. Comment falsely claims "25.00% decline." This is a single-line diff — no other config changes.

**Impact:** All §4.2 headline claims (99.8% cost reduction, 100% vs 64% survival) are non-reproducible from committed code.
→ Updated `FCM_PRIMER_FIGURE_MAPPING.md`: added D7, resolved D4, added Reproducibility Status table.

---

## Open Questions (cross-session)

| ID | Question | Since | Refs |
|----|----------|-------|------|
| F1 | Algo rebalancer $0 profit on $3.6M volume — accounting bug or design? | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger never fires | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| B2 | Flash crash infinite leverage loop — `moet_debt` reset root cause | 2026-02-20 | `FLASH_CRASH_SIMULATION_SUMMARY.md` |

## System Evolution Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-02-03 | Initial system creation | Bootstrap |
| 2026-02-06 | First validated finding | Discrepancy check bug → CONCLUSIONS.md |
| 2026-02-07 | Validation gate added | Process correction: need auditor sign-off |
| 2026-02-20 | SESSION_LOG compacted | Entropy management: snippets over prose, refs over copies |
| 2026-02-20 | Active retrieval + format directives | Memory must be proactively consulted, not just passively available |
