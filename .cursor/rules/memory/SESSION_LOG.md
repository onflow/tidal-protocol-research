# Session Log

Technical insights, artifacts, bugs, open questions. Snippets over prose; cross-reference artifacts instead of duplicating content.

## Audit State (living summary — update each session)

**Phase:** Reproducibility assessment of FCM Primer §4 claims via source simulation scripts.

**Covered so far:**
- All 8 Primer §4 figures mapped to source scripts → `FCM_PRIMER_FIGURE_MAPPING.md`
- All sim scripts catalogued by runnability → `RUNNABILITY_AUDIT.md`
- `hourly_test_with_rebalancer.py` executed (modes 1 + 3), partial reproduction (2/6 panels match, 1/6 partial, 3/6 fail)
- `balanced_scenario_monte_carlo.py`: **4 reproduction attempts** (current code, current engine+fixed config, old engine+fixed config, old engine+swapped order). Swapped order reduces AAVE survival error 43% (3/5 runs match combined). Commit `cfdbd21` disproven as reproduction source. HT costs ~1.8× gap and 2/5 AAVE survival runs remain unexplained. → `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`
- Flash crash simulation analyzed (not executed to completion — B2 leverage loop blocks)
- Core formulas verified: Health Factor, Debt Reduction, Rebalancing algorithm
- **Slippage discrepancy root-caused (D9)** — post-Primer swap formula change (`48a9ff2`) + pre-existing fee bypass (B3) + triple-recording (B4)

**Key audit artifacts:** `sims-review/` — `FCM_PRIMER_FIGURE_MAPPING.md`, `RUNNABILITY_AUDIT.md`, `POOL_REBALANCER_36H_COMPARISON.md`, `FLASH_CRASH_SIMULATION_SUMMARY.md`, `DISCREPANCY-ANALYSIS_full_year_sim.md`, `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`, `MOET_DOLLAR_PEG_INSTANCES.md`, `SIMULATION_STUDY_CATEGORIZATION.md`

**Natural next steps:**
- Revert D9 (`48a9ff2` swap formula in `compute_swap_step`) and re-run to verify slippage matches Primer's ~$2
- Fix D8 (snapshot frequency + chart x-axis) and re-run for full §4.3 reproduction
- Fix `comprehensive_ht_vs_aave_analysis.py` import and test Figure 5
- Investigate F3 (HT cost 1.8× gap) — possibly related to B4 triple-recording interaction or different pool parameters
- Resolve open questions F1 (algo profit), F2 (ALM off-by-one), B2 (leverage loop)

---

## 2026-02-03: System Genesis

Memory system created. Codebase overview: lending protocol + MOET stablecoin + High Tide yield vaults + Uniswap V3 + agent-based sim + stress testing.

MOET pricing corrected: ≠ $1 peg; correct is `MOET_price = k × geometric_mean(backing_assets)`.
→ `sims-review/MOET_DOLLAR_PEG_INSTANCES.md`, `TECHNICAL.md` updated

---

## 2026-02-06: Discrepancy Check Bug — verified

`full_year_sim.py:2951` false "ACCOUNTING ERROR" ($541.96). Root cause: `total_interest_accrued` never decremented on debt repayment. Sim accounting correct; check flawed.
→ `sims-review/DISCREPANCY-ANALYSIS_full_year_sim.md`

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

Also: WORKING_STYLE.md compacted — removed directions that duplicate always-applied rules, consolidated communication directions, tightened structure. **Post-mortem (2026-02-28): this compaction was overly aggressive — it eliminated tracking metadata for 5 core directives (mutual fallibility, directive confidence scaling, validation gate, generalization awareness, top-down presentation). Restored in restructure below.**

---

## 2026-02-27: Memory System Iteration

Three changes from self-evaluation:
1. Added "Audit State" living summary to top of SESSION_LOG — reduces session-start orientation time
2. Brought CONCLUSIONS.md current — added "Evidence-Supported" tier, populated with D7/D8/rebalancing-limits/AAVE-collateral findings, refreshed open questions
3. Added "Principles over recollections" rule to `00-memory-system.mdc § How to Update` — directions should state general principles, not specific cases that motivated them
4. Made Active Retrieval in `00-memory-system.mdc` more specific (numbered checklist of what to read at session start)

