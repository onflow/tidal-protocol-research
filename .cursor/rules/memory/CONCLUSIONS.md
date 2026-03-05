# Audit Conclusions

Last updated: 2026-03-03

## Commit Scope

**Current focus**: `ba544b1` (UnitZero's latest fixes)
**Prior analysis**: `da4cbf9` — detailed findings in `sims-review_commit-da4cbf9/`

---

## Protocol-Level Conclusions (commit-independent)

### Validated

**Core Formulas (2026-02-07)**: Health Factor, Debt Reduction, and High Tide Rebalancing algorithm verified against code.
→ `TECHNICAL.md`

**MOET ≠ $1 USD (2026-02-03)**: `MOET_price = k × geometric_mean(backing_assets)`, not a dollar peg. Codebase had stale $1 assumptions throughout.
→ `sims-review_commit-da4cbf9/MOET_DOLLAR_PEG_INSTANCES.md`

### Evidence-Supported

**Rebalancing has no cooldown, no minimum threshold, no gas costs (2026-02-07)**: Agent can rebalance every minute (525,600×/year, 3 cycles each). Design choice, not a bug per se, but unrealistic.
→ `TECHNICAL.md § High Tide Rebalancing Limitations`

**AAVE collateral factor inconsistency (2026-02-07)**: HF uses 0.85 but rebalancing debt target uses 0.80. More conservative deleveraging than HF implies.
→ `TECHNICAL.md § Assumptions`

---

## Prior Art from da4cbf9

Findings from our analysis of commit `da4cbf9`. Each becomes a zero-hypothesis to verify against `ba544b1`. Full evidence in `sims-review_commit-da4cbf9/` documents.

### Pre-existing bugs (present when Primer was generated — likely persist)

| ID | Finding | da4cbf9 Status | ba544b1 Status | Ref |
|----|---------|---------------|---------------|-----|
| B2 | Flash crash infinite leverage loop — `moet_debt` resets to $0 after borrow | evidence-supported | to-verify | `FLASH_CRASH_SIMULATION_SUMMARY.md` |
| B3 | Uniswap V3 fee bypass — `fee_amount` omitted from `amount_specified_remaining` (`uniswap_v3_math.py:1282`) | evidence-supported | to-verify | `FCM_PRIMER_FIGURE_MAPPING.md §B3` |
| B4 | Triple-recording of rebalancing events — 3 appends per event (engine lines 536, 562, 628) | evidence-supported | to-verify | `FCM_PRIMER_FIGURE_MAPPING.md §B4` |

### Post-delivery changes (introduced after Primer — may be addressed in ba544b1)

| ID | Finding | da4cbf9 Status | ba544b1 Status | Ref |
|----|---------|---------------|---------------|-----|
| D7 | `btc_final_price` changed from 76,342.50 to 90,000 in file move (`684c007`) | evidence-supported | to-verify | `FCM_PRIMER_FIGURE_MAPPING.md §D7` |
| D8 | Snapshot frequency default (1440min) + chart x-axis bug break §4.3 panels | evidence-supported | to-verify | `FCM_PRIMER_FIGURE_MAPPING.md §D8` |
| D9 | Swap formula change (`48a9ff2`): `get_amount0_delta` → `get_amount0_delta_economic`, collapses slippage from ~$2 to ~$0.005 | evidence-supported | to-verify | `FCM_PRIMER_FIGURE_MAPPING.md §D9` |
| F4 | Post-`2fd742d` AAVE liquidation cascading: broken BTC→MOET swap → 3 liquidations/agent ($77k vs $32k) | validated | to-verify | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §F4` |

### Structural / reproduction findings

| ID | Finding | da4cbf9 Status | ba544b1 Status | Ref |
|----|---------|---------------|---------------|-----|
| F2 | AAVE survival rates not reproducible from any tested committed code — HFs deterministic but don't match Primer pattern | validated | to-verify | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §F2` |
| F3 | HT costs ~1.8× lower than Primer at every tested commit | evidence-supported | to-verify | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §F3` |
| F6 | Swapped sim order reduces AAVE survival error: 1/5 runs match exactly (Run 3), others off by 20pp; prior "3/5" claim was based on stale sim values in "Primer" column | validated | verified | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §Attempt 4` |
| — | `cfdbd21` cannot reproduce Primer (wrong config, all post-delivery changes present) | evidence-supported | n/a | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §Avenue 1` |
| — | Discrepancy check false positive in `full_year_sim.py:2951` | validated | to-verify | `DISCREPANCY-ANALYSIS_full_year_sim.md` |
| — | MOET:BTC pool scaling bug — `_initialize_btc_pair_positions` uses raw `total_liquidity*1e6` as L | evidence-supported | to-verify | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md §F4 root cause` |

---

## ba544b1 Findings

### Verified

**All da4cbf9 prior-art findings confirmed at ba544b1 (2026-03-03):** The ba544b1 diff is purely organizational (file moves); no engine, agent, or math files were changed. B2, B3, B4, D7, D8, D9, F4, F6 all persist unchanged. Confirmed by re-running `balanced_scenario_monte_carlo.py` with identical fix set and obtaining identical results.

**Figure 2 Reproduction (2026-03-03):** With 3 fixes (import stub removal, D7 btc_final_price, F4 direct debt repayment) + swapped simulation order: AAVE survival (60%, 40%, 80%, 40%, 60%) vs Primer (40%, 60%, 80%, 60%, 80%). Run 3 matches exactly; others off by 20pp. AAVE costs ~$34.5k vs Primer ~$32.9k (+5% explained by collateral factor 0.85 vs 0.80). Auditor: results "look intuitively better than what is currently in the primer."

### Evidence-Supported
(none yet beyond what's confirmed above)

### Invalidated in ba544b1
(none — UnitZero's changes were purely organizational)

---

## Open Questions

Canonical list lives in `SESSION_LOG.md § Open Questions`. Carried forward from da4cbf9.

| ID | Question | Since | Priority | Commit Scope |
|----|----------|-------|----------|-------------|
| F1 | Algo rebalancer $0 profit on $3.6M volume | 2026-02-27 | Medium | da4cbf9 |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger | 2026-02-27 | Low | da4cbf9 |
| B2 | Flash crash infinite leverage loop | 2026-02-20 | Medium | da4cbf9 |
| F3 | HT cost ~1.8× lower than Primer at every tested commit | 2026-03-02 | Medium | da4cbf9 |

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
| 2026-02-28 | D9 swap formula change | Evidence-supported | git diff, code trace |
| 2026-02-28 | B3 fee bypass | Evidence-supported | git show, Uniswap V3 ref comparison |
| 2026-02-28 | B4 triple-recording | Evidence-supported | Code trace (3 append sites) |
| 2026-03-02 | §4.2 AAVE survival non-reproducible | Validated | 3 reproduction attempts, RNG proof |
| 2026-03-02 | Post-`2fd742d` AAVE liquidation cascading | Validated | CSV comparison, auditor review |
| 2026-03-02b | Swapped order reduces AAVE error 43% | Validated | Attempt 4 run, auditor confirmed |
| 2026-03-02b | `cfdbd21` cannot reproduce Primer | Evidence-supported | File identity check |
| 2026-03-02b | HT sim consumes random draws | Evidence-supported | Engine-only vs full-sim comparison |
| 2026-03-03 | **Commit transition** | Restructured | All da4cbf9 findings → Prior Art; ba544b1 sections created |
| 2026-03-03 | F6 "3/5 match" claim | Corrected | Prior "Primer" column was stale sim values; actual match is 1/5 (Run 3 only) |
| 2026-03-03 | ba544b1 reproduction confirmed | Evidence-supported | Identical results to da4cbf9 Attempt 4; all prior findings persist |
