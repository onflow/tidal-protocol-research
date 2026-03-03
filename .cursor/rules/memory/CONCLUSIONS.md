# Audit Conclusions

Last updated: 2026-03-02

## Validated (auditor confirmed)

### Discrepancy Check Bug (2026-02-06)

**Finding**: `full_year_sim.py:2951` "ACCOUNTING ERROR" is a **false positive**. `total_interest_accrued` never decremented on repayment, so the check formula is wrong. Core sim accounting is correct.
→ `sims-review/DISCREPANCY-ANALYSIS_full_year_sim.md`

### Core Formulas (2026-02-07)

Health Factor, Debt Reduction, and High Tide Rebalancing algorithm verified against code.
→ `TECHNICAL.md` (verified entries)

### §4.2 AAVE survival rates not reproducible at tested code versions (2026-03-02)

AAVE agent initial HFs are deterministic (seed + 10 `random.uniform` calls; HT simulation adds zero random draws). HFs identical at both tested versions (`1c9fce8` and HEAD). Survival pattern at these HFs is (100%, 80%, 20%, 60%, 80%), not Primer's (40%, 60%, 80%, 60%, 80%) — only Runs 4,5 match. The contradictory-threshold argument (no single T satisfies Run 1 and Run 2 simultaneously) holds if the AAVE simulation is deterministic, which code inspection supports but is not exhaustively verified. Untested intermediate commits not fully ruled out. Most likely explanation: uncommitted code.
→ `sims-review/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md` §F2

### Post-`2fd742d` multiple AAVE liquidation events (2026-03-02)

Current engine (post-`2fd742d`) triggers 3 liquidation events per AAVE agent instead of 1 (old engine at `1c9fce8`). Inflates AAVE cost per agent from ~$32k to ~$77k. Root cause: behavioral changes in `2fd742d` (MOET init, leverage throttling, balance deduction).
→ `sims-review/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md` §F4

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

### D9: Post-Primer swap formula change breaks slippage reproduction (2026-02-28)

Commit `48a9ff2` (2025-09-29) replaced `get_amount0_delta` (Q96 integer math, ~0.25% truncation loss) with `get_amount0_delta_economic` (float, near-1:1) for YT→MOET swaps. Primer generated in 4-day window before this change with original formula producing ~$2.14 slippage. Current code produces $0.005. **Post-Primer change — revert to reproduce Primer figures.**
→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` §D9

### B3: Uniswap V3 fee bypass — pre-existing (2026-02-28)

`uniswap_v3_math.py:1282` omits `fee_amount` from `amount_specified_remaining`. Present since swap function creation (pre-`684c007`). Primer generated WITH this bug. Impact masked by integer truncation in original formula. **Pre-existing bug — fix independently of reproduction.**
→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` §B3

### B4: Triple-recording of rebalancing events — pre-existing (2026-02-28)

Each rebalancing appends 3× to `engine.rebalancing_events` (engine lines 536, 562, 628). Present since `684c007`. Event counts and cost sums 3× inflated; per-event stats unaffected. **Pre-existing bug — fix independently of reproduction.**
→ `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` §B4

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
| 2026-02-28 | D9 swap formula change | Evidence-supported | git diff `684c007..48a9ff2`, code trace |
| 2026-02-28 | B3 fee bypass (pre-existing) | Evidence-supported | git show `684c007`, Uniswap V3 ref comparison |
| 2026-02-28 | B4 triple-recording (pre-existing) | Evidence-supported | Code trace (3 append sites at `684c007`) |
| 2026-03-02 | §4.2 AAVE survival non-reproducible | Validated | 3 reproduction attempts, RNG determinism proof, auditor review |
| 2026-03-02 | Post-`2fd742d` multiple AAVE liquidations | Validated | CSV comparison (1 vs 3 events, $32k vs $77k), auditor review |