---

## 2026-02-28: Slippage Discrepancy Root Cause — Post-Primer Swap Formula Change (D9)

Auditor-initiated investigation of ~430× slippage discrepancy between Primer figure (image19) and sim output (`agent_slippage_analysis.png`).

**Initial hypothesis (fee bypass) revised after git history cross-check.** Auditor directed two-step approach: (i) identify post-Primer changes causing discrepancy, (ii) catalog pre-existing bugs separately.

**D9 — Swap formula change (category i):** Commit `48a9ff2` (2025-09-29, 4 days after `hourly_test_with_rebalancer.py` was added) replaced `get_amount0_delta` (Q96 integer math) with `get_amount0_delta_economic` (floating-point) for YT→MOET output in `compute_swap_step`. The original integer formula had ~0.25% truncation loss on concentrated stablecoin positions (producing ~$2 slippage per $842 trade). The replacement gives near-1:1 output (~$0.005 slippage). Primer generated in the 4-day window before this change.

**B3 — Fee bypass (category ii, pre-existing):** `uniswap_v3_math.py:1282` omits `fee_amount` from `amount_specified_remaining` update. Present since swap function was first written. Causes fee to be re-swapped in subsequent loop iterations. Impact masked by integer truncation in original formula; amplified by floating-point formula.

**B4 — Triple-recording (category ii, pre-existing):** `engine.rebalancing_events` gets 3 appends per event (engine lines 536, 562, 628). Present since `684c007`.

**Methodology established:** For reproducing Primer results across all simulations: (i) revert post-Primer changes only, (ii) catalog pre-existing bugs separately for independent fixes.

→ `FCM_PRIMER_FIGURE_MAPPING.md` updated: D9 rewritten (swap formula, not fee bypass), B3 reclassified as pre-existing, B4 documented.

---

## 2026-02-28: Memory System Restructure — Retention Policy

**Trigger:** Auditor noticed 5 core directives had been dropped from WORKING_STYLE.md during a prior "compaction." Directives were still in `.mdc` rules but tracking metadata (reinforcement counts, dates, notes) was destroyed.

**Root cause of the failure:** I treated "also exists in .mdc file" as sufficient reason to remove tracking from WORKING_STYLE.md. But `.mdc` = static instruction, WORKING_STYLE.md = learning record. Different purposes; removing one doesn't substitute for the other.

**Key meta-learning (generalized):**
- **Absence of corrective feedback signals compliance, not irrelevance.** A well-internalized directive that stops generating corrections is *more* important to retain, not less.
- **Compaction must preserve provenance.** Merge and generalize — never silently delete. Reinforcement counts are the empirical record of what works.
- **Terminology in audit docs:** Assume only finance/CS/Python is known. Conversation-local shorthand must become prose in `sims-review/` documents. Ask before introducing new nomenclature.

**Changes made:**
1. WORKING_STYLE.md restructured: restored 5 core principles with tracking; added Retention Policy section; added Memory Organization section; separated "Core Principles" from "Communication Style" and "Document Authoring"
2. CONCLUSIONS.md: replaced "Category (i)/(ii)" labels with self-explanatory prose
3. FCM_PRIMER_FIGURE_MAPPING.md: verified clean of conversation-local labels (already was)

**Second pass — system-level improvements (same session):**

Auditor directed deeper self-analysis: the recurring accumulation/pruning failure suggests missing *process*, not just missing *rules*. Applied:

4. Mined git history of all memory files (`git show` across 8 commits). Recovered 2 additional dropped directives (Progressive abstraction, Self-monitoring for patterns).
5. Created `CHANGELOG.md` — provenance file rebuilt from git history. Tracks directive lifecycle + structural changes + meta-learnings. On-demand, not read at session start.
6. Added **Memory Maintenance Protocol** to `00-memory-system.mdc` — procedural checklist requiring compaction to be deliberate (not a side effect), with pre-flight checks against CHANGELOG and git history.
7. Added **session-start health check** to Active Retrieval — brief evaluation: anything unfamiliar? size anomalies? stale entries?
8. Added "Split" to Evolution Operations — prefer creating topic files over pruning content.
9. Generalized 4 meta-learnings into `CHANGELOG.md § Meta-Learnings` (purpose conflation, silence ≠ irrelevance, compaction-as-side-effect, accumulation/pruning tension).

