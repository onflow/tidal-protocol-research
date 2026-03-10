# Simulation Comparison: `balanced_scenario_monte_carlo.py` vs `run_flash_crash.py`

**Date:** 2026-03-10
**Commit:** reference `ba544b1` (on `main`)

---

**Summary**: The Monte Carlo sim asks "is HT better than AAVE?" (comparative, single stressor). The flash crash sim asks "can the protocol survive?" (absolute, multi-stressor).

---

## Side-by-Side

| Dimension | `balanced_scenario_monte_carlo` | `run_flash_crash` |
|-----------|--------------------------------|-------------------|
| **Purpose** | HT vs AAVE head-to-head comparison | Protocol resilience stress test |
| **Protocols** | Both HT and AAVE | HT only |
| **Duration** | 60 minutes | 2,880 minutes (2 days) |
| **Agents** | 5 per protocol per scenario, heterogeneous HFs (uniform 1.25–1.45) | 150 HT, homogeneous (all HF: 1.15 initial / 1.05 rebalancing / 1.08 target) |
| **System debt** | ~$325k per protocol (5 × $65k); ~$650k total across both | $20M (150 × $133k) |
| **BTC price** | Synthetic linear decline ($100k → $76.3k in Primer-compatible config; committed ba544b1 code uses $90k — see D7), engine-controlled | Deterministic crash (5-min drop → floor → exponential recovery), sim-controlled override |
| **Stressors** | BTC decline only | BTC crash + oracle manipulation + liquidity evaporation + forced liquidations |
| **Market structure** | None — pool arbing disabled, no arbitrageurs | Explicit: ALM/Algo rebalancers, 10 MOET arb agents, liquidity throttling |
| **Oracle** | True price only | Manipulated: wicks (~12%/min), ±volatility noise, 5-min pre-crash attack window |
| **Outcome determinism** | Near-total — initial HF draw determines survival | Emergent from multi-mechanism interaction |
| **Real-world data** | None | None |
| **Primer figure** | §4.2 Figure 2 (performance heatmap) | None identified |

---

## Key Conceptual Differences

**1. Comparative vs absolute framing.** The Monte Carlo sim controls for variables to isolate HT's rebalancing advantage over AAVE. The flash crash pushes HT to its limits without a comparator — it tests whether the protocol parameters survive extreme conditions.

**2. Single vs compound threat model.** The Monte Carlo sim has one stressor (BTC decline); everything else is held constant. The flash crash layers four simultaneous stressors with feedback: BTC crash depresses HF, oracle manipulation misleads rebalancing, liquidity evaporation prevents efficient exit, forced liquidations compound losses.

**3. Deterministic vs path-dependent outcomes.** In the Monte Carlo sim, outcomes are effectively decided at agent creation: given initial HFs and the fixed BTC endpoint, survival is a threshold check (`initial_HF > ~1.31`). Interest accrual over 60 min is negligible (~$0.74 on $65k debt). In the flash crash, the same initial HF for all 150 agents means outcomes depend on the interaction sequence — oracle wick timing, liquidity throttling phase, rebalancing-vs-liquidation race conditions.

**4. Agent heterogeneity vs homogeneity.** The Monte Carlo sim uses random HFs to produce a survival *rate* (e.g., "60% survived" = 3/5 agents above threshold). The flash crash uses 150 agents with identical initial parameters. Agent-level divergence in the flash crash simulation arises from: (1) processing order, i.e. earlier agents get better pool liquidity in the $500k MOET:YT pool; (2) oracle wick timing (~12%/min probability) amplifying queue-position effects; (3) BTC recovery noise (±2%/min) propagating differently through already-diverged portfolios. Whether per-agent random draws or agent-order shuffling occur is unverified.

**5. Market structure: absent vs modeled (but exogenous).** The Monte Carlo sim disables pool arbing — swaps happen in a vacuum. The flash crash explicitly models arbitrageur behavior (ALM/Algo), but liquidity evaporation follows a predetermined schedule rather than emerging from realized losses. Both have incomplete market-structure modeling, in different ways.

---

## Shared Limitations

- Neither uses real-world BTC price data (both synthetic).
- YT pricing is formula-based (10% APR rebasing), not market-observed.
- MOET is treated as $1 in both (the geometric-mean pricing formula is not exercised).
- Neither has been successfully validated against Primer claims. The Monte Carlo sim achieves 1/5 exact AAVE survival matches after fixes; the flash crash has never been run.
- The AAVE agent in the Monte Carlo sim is a stylized passive strategy, not a faithful AAVE protocol implementation.

---

## Cross-References

- Monte Carlo detailed analysis: [`DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md`](../sims-review_commit-da4cbf9/DISCREPANCY-ANALYSIS_balanced_scenario_monte_carlo.md)
- Flash crash code analysis: [`FLASH_CRASH_SIMULATION_SUMMARY.md`](../sims-review_commit-da4cbf9/FLASH_CRASH_SIMULATION_SUMMARY.md)
- Data sources for all sims: [`SIMULATION_DATA_SOURCES.md`](SIMULATION_DATA_SOURCES.md)
