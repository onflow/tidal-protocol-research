# Discrepancy Check Bug Analysis

**Date**: 2026-02-06  
**Status**: Confirmed bug in check logic (not in simulation accounting)

---

## Summary

The "ACCOUNTING ERROR DETECTED!" message in the simulation output is a **false positive** caused by a flawed formula in the discrepancy check, not by actual accounting errors in the simulation.

---

## The Check Under Analysis

**Location**: `sim_tests/full_year_sim.py`, lines 2951-2956

```python
discrepancy = yt_portfolio.get('total_initial_value', 0) - (agent.get('current_moet_debt', 0) - agent.get('total_interest_accrued', 0))
print(f"   ⚠️  DISCREPANCY CHECK:")
print(f"       YT Purchased should equal MOET Borrowed (ex-interest)")
print(f"       Difference: ${abs(discrepancy):,.2f}")
if abs(discrepancy) > 100:
    print(f"       ❌ ACCOUNTING ERROR DETECTED!")
```

**Intended invariant**: `YT_initial_value == Principal_borrowed`

**Formula used**: `Principal = current_moet_debt - total_interest_accrued`

---

## The Bug

### Root Cause

The formula `debt - interest = principal` is **only valid when no debt has been repaid**.

When debt is repaid:
- `moet_debt` is decremented by the repayment amount
- `total_interest_accrued` is **never adjusted**

### Evidence

**1. Debt repayment code** (`tidal_protocol_sim/agents/high_tide_agent.py`, lines 321-323):

```python
debt_repayment = min(available_moet, self.state.moet_debt)
self.state.moet_debt -= debt_repayment
self.state.token_balances[Asset.MOET] -= debt_repayment
```

Note: `total_interest_accrued` is not modified.

**2. Grep search for interest decrement**:

```
$ grep -r "total_interest_accrued.*-=" tidal_protocol_sim/
No matches found
```

`total_interest_accrued` is **never decremented** anywhere in the codebase.

**3. Interest accrual code** (`tidal_protocol_sim/agents/high_tide_agent.py`, lines 509-514):

```python
old_debt = self.state.moet_debt
self.state.moet_debt *= interest_factor
interest_accrued = self.state.moet_debt - old_debt
self.state.total_interest_accrued += interest_accrued
```

Interest is accumulated on the **total debt at each moment**, including on debt that is later repaid.

---

## Worked Example

| Step | Event | moet_debt | interest_accrued | YT_init | Calculated "Principal" |
|------|-------|-----------|------------------|---------|------------------------|
| 0 | Borrow $10,000, buy YT | $10,000 | $0 | $10,000 | $10,000 ✓ |
| 1 | Interest accrues (2%) | $10,200 | $200 | $10,000 | $10,000 ✓ |
| 2 | Sell YT (init=$2,000) for $1,900 (slippage), repay debt | $8,300 | $200 | $8,000 | **$8,100** ✗ |

**After Step 2:**
- Actual remaining principal: ~$8,000
- Formula result: $8,300 - $200 = $8,100
- Discrepancy: $8,000 - $8,100 = **-$100**

The formula incorrectly computes "principal" because:
1. The $200 interest was earned on $10,000 debt
2. After repaying $1,900, only $8,300 debt remains
3. But $200 interest (on the original $10k) is still subtracted
4. This yields $8,100, not the actual ~$8,000 remaining principal

---

## Observed Simulation Values

From the simulation run output:

| Metric | Value |
|--------|-------|
| YT Initial Value (remaining) | $31,088.52 |
| Current MOET Debt | $34,240.43 |
| Total Interest Accrued | $2,609.95 |
| Calculated "Principal" | $31,630.48 |
| YT Sold (deleveraging) | $2,955.35 |
| **Reported Discrepancy** | **$541.96** |

The $541.96 discrepancy reflects:
1. Cumulative slippage when selling YT (~$542 less MOET received than YT initial cost sold)
2. The flawed "principal" calculation after debt repayments

---

## Why This Is Not an Accounting Bug

The simulation correctly tracks:
- `moet_debt`: Current total debt (principal + accrued interest)
- `total_interest_accrued`: Historical sum of all interest accrued
- `total_initial_value_invested`: MOET spent on YT purchases (decremented by initial cost when sold)

These values are individually correct. The bug is in the **derived calculation** `debt - interest`, which does not equal remaining principal after repayments.

---

## Recommendations

### Option 1: Track Principal Separately
Add a new field `principal_borrowed` that:
- Increases when MOET is borrowed
- Decreases proportionally when debt is repaid

### Option 2: Adjust Interest on Repayment
When debt is repaid, adjust `total_interest_accrued` proportionally:
```python
interest_portion = (repayment * total_interest_accrued) / moet_debt
total_interest_accrued -= interest_portion
moet_debt -= repayment
```

### Option 3: Remove or Reclassify Check
- Remove the check entirely, OR
- Change threshold to informational (not flagged as "ERROR")
- Add context explaining this reflects slippage, not an accounting bug

---

## Conclusion

**The discrepancy check formula is mathematically incorrect after debt repayments occur.** The $541.96 discrepancy is expected behavior reflecting cumulative swap slippage, not a simulation bug. The "ACCOUNTING ERROR DETECTED!" message is a false positive.