**Process note:** Auditor offered periodic "memory maintenance" prompts between technical sessions. This is valuable — request when substantial reorganization is needed rather than doing it as a side effect of technical work.

---

## 2026-03-02: §4.2 Deep Reproduction — balanced_scenario_monte_carlo.py

Three reproduction attempts: (1) current code as committed, (2) current engine + corrected btc_final_price, (3) old engine at `1c9fce8` + corrected config.
→ `sims-review/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`

**Key findings:**
- F1 (= D7): btc_final_price change — already known, config restored
- F2 (new): **AAVE survival rates NOT reproducible from ANY committed code.** Agent initial HFs deterministic across all versions (identical RNG draws). Primer's (40,60,80,60,80) pattern requires HFs no committed version generates. Only Runs 4,5 match.
- F3 (new): HT costs ~1.8× lower than Primer ($9-13 vs $19-22 per agent) even with old engine and integer swap formula
- F4 (new): Post-`2fd742d` engine triggers 3 liquidation events per AAVE agent (vs 1 in old engine), inflating AAVE costs from ~$32k to ~$77k per agent
- AAVE cost per liquidation with old engine (~$32-33k) matches Primer ✓

**Technical insight — RNG determinism:** AAVE agent HFs are determined by the seed and the total random draws consumed before AAVE agent creation: HT engine construction (N draws) + 5 HT agent draws + HT simulation (M draws via `np.random`) + AAVE engine construction (N draws). N is identical across old/HEAD engine versions; M appears constant across the two tested versions. The `_run_high_tide_scenario` resets the seed, making HT agent HFs invariant to call ordering. The `_run_aave_scenario` does NOT reset the seed, making AAVE HFs sensitive to what ran before.

---

## 2026-03-02b: §4.2 Reproduction — Swapped Order Experiment + `cfdbd21` Investigation

Two avenues tested to get closer to Primer Figure 2.
→ `sims-review/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md` (Attempt 4 + Avenue 1)

**Avenue 1 — Commit `cfdbd21`:**
Claimed to be a "runnable commit" that could reproduce Primer results. Disproven: `btc_final_price = 90_000.0` (wrong), `balanced_scenario_monte_carlo.py` identical to `48a9ff2`, all post-delivery changes present. Cannot produce any AAVE liquidations.

**Avenue 2 — Swapped simulation order (Attempt 4):**
- F6 (new): **Swapped order reduces AAVE survival total error from 140pp to 80pp (43% improvement).** Run 3 matches exactly (80%). Combined best of both orderings: 3/5 runs match (Runs 3,4,5). Remaining 2 runs off by exactly 20pp (one agent each).
- F7 (new): **HT simulation consumes random draws** (`np.random`, for BTC price path). Verified by comparing AAVE HFs from engine-only construction vs full simulation run. Does not affect swapped-order analysis since AAVE agents are created before any simulation.
- Confirmed: swapped AAVE HFs = HT HFs (engine constructors consume identical random draws). Holds at both `1c9fce8` and HEAD.
- Per-run effective liquidation threshold varies (~1.315–1.320 vs theoretical 1.3099), likely due to BTC price path randomness via `np.random` (F6).
- HT costs and AAVE costs per liquidation are unchanged by ordering (HT: seed reset; AAVE: cost is f(debt/collateral)).
- F3 (HT cost 1.8× gap) remains unexplained.

---

## Open Questions (cross-session)

| ID | Question | Since | Refs |
|----|----------|-------|------|
| F1 | Algo rebalancer $0 profit on $3.6M volume — accounting bug or design? | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger never fires | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| B2 | Flash crash infinite leverage loop — `moet_debt` reset root cause | 2026-02-20 | `FLASH_CRASH_SIMULATION_SUMMARY.md` |
