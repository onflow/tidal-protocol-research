# Audit Conclusions

Last updated: 2026-02-06

## Validated

### Discrepancy Check Bug (2026-02-06)

**Finding**: The "ACCOUNTING ERROR DETECTED!" in `full_year_sim.py` (lines 2951-2956) is a **false positive** caused by a flawed formula.

**Formula bug**: `debt - total_interest_accrued` does NOT equal remaining principal after debt repayments, because `total_interest_accrued` is never decremented when debt is repaid.

**Evidence**:
- Grep confirms `total_interest_accrued` is never decremented
- Code trace shows debt repayment only modifies `moet_debt`
- Mathematical proof via worked example

**Impact**: Informational only. Core simulation accounting is correct.

**Details**: See `sims-review/DISCREPANCY_CHECK_BUG_ANALYSIS.md`

## Invalidated

*None yet - prior beliefs that are corrected will be logged here.*

## Open Questions

| Question | Current Hypothesis | Blocking On | Priority |
|----------|-------------------|-------------|----------|
| Is the tri-health factor system mathematically sound? | Likely yes, given simulation results | Code review of thresholds | High |
| Does MOET maintain peg under stress scenarios? | Appears to, per stress tests | Review of arbitrage mechanisms | High |
| Are liquidation cascades properly bounded? | Unknown | Review of capacity calculations | High |
| Is Uniswap V3 math implementation correct? | Assumed yes | Verify against spec | Medium |

## Hypotheses Under Investigation

| Hypothesis | Evidence For | Evidence Against | Status |
|------------|--------------|------------------|--------|
| *None yet* | | | |

---

## Conclusion Change Log

| Date | Item | Change | Evidence |
|------|------|--------|----------|
| 2026-02-03 | (file) | Initial creation | System bootstrap |
| 2026-02-06 | Discrepancy Check | Validated as bug in check logic | Code trace, grep, mathematical proof |
