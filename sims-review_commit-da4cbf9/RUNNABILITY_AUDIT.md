# Simulation Runnability Audit

**Date:** February 20, 2026  
**Scope:** All Python simulation scripts in `sim_tests/` and project root  
**Method:** Static analysis of imports, sys.path, config attributes, and documentation cross-reference

---

## Category A: Crash on Import (9 scripts)

### A1: Crash with `ModuleNotFoundError` 


These scripts set `project_root = Path(__file__).parent` instead of `.parent.parent`. Since they live in `sim_tests/` but import from `tidal_protocol_sim/` (at the project root), they fail immediately with `ModuleNotFoundError`.

| Script | Line | Bug |
|--------|------|-----|
| `hourly_test_with_rebalancer.py` | 29 | `.parent` → should be `.parent.parent` |
| `yield_token_pool_capacity_analysis.py` | 28 | `.parent` → should be `.parent.parent` |
| `tri_health_factor_analysis.py` | 28 | `.parent` → should be `.parent.parent` |
| `rebalance_liquidity_test.py` | 26 | `.parent` → should be `.parent.parent` |
| `longterm_scenario_analysis.py` | 31 | `.parent` → should be `.parent.parent` |
| `comprehensive_realistic_pool_analysis.py` | 19 | `.parent` → should be `.parent.parent` |
| `comprehensive_ht_vs_aave_analysis.py` | 24 | `.parent` → should be `.parent.parent` |
| `balanced_scenario_monte_carlo.py` | 24 | `.parent` → should be `.parent.parent` |
| `test_pool_exhaustion.py` | N/A | No sys.path manipulation at all, but imports from `tidal_protocol_sim` |


### A2: Crash with `AttributeError` trying to read non-existent parameter  
*   `run_all_studies.py`
* `run_flash_crash.py` 




## Category B: Run But With Silent Config Bugs (14 study scripts)

All study runner scripts (`run_study_1` through `run_study_10`, `study11`–`study14`) set config attributes that don't exist on `FullYearSimConfig` or use wrong names. Python silently creates new attributes that are never read by the simulation engine.

### B1: `simulation_duration_days` — Set But Never Read

Every study script sets e.g. `config.simulation_duration_days = 365`. But `FullYearSimConfig` only defines `simulation_duration_hours` and `simulation_duration_minutes`. The `__setattr__` override doesn't handle this conversion. The simulation loop uses `simulation_duration_minutes` (line 1375 of `full_year_sim.py`), which stays at the **default 364 days (2021 default)**.

**Impact:**
- For 2024 studies: off by 1 day (mostly harmless)
- For **Study 5/10 (2025, intended 268 days)**: sim runs the default 364 days with only 268 days of BTC data — last 96 days use a flat price (BTC data accessor clamps to last available value). Wrong results, no crash.
 
  The root cause: `FullYearSimConfig.__init__` hardcodes `simulation_duration_minutes = 364 * 24 * 60`. The `get_btc_price_at_minute()` method clamps out-of-range days to the last available price (line 614-615 of `full_year_sim.py`), so studies 5/10 simulate 96 extra days of constant BTC price instead of stopping at day 268. This inflates duration-dependent metrics (APY, rebalance counts, slippage totals) and fundamentally misrepresents the 2025 low-vol scenario.

### B2: `ecosystem_growth_enabled` vs `enable_ecosystem_growth`

Study scripts set `config.ecosystem_growth_enabled = False`. The actual attribute read by the engine is `config.enable_ecosystem_growth`. The `__setattr__` override doesn't translate. Harmless here because the default is already `False`, but indicates the contractor was coding against an API they didn't verify.


## Category C: No issues encountered; but also some simulations not attempted

| Script | Status | Notes |
|--------|--------|-------|
| `run_study_1` through `run_study_10` | **Work** | With silent config bugs (Category B) |
| `study11`–`study14` | **Likely work** | Same silent bugs; untested by us |
| `flash_crash_simulation.py` | **Works** | Core engine, correct sys.path |
| `full_year_sim.py` | **Works** | Core engine, correct sys.path |
| `simple_flash_crash.py` | **Works** | Correct sys.path |
| `base_case_ht_vs_aave_comparison.py` | **Works** | Correct sys.path |
| `diagnostic_base_case.py` | **Works** | Correct sys.path |
| `aave_leverage_strategy_sim_v2.py` | **Works** | Correct sys.path |
| `three_way_strategy_comparison.py` | **Partial** | Correct sys.path but requires pre-existing `Full_Year_2024_BTC_Simulation/` data (orphaned dependency — no script produces this directory) |


## Category D: Insufficient Documentation

| Issue | Detail |
|-------|--------|
| Flash crash simulation | **Completely undocumented** — no README, no guide, no mention in any docs |
| `hourly_test_with_rebalancer.py` | **Undocumented** — the capacity study report (`High_Tide_Capacity_Study_w_Arbing.md`) references its output but never says how to run it |
| `Full_Year_2024_BTC_Simulation/` | **Orphaned reference** — report (`Full_Year_2024_BTC_High_Tide_Performance_Analysis.md`) and `three_way_strategy_comparison.py` reference this directory but no current script produces it |
| `STUDIES_README.md` | Documents the 10-study suite only; omits studies 11-14, flash crash, capacity study |
| `OPTIMIZATION_STUDIES_README.md` | Documents studies 11-14 but provides no run commands |
| files in folder `reports` | insufficient documentation for reproducing figures |

---

## Summary Scorecard

| Category | Count | Severity | Verdict |
|----------|-------|----------|---------|
| **Crash on launch** (sys.path) | **10** scripts | Critical — cannot run | Contractor bug |
| **Crash on during run** (AttributeError) | **2** scripts | Critical — cannot run | Contractor bug|
| **Materially wrong results** (duration bug) | **2** scripts (Studies 5, 10) | **High — 96 phantom days at flat BTC price** | Contractor bug |
| **Confirmed runnable** | approx 21 scripts | N/A | not yet closely inspected |
| **Documentation** | Flash crash, capacity study, studies 11-14 | Medium — cannot reproduce without extensive reading of code  | Contractor omission |

