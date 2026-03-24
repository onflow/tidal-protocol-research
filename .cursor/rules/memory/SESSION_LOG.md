# Session Log

Technical insights, artifacts, bugs, open questions. Snippets over prose; cross-reference artifacts instead of duplicating content.

## Audit State (living summary — update each session)

**Active commit:** `ba544b1` — branch `alex/sim-validation_commit-ba544b1` (7 commits ahead of `ba544b1`).

**Per-simulation status:**

| Simulation | Phase | Notes |
|------------|-------|-------|
| `balanced_scenario_monte_carlo.py` | **Update & extension** | Analysis complete (→ `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`). Bug fixes in original; new code in `sim_adaptations/`. |
| `hourly_test_with_rebalancer.py` | Analysis | Ran mode 1 & 3 (→ `POOL_REBALANCER_36H_COMPARISON.md`). Open: algo rebalancer $0 profit, off-by-one in range(2160). |
| `flash_crash_simulation.py` | Analysis | Detailed code review + scenario summary done. Runner broken at ba544b1 (import path + stale attribute). Never run. Open: infinite leverage loop (`moet_debt` reset). → `FLASH_CRASH_SIMULATION_SUMMARY.md`, `SIMULATION_COMPARISON_monte_carlo_vs_flash_crash.md` |
| `full_year_sim.py` | Analysis | Discrepancy check false positive root-caused (→ `DISCREPANCY-ANALYSIS_full_year_sim.md`). |
| Others (§4.3 panels, etc.) | Not started | Snapshot frequency default (1440min) + chart x-axis bug blocks reproduction. |

**Policy:** New/extended sim code goes in `sim_adaptations/`. Existing sims receive only bug fixes, no substantial modifications.

**Primer timeline (verified):** Google Docs version history shows the Primer already included Figure 2 and most §4 figures by 2025-10-07. Code commits `684c007`–`48a9ff2` (2025-09-25 to 2025-09-29) introduced post-delivery changes that break reproduction. No committed code version reproduces them.

**Prior analysis (da4cbf9, completed):**
- Branch: `alex/sim-validation_commit-da4cbf9`
- Artifacts: `sims-review_commit-da4cbf9/` (8 analysis docs), `results_commit-da4cbf9/` (all run outputs)
- Summary: 8 Primer §4 figures mapped; AAVE liquidation cascading bug root-caused and fixed (→ `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`); core formulas verified; slippage discrepancy root-caused (swap formula change + fee bypass + triple-recording); pre-existing bugs (fee bypass, triple-recording, infinite leverage); post-delivery changes (btc_final_price, snapshot frequency, swap formula).

**ba544b1 analysis (completed):**
- Diff purely organizational (file moves); all prior findings persist unchanged.
- Figure 2 reproduced with same fix set: 1/5 runs exact match, others ±20pp.

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

**D9 — Swap formula change (category i):** Commit `48a9ff2` (2025-09-29) replaced `get_amount0_delta` (Q96 integer math) with `get_amount0_delta_economic` (floating-point) for YT→MOET output in `compute_swap_step`. The original integer formula had ~0.25% truncation loss on concentrated stablecoin positions (producing ~$2 slippage per $842 trade). The replacement gives near-1:1 output (~$0.005 slippage). The change post-dates `1c9fce8` (2025-09-23), which is the last commit where the formula has the form consistent with the Primer's slippage magnitudes — but no committed version fully reproduces the Primer's numbers. Exact Primer generation date unknown.

**B3 — Fee bypass (category ii, pre-existing):** `uniswap_v3_math.py:1282` omits `fee_amount` from `amount_specified_remaining` update. Present since swap function was first written. Causes fee to be re-swapped in subsequent loop iterations. Impact masked by integer truncation in original formula; amplified by floating-point formula.

**B4 — Triple-recording (category ii, pre-existing) — FIXED (2026-03-11):** `engine.rebalancing_events` got 3 appends per event (engine lines 536, 562, 628). Present since `684c007`. Fix: removed appends at 536 and 628 (+ method `record_agent_rebalancing_event` + caller at `high_tide_agent.py:354`); kept 562 only.

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

