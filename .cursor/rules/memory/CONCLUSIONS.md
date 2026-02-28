# Audit Conclusions

Last updated: 2026-02-27

## Validated (auditor confirmed)

### Discrepancy Check Bug (2026-02-06)

**Finding**: `full_year_sim.py:2951` "ACCOUNTING ERROR" is a **false positive**. `total_interest_accrued` never decremented on repayment, so the check formula is wrong. Core sim accounting is correct.
→ `sims-review/DISCREPANCY_CHECK_BUG_ANALYSIS.md`

### Core Formulas (2026-02-07)

Health Factor, Debt Reduction, and High Tide Rebalancing algorithm verified against code.
→ `TECHNICAL.md` (verified entries)

## Evidence-Supported (strong code evidence, not yet presented for auditor confirmation)

### D7: Post-delivery config change breaks §4.2 results (2026-02-27)

Commit `684c007` changed `btc_final_price` from `76_342.50` to `90_000.0` while moving file. All §4.2 headline claims (100% vs 64% survival, 99.8% cost reduction) non-reproducible from committed code.
→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` §D7

### D8: Snapshot frequency + chart bugs break §4.3 time-series (2026-02-27)

Engine defaults `agent_snapshot_frequency_minutes = 1440`; chart uses enumerate index instead of minute field. Three of six §4.3 panels unrecognizable vs Primer.
→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` §D8

### Rebalancing Limitations (2026-02-07)

No inter-minute cooldown, no minimum threshold, no gas costs. Agent can rebalance every minute (525,600×/year, 3 cycles each).
→ `TECHNICAL.md` §High Tide Rebalancing Limitations

### AAVE Collateral Factor Inconsistency (2026-02-07)

HF formula uses 0.85 but rebalancing debt target uses 0.80. Effect: AAVE targets more conservative debt when deleveraging than its HF implies.
→ `TECHNICAL.md` §Assumptions

## Invalidated

### MOET $1 USD Peg (2026-02-03)

Codebase assumed $1 peg throughout. Correct: `MOET_price = k × geometric_mean(backing_assets)`.
→ `sims-review/MOET_DOLLAR_PEG_INSTANCES.md`

## Open Questions

Canonical list lives in `SESSION_LOG.md § Open Questions`. Summary:

| ID | Question | Priority |
|----|----------|----------|
| F1 | Algo rebalancer $0 profit on $3.6M volume | Medium |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger | Low |
| B2 | Flash crash infinite leverage loop | Medium |

## Conclusion Change Log

| Date | Item | Change | Evidence |
|------|------|--------|----------|
| 2026-02-03 | MOET $1 peg | Invalidated | Auditor correction |
| 2026-02-06 | Discrepancy Check | Validated | Code trace, grep, mathematical proof |
| 2026-02-07 | Core formulas | Validated | Code trace, auditor confirmed |
| 2026-02-07 | Rebalancing limits | Evidence-supported | Grep + code trace |
| 2026-02-07 | AAVE collateral inconsistency | Evidence-supported | Code trace |
| 2026-02-27 | D7 config change | Evidence-supported | git diff, reproduction run |
| 2026-02-27 | D8 snapshot bugs | Evidence-supported | Code trace, reproduction run |