## 2026-03-03: F4 Fix — AAVE Liquidation Cascading Bug

**Root cause chain (fully traced):**
1. `execute_aave_liquidation` created a fresh MOET:BTC Uniswap V3 pool and called `calculate_swap_slippage(btc_value, "BTC")` to convert seized BTC→MOET
2. Post-`1c9fce8`, BTC swap routing changed from `_calculate_btc_to_moet_swap` (correct) to `_calculate_btc_to_stablecoin_swap` (double-converts USD value → astronomical swap amount)
3. Pool exhausted liquidity → post-`1c9fce8` code raised `ValueError("LIQUIDITY COVERAGE FAILURE")` → exception handler returned `amount_out: 0.0`
4. Agent's BTC seized but zero debt repaid → HF crashed (1.0→0.55→0.10→0) → 3 cascading liquidations → $77k total cost
5. **Deeper issue**: even with routing fixed, the MOET:BTC pool has fundamental scaling bug: `_initialize_btc_pair_positions` uses raw `total_liquidity * 1e6` as L, treating it as abstract units regardless of token price ratios. Pool returns ~1:1 in raw units instead of ~79,000:1 for BTC:MOET. This affects both old and new code but old code masked it by running swap loop with stale liquidity past uncovered ticks.

**Fix applied:**
- `aave_agent.py:execute_aave_liquidation` — replaced broken AMM swap with direct debt repayment. Matches real AAVE mechanics: liquidator provides stablecoins directly, no AMM intermediary. Debt reduced by 50%, BTC seized = `debt_reduction * 1.05 / btc_price`.
- `uniswap_v3_math.py` — two ancillary fixes: (a) `LIQUIDITY COVERAGE FAILURE` now `break`s gracefully instead of `raise ValueError`, returning partial swap result; (b) BTC swap routing restored for MOET:BTC pools (routes to `_calculate_btc_to_moet_swap` instead of broken stablecoin function).

**Results after fix (da4cbf9, HT-first order):**
| Run | AAVE surv (sim) | AAVE surv (Primer) | Δ | Cost/liq (sim/Primer) |
|-----|----------------|-------------------|---|----------------------|
| 1   | 60%            | 40%               | +20pp | $34,678 / $32,956 |
| 2   | 40%            | 60%               | −20pp | $34,677 / $32,884 |
| 3   | **80%**        | **80%**           | **0 ✓** | $34,516 / $32,946 |
| 4   | 40%            | 60%               | −20pp | $34,719 / $32,931 |
| 5   | 60%            | 80%               | −20pp | $34,326 / $32,315 |

- Liquidation events: 1 per agent (was 3) ✓
- Cost residual: +$1.5–2.5k explained by 0.80→0.85 collateral factor change
- Survival: **1/5 runs match** (Run 3 only); others off by exactly 20pp (one agent each)
- **Note**: prior session log entry had stale sim values in the "Primer" column — corrected 2026-03-03
- **F4 finding status**: `evidence-supported` → ready for validation

**Still deferred:** D9 (swap formula revert for HT costs), F3 (HT cost 1.8× gap), pool scaling bug (affects all BTC:stablecoin swaps)

---

## 2026-03-03: Commit Transition — da4cbf9 → ba544b1

**Context:** UnitZero pushed fixes; newest commit `ba544b1`. We are transitioning to analyze the new code while preserving all learnings from `da4cbf9`.

**Organizational changes:**
- Branch `alex/sim-validation_commit-da4cbf9` preserves our surgical edits to `da4cbf9`
- Audit documents renamed: `sims-review/` → `sims-review_commit-da4cbf9/` (note: all `→ sims-review/X` references in session entries above this point refer to `sims-review_commit-da4cbf9/X`)
- Memory restructured: `CONCLUSIONS.md` now has commit-scoped sections; prior findings carried forward as "zero-hypotheses" with `to-verify` status
- New analysis will go in `sims-review_commit-ba544b1/` and `results_commit-ba544b1/`

**Approach for ba544b1:** Diff-driven triage first — classify each prior finding by whether UnitZero's changes touched the relevant code. Then verify in priority order: pre-existing bugs (likely persist) → post-delivery changes (may be addressed) → reproduction attempts.

---

## 2026-03-03: Figure 2 Reproduction at ba544b1

**ba544b1 diff result:** Pure file reorganization (`archive_tests/`, `comprehensive_tests/`). No changes to any core engine, agent, or math file. `balanced_scenario_monte_carlo.py` byte-identical to `da4cbf9` version. No new reproduction guidance added.

**Fixes required (same as da4cbf9):**
1. **Import fix** — `from target_health_factor_analysis import create_custom_agents_for_hf_test` (file deleted in `684c007`, function never called): remove import statement
2. **D7** — `btc_final_price`: `90_000.0` → `76_342.50`
3. **F4 fix** — `aave_agent.py:execute_aave_liquidation`: replace broken AMM swap with direct debt repayment
4. **Simulation order** — swap AAVE before HT (HT resets seed internally; AAVE doesn't)

**Results (F4 fix + swapped order):**
| Run | AAVE surv (sim) | Primer | Δ | Cost/liq (sim/Primer) |
|-----|----------------|--------|---|----------------------|
| 1 | 60% | 40% | +20pp | $34,678 / $32,956 |
| 2 | 40% | 60% | −20pp | $34,677 / $32,884 |
| 3 | **80%** | **80%** | **0 ✓** | $34,516 / $32,946 |
| 4 | 40% | 60% | −20pp | $34,719 / $32,931 |
| 5 | 60% | 80% | −20pp | $34,326 / $32,315 |

- Match: 1/5 runs (Run 3). Others off by exactly 20pp (one agent each). Total error 80pp — same as Attempt 4 from da4cbf9. Results reproducible and consistent across commits.
- HT cost ~$0 (D9 swap formula change still present; not reverted here)
- Auditor: results "look intuitively better than what is currently in the primer"

**All prior findings confirmed at ba544b1** — B2, B3, B4, D7, D8, D9, F4 all persist (code untouched).

---

## 2026-03-10: Phase Transition — Simulation Update & Extension

**Phase transition** for `balanced_scenario_monte_carlo.py`: moving from analysis/reproduction to update & extension.
- Per-simulation phase tracking introduced in Audit State (initially over-generalized as global; corrected by auditor)
- New code targets `sim_adaptations/`; existing sims receive only bug fixes
- Memory system reviewed: all directives intact, no drift, no anomalies

**Corrections received:**
1. Phase scope: per-simulation, not global → Audit State restructured with per-sim table
2. Shorthand IDs (F4, B2, etc.) are scoped to their analysis doc → replaced with descriptive text + doc references in Audit State
3. Living summary stale (`f5fd2f5` one commit ahead → actually 5 ahead) → updated

**Patterns extracted:**
- "Scoped IDs need source context" → `WORKING_STYLE.md § Document Authoring`
- "Generalization awareness" reinforced (+1, now 2)

---

## 2026-03-10b: Flash Crash Review & Doc Cleanup

Reviewed `run_flash_crash.py` scenario and existing flash crash analysis.

**Fixes:**
- `run_flash_crash.py` menu strings: YT crash magnitudes were stale (35/50/70% → corrected to 20/32/45%)
- `SIMULATION_COMPARISON_monte_carlo_vs_flash_crash.md`: 4 ambiguities fixed (HF triple notation, BTC endpoint D7 context, system debt per-protocol, date)

**Technical insight — flash crash agent divergence:** 150 agents start with identical parameters, but diverge through: (1) processing order × pool liquidity (primary — $500k MOET:YT pool is small relative to aggregate demand), (2) oracle wick timing amplifying queue effects, (3) BTC recovery noise propagating through already-diverged states. Unverified: whether per-agent random draws or agent-order shuffling add further divergence.

**Direction extracted:** "Results over process" → `WORKING_STYLE.md § Document Authoring`

---

## 2026-03-10c: Data Source Mapping & Simulation Comparison

Auditor-requested deep review of both `run_flash_crash.py` and `balanced_scenario_monte_carlo.py` scenarios, plus real-world data usage across all simulations.

**Artifacts created (in `sims-review_commit-ba544b1/`):**
- `SIMULATION_DATA_SOURCES.md` — maps real-world CSV files to consuming simulations; documents what's synthetic
- `SIMULATION_COMPARISON_monte_carlo_vs_flash_crash.md` — conceptual comparison of the two simulations

**Findings:**
- `optimal_range_lookup_corrected.csv` referenced by `pool_rebalancer.py` but **missing from repo** → `FileNotFoundError` if ALM optimal-range code path fires (affects year-long studies + flash crash when pool arbing enabled; Monte Carlo unaffected since `enable_pool_arbing = False`)
- `dune_query_6227486.csv` (1-min BTC prices, single day) not loaded by any simulation script
- `run_flash_crash.py` import path broken at ba544b1 (`sim_tests.flash_crash_simulation` → file moved to `sim_tests/archive_tests/`)
- Flash crash oracle timing offset: BTC crash window (900–925) vs oracle manipulation window (895–920) → 5-min phase where BTC at floor but oracle already recovering (minutes 921–925)

**Working style reinforcement:** Cross-references pattern in audit docs (dedicated section, relative paths, brief context) — auditor explicitly praised.

---

## 2026-03-10d: Remediation Cross-Check & Doc Reorganization

Auditor-initiated verification: which edits from PRIMER-COMPATIBLE analysis are applied in the current code?

**Verification results — all 5 edits confirmed applied:**
1. Import stub removal: lines 33–34 have comment stub ✓
2. `btc_final_price = 76_342.50`: line 203 ✓
3. F4 direct debt repayment: `aave_agent.py` line 204 `actual_debt_repaid = debt_reduction` ✓
4. Sim order swap: lines 425–431 AAVE first, then HT ✓
5. D9 revert: `compute_swap_step` lines 341–343 use `get_amount0_delta` (standard formula). Commit `081a011` ✓

**Pre-existing bugs verified still present:**
- B3: `uniswap_v3_math.py:1279` — `amount_specified_remaining -= amount_in` (still omits `fee_amount`)
- B4: `high_tide_vault_engine.py` — 3 `rebalancing_events.append` sites (lines 536, 562, 628) — **FIXED (2026-03-11)**: removed 536 and 628, kept 562

**Results data update:** Results in `results_commit-ba544b1/` are current (all 5 edits applied, including D9 revert). Auditor corrected an earlier misunderstanding that the results predated D9.

**New observation — F3 gap widened:** HT costs with current engine + D9 revert = $1–4/agent. Much lower than old engine at `1c9fce8` ($9–13/agent) or Primer ($19–22). The post-`2fd742d` engine changes (leverage check throttling, MOET balance accounting) alter rebalancing behavior, widening the F3 gap from 1.8× to 5–15×. AAVE results are byte-identical between pre- and post-D9 runs, confirming the D9 change only affects the HT swap path.

**Doc reorganization:**
- Moved `FCM_PRIMER_FIGURE_MAPPING.md` from `sims-review_commit-da4cbf9/` to `sims-review_commit-ba544b1/`
- Added Remediation Status table (per-script, per-issue, with fix status)
- Updated `PRIMER-COMPATIBLE_balanced_scenario_monte_carlo.md` Results section with pre-D9 result table
- Fixed cross-references (FCM doc moved)
- Updated `CONCLUSIONS.md` ba544b1 status column for all findings

**Also noted:** `base_case_charts.py` exists in `sim_tests/archive_tests/` — UnitZero's charting utility for the comparison object. Generates charts from results data (BTC price, survival, net APY, health factor, yield strategy, agent performance). ~1069 lines.

---

### Session 2026-03-11: B4 fix + Monte Carlo chart replacement

**B4 fix applied:**
- Removed duplicate `rebalancing_events.append` at engine line 536 and method `record_agent_rebalancing_event` (lines 625–648) + caller at `high_tide_agent.py:354`
- Kept single append at line 562 — covers both normal rebalancing and emergency yield sale paths
- Verified: post-fix agent 0 Run 1 shows 96 events (was 225 = ~3× inflated; cost 0.92 vs 2.76 = exactly 3×)
- Re-ran `balanced_scenario_monte_carlo.py`; results regenerated in `results_commit-ba544b1/`

**Chart replacement — `performance_matrix_heatmap.png`:**
- Created `sim_adaptations/balanced_mc_overview_charts.py`
- Reads CSV + JSON from results dir; computes 3 metrics per (Strategy, Scenario):
  1. Survival rate (3 series: HT rebal. sufficiency, HT no collat. liq., AAVE)
  2. Liquidated collateral value (HT, AAVE)
  3. Position degradation (HT, AAVE)
- Generates 2 charts: `overview_bars.png` (grouped bars, mean ± std across runs) and `per_run_lollipops.png` (per-run breakdown)
- Consistency checks all pass: HT survival 100%, AAVE 56%, HT $0 liquidated, AAVE $76k/run, HT $387/agent degradation, AAVE $804/agent

**All B4 references updated** across 5 documents: DISCREPANCY-ANALYSIS (da4cbf9), FCM_PRIMER_FIGURE_MAPPING (ba544b1), PRIMER-COMPATIBLE (ba544b1), CONCLUSIONS.md, SESSION_LOG.md.

→ Artifacts: `sim_adaptations/balanced_mc_overview_charts.py`, `overview_bars.png`, `per_run_lollipops.png`

---

### Session 2026-03-11b: Position degradation recovery framing

**Recovery degradation metric added** to `balanced_mc_overview_charts.py`:
- Per-agent `recovery_degradation`: FCM = bottom (fixed stablecoin cost); AAVE = `P_0 - (Final_Net_Position / P_bottom) * P_0`
- `per_run_summary()`: new cols `mean_recovery_degradation`, plus AAVE survived/liquidated split (`mean_pos_degrad_aave_surv`, `mean_recov_degrad_aave_surv`, `_aave_liq` variants)
- `overview_summary()`: mean ± std for all new per-run cols

**Position degradation chart replaced** with dual-scenario grouped layout:
- 3 groups (FCM, AAVE survived, AAVE liquidated) × 2 scenarios ("At crash bottom", "After full recovery")
- Annotations: FCM bracket "$387 (fixed)", AAVE liquidated arrow "+$426 from recovery"
- Subtitle: "FCM cost is fixed; AAVE liquidation losses grow with recovery"
- Footnote: "56% of AAVE agents survived. Gas costs not modeled."
- Title: "Unrecoverable Position Damage"

**Lollipop panel 3 updated** to show recovery degradation with 3-way AAVE split (FCM, AAVE survived, AAVE liquidated). Title: "Position Degradation After Full Recovery".

**Numbers (verified against plan estimates):**
| | Plan | Actual |
|---|---|---|
| FCM recovery | $387 | $387 |
| AAVE survived recovery | $467 | $506 |
| AAVE liquidated recovery | $1,798 | $1,802 |
| AAVE avg recovery | $1,053 | $1,053 |

→ Artifacts: `position_degradation.png` (new layout), `per_run_lollipops.png` (panel 3 updated)

---

### Session 2026-03-17: B4 `yield_token_trades` verification + B5 deleveraging gap

**B4 extension — `yield_token_trades` safety verified:**
Auditor-requested exhaustive code-path analysis: is the `yield_token_trades.append` inside the removed `record_agent_rebalancing_event` also redundant? Confirmed safe for all three YT sale paths:
- Rebalancing + emergency: per-cycle recording at `_execute_yield_token_sale` line 577 already covers these
- Deleveraging: never called `record_agent_rebalancing_event`; has own tracking
- Purchases: independent at line 490

**B5 — new finding: deleveraging YT sales absent from `engine.yield_token_trades`:**
The deleveraging path (`agent.execute_deleveraging` → `agent.execute_yield_token_sale`) calls the pool directly, bypassing `engine._execute_yield_token_sale`. Deleveraging data exists in `agent.state.deleveraging_events` / `engine.deleveraging_events` but is not consolidated into `yield_token_trades`. Affects `real_slippage_cost`, `total_rebalancing_sales`, chart functions. Pre-existing gap; does not affect `balanced_scenario_monte_carlo.py` (no deleveraging).

**Code-reference cross-check (auditor-directed):**
Systematic verification of all line-number references in `FCM_PRIMER_FIGURE_MAPPING.md`. Found 8 stale refs from two root causes:
- Edit 1 (import fix) removed 1 net line from `balanced_scenario_monte_carlo.py` → 3 refs shifted by −1
- B4 fix (comment blocks) added +3 lines in engine, +2 in agent → 4 refs shifted
- 1 pre-existing error (`hourly_test_with_rebalancer.py` sys.path: 18→29, was always wrong)
All other refs (19+) confirmed correct. New directive extracted: "Verify code refs after edits" → `WORKING_STYLE.md § Document Authoring`.

**Memory system observation:** First positive evidence that `03-memory-update-triggers.mdc` (system-prompt trigger checklist) is working — successfully reinforced a directive on a praise-only turn, which was previously the failure mode. Logged in `WORKING_STYLE.md § Memory Update Crowding`.

→ `FCM_PRIMER_FIGURE_MAPPING.md` §B4 (extended), §B5 (new), line refs updated throughout
→ `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md` (da4cbf9) §F5 cross-reference updated; broken FCM doc link fixed

---

### Session 2026-03-17b: Chart legend rework — overview_bars + position_degradation

**overview_bars.png — legend split and reframing:**
- Replaced shared 3-entry bottom legend with per-panel dedicated legends
- Left panel (Survival Rate): 2 entries — "FCM: no collateral liquidated", "AAVE: 56% of agents unaffected by liquidation"
- Right panel (Liquidated Collateral Value): 3 entries — reframed to describe averaging population: "average across all agents (including unaffected)" vs "average across liquidated agents only (44%)"
- Right panel y-axis moved to right side; left panel narrowed (1:1.6 ratio); title gap tightened

**position_degradation.png — legend reframing:**
- FCM entry: "rebalancing cost only, no liquidation losses" (metric-relevant, not survival-relevant)
- AAVE entries: parallel structure with percentage at end
- Legend kept inside chart (sufficient space at top)

**Additional polish:**
- Selective error bars: bars drawn without `yerr`, then `ax.errorbar(x, y, yerr=..., fmt="none")` called only for bars that need them. Avoids matplotlib drawing cap remnants on zero-variance bars. `fmt="none"` suppresses marker/line, drawing only whisker+caps.
- FCM survival error bar removed (zero variance); AAVE-liquidated-only error bar removed (near-zero variance — same 50% debt + 5% penalty mechanics for all liquidated agents)
- Docstring added to `plot_overview_bars` documenting layout techniques; inline comments document x-position mapping and errorbar parameter semantics

**Design principle applied:** Legend text should describe what the bar represents *in the context of the chart's metric*, not repeat the same framing across all charts. The same sub-population can need different descriptions depending on whether the chart shows survival, collateral loss, or position degradation.

→ Artifacts: `overview_bars.png`, `position_degradation.png` (both regenerated), `balanced_mc_overview_charts.py` (documented)

---

### Session 2026-03-18: Yield harvesting exhaustive audit

**Context**: Auditor relayed colleague Felipe's description of a weekly `_check_deleveraging` that harvests rebased YT gains when HF > initial_hf — sells accrued yield, converts to BTC collateral. Auditor named it "yield harvesting" and asked for exhaustive codebase/docs/reports search.

**Findings — yield harvesting fully implemented in two agents:**

1. **HT agent** (`high_tide_agent.py:723`): `_check_deleveraging` has two branches:
   - Check 1 (HF deleveraging): HF > initial×1.05 → sell YT to reduce HF to initial×1.02 (position reduction, not harvest)
   - Check 2 (weekly harvest): every 7 days → `_execute_weekly_deleveraging` (line 775) → sells accrued yield (rebasing price increase × quantity) → full swap chain YT→MOET→USDC/USDF→BTC→deposit as collateral

2. **AAVE agent** (`aave_agent.py:307`): `execute_weekly_rebalancing` called at `leverage_frequency_minutes` intervals:
   - HF < initial×0.99 → deleverage (sell YT → repay debt)
   - HF ≥ initial → harvest (sell incremental yield → MOET / btc_price → add BTC collateral; simpler than HT, no AMM)

3. **Dead config flag**: `enable_weekly_yield_harvest` set in all 14 study scripts, never read by `full_year_sim.py`, engine, or agents. No gating effect — harvest logic always active.

4. **Exercise scope**: All year-long studies (S1–S14) exercise this. Short sims (balanced_scenario_monte_carlo 60min, flash crash 2d, hourly_test 36h) never fire the weekly timer.

5. **Documentation**: Whitepaper Study 11 section (lines 1556–1690) has full pseudocode + rationale. `SIMULATION_STUDY_CATEGORIZATION.md` documents both agents. `HIGH_TIDE_VAULT_ENGINE_README.md` covers only leverage-increase, not harvest.

6. **Why it goes beyond simple yield harvesting**: (a) cross-asset conversion (YT yield → BTC collateral, different token types); (b) collateral reinforcement loop — harvest improves HF, which can trigger separate leverage-increase path (10-min check), composing the two mechanisms.

→ `sims-review_commit-ba544b1/YIELD_HARVESTING_AUDIT.md`

**Check 1 (HF deleveraging) dead code — three compounding errors:**
- Layer 1: Sizing math produces negative `debt_reduction_needed` when trigger fires (HF > initial×1.05 but target_hf = initial×1.02, so target_debt > actual debt at P_MOET≈1)
- Layer 2: Execution path (YT→MOET→stablecoin→BTC→deposit) adds collateral / raises HF — contradicts stated purpose of reducing HF
- Layer 3: Priority ordering (leverage increase at step 2 fires before `_check_deleveraging` at step 4)
- **Impact**: None — code never fires. Present in all HT simulations but inert. Verified at `ba544b1` on remote.
→ `sims-review_commit-ba544b1/HF_DELEVERAGING_DEAD_CODE.md`
→ Cross-references added to `YIELD_HARVESTING_AUDIT.md` (strikethrough Check 1 row + annotation)

---

### Session 2026-03-19: Generalized Agent Learnings — Systematic Review Planning

**Context**: Meta-task — systematic per-file review of `generalized-agent-learnings/` against `.cursor/rules/` source material.

**Technical research — subagent context architecture:**
Auditor challenged batched subagent approach. Web research confirmed:
- Opus 4.6: 1M token context, but practical attention degrades ~100-200K tokens
- Cursor subagents: isolated context windows (own clean context per subagent)
- Estimated ~50-70K tokens per review subagent (all source + all target files) — well within high-quality range
- Conclusion: one subagent per file (10 parallel) beats batching; batching only crowds context without benefit since each subagent reads all files anyway

→ `TECHNICAL.md § Cursor Subagent Architecture`

**Auditor directive**: "resources are well invested here" — continue iterating until diminishing returns reached, not to minimize subagent runs.

**Reviews completed** — 10 parallel subagents produced `generalized-agent-learnings-review/` (10 review files + 1 consistency pass). Key findings:
- 1 factual error (07 §8 "most reinforced" claim)
- 1 high-priority gap (Active Retrieval / session-start protocol missing from 01, 03, 08)
- 4 files missing cross-references sections (01, 02, 05, 06)
- 1 content overlap (04/05 cross-referencing after changes)
- 4 spots with residual domain-specific language
- No contradictions across reviews; all 10 consistent

**Auditor feedback on PLAN-review**: O1 (archival vs. living status) — auditor values both uses. PLAN.md should explicitly state dual purpose: archival record + reusable template.

**Implementation of high/medium-value changes** — applied all changes identified in `CONSISTENCY-PASS.md`:
- PLAN.md: source list corrected (added TECHNICAL, CONCLUSIONS; fixed count), dual-purpose Status section added
- 00-OVERVIEW.md: Validation Gate design decision added, reading order annotated with rationale
- 01-MEMORY-SYSTEM.md: Active Retrieval section added (HIGH), Validation Gate in update rules, pattern extraction trigger (item 7), cross-references section
- 02-INTERACTION-STYLE.md: cross-references section added, forward-refs to 03 (corrections) and 04 (evidence)
- 03-SELF-IMPROVEMENT.md: session-start cadence added (HIGH), chart legend example generalized, Three Priorities → 01 forward-ref, step 7 in corrections (repetition check)
- 04-EVIDENCE-AND-VALIDATION.md: status definitions table, cross-referencing thinned to ref 05, remediation scope broadened
- 05-CODE-AND-DOCUMENTS.md: cross-references section, piped input technique, version-to-cite guidance
- 06-FAILURE-MODES.md: F10 (Duplicated Data Drift) added, F7 status enriched, F9 example generalized, cross-references section
- 07-META-LEARNINGS.md: §8 factual fix ("most reinforced" → "among the most"), §7 and §11 framed as examples
- 08-BOOTSTRAPPING.md: Step 4 (session-start protocol), trigger checklist template in Step 2, Phase 2 correction cross-ref, Phase 3 mitigation note

---

### Session 2026-03-23: Monte Carlo agent initialization audit + doc correction

**Auditor-requested exhaustive analysis**: How much debt and collateral does each agent start with in `balanced_scenario_monte_carlo.py`?

**Findings — initialization traced through full call chain:**
- Both HT and AAVE agents share identical initialization (`AaveAgentState` inherits `HighTideAgentState.__init__`)
- Collateral: 1 BTC = $100,000 (hardcoded at `high_tide_agent.py:33`)
- Debt: `$85,000 / initial_hf` where `initial_hf ~ U(1.25, 1.45)` → range $58,621–$68,000, E[debt] ≈ $63,079
- `initial_balance = 100_000.0` (constructor default) is used as BTC price, not as a dollar balance

**Doc correction — `SIMULATION_COMPARISON_monte_carlo_vs_flash_crash.md`:**
- System debt was listed as "$65k per agent / $325k per protocol / $650k total" — corrected to ~$63k / ~$315k / ~$630k with derivation formula
- Interest figure corrected: $0.74 → $0.72

**CSV reporting bug noted**: `balanced_scenario_monte_carlo.py:2295` hardcodes `Current_MOET_Debt: 0.0` for AAVE agents with comment "AAVE agents don't have MOET debt" — incorrect; AAVE agents do borrow MOET via inherited `HighTideAgentState` init. Affects CSV output only, not simulation.

**Flash crash cross-check**: $133k/agent confirmed correct (explicit `$20M / 150` target at `flash_crash_simulation.py:54,712,728`). Different initialization path: `_setup_large_system_positions` overrides agent state directly rather than deriving from HF.

---

## Open Questions (cross-session)

| ID | Question | Since | Refs |
|----|----------|-------|------|
| F1 | Algo rebalancer $0 profit on $3.6M volume — accounting bug or design? | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| F2 | off-by-one in `range(2160)` — 3rd ALM trigger never fires | 2026-02-27 | `POOL_REBALANCER_36H_COMPARISON.md` |
| B2 | Flash crash infinite leverage loop — `moet_debt` reset root cause | 2026-02-20 | `FLASH_CRASH_SIMULATION_SUMMARY.md` |
| F3 | HT cost ~1.8× lower than Primer at every tested commit | 2026-03-02 | `DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md` |
| — | `enable_weekly_yield_harvest` config flag set in 14 study scripts but never consumed by sim/engine/agents | 2026-03-18 | SESSION_LOG this entry |
