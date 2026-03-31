#!/usr/bin/env python3
"""
FCM Position Maintenance — Cost Estimate Simulation (2022 Bear Market)

Runs a single High Tide agent over the full 2022 year (BTC $46k → $17k, -64%)
with FCM's exact operational constraints:

  - Health check frequency: hourly (every 60 minutes)
  - Max rebalancing cycles per trigger: 1 (one atomic Flow transaction)
  - _check_deleveraging: disabled (not yet modelled as a transaction type)

Outputs the three transaction-type counts needed for the cost formula:

  Total Cost = N_HC_no_action × cost_HC
             + N_SR           × cost_SR
             + N_ER           × cost_ER

See COST_ESTIMATE.md for full framework documentation.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sim_tests.full_year_sim import FullYearSimConfig, FullYearSimulation


def main():
    print("=" * 80)
    print("FCM COST ESTIMATE — 2022 Bear Market (S4 symmetric, single agent)")
    print("=" * 80)
    print("Configuration:")
    print("  - Market: 2022 (Bear, -64.2% BTC)")
    print("  - High Tide HF: ER trigger=1.5 / SR trigger=1.1 / target=1.3  (FlowCreditMarket.cdc)")
    print("  - Rates: Historical AAVE 2022 (symmetric)")
    print("  - Advanced MOET: OFF")
    print("  - Duration: 365 days")
    print("  - Agents: 1 (single FCM position)")
    print("  - Health check frequency: HOURLY (every 60 minutes)")
    print("  - Max rebalance cycles per trigger: 1 (one atomic Flow tx)")
    print("  - _check_deleveraging: DISABLED (not yet modelled)")
    print("=" * 80)

    config = FullYearSimConfig()

    # --- Identity ---
    config.test_name = "FCM_Cost_Estimate_2022_Bear_Hourly_SingleCycle_HF1.5-1.1-1.3"
    config.simulation_duration_hours = 24 * 365      # 365 days = 8,760 hours
    config.simulation_duration_minutes = 365 * 24 * 60  # 525,600 minutes
    config.num_agents = 1

    # --- Market data ---
    config.market_year = 2022
    config.use_historical_btc_data = True
    config.use_historical_aave_rates = True

    # --- Health factors (from FlowCreditMarket.cdc) ---
    config.agent_initial_hf = 1.5      # maxHealth  — ER trigger
    config.agent_rebalancing_hf = 1.1  # minHealth  — SR trigger
    config.agent_target_hf = 1.3       # targetHealth — post-rebalance target
    config.aave_initial_hf = 1.5

    # --- FCM constraints ---
    config.check_frequency_minutes = 60   # Hourly health checks
    config.max_rebalance_cycles = 1       # One atomic Flow transaction per trigger
    config.disable_deleveraging = True    # Exclude weekly harvest from this estimate

    # --- Symmetric study: no Advanced MOET ---
    config.use_advanced_moet = False

    # --- Single agent, no ecosystem growth, HT only ---
    config.run_aave_comparison = False        # High Tide only (no AAVE run)
    config.enable_ecosystem_growth = False

    print("\nStarting simulation...")
    print()

    sim = FullYearSimulation(config)
    results = sim.run_test()

    # --- Extract and print cost estimate outputs ---
    print("\n" + "=" * 80)
    print("FCM COST ESTIMATE RESULTS")
    print("=" * 80)

    # In HT-only mode results are under "simulation_results"; in comparison mode under "high_tide_results"
    raw = (results.get("high_tide_results") or
           results.get("simulation_results") or {})
    agent_outcomes = raw.get("agent_outcomes", [])

    # Filter to HT agents only
    ht_agents = [a for a in agent_outcomes if a.get("agent_type") == "high_tide_agent"]

    if not ht_agents:
        print("ERROR: No High Tide agent outcomes found in results.")
        return

    agent = ht_agents[0]

    hc = agent.get("hc_no_action_count", 0)
    sr = agent.get("sr_count", 0)
    er = agent.get("er_count", 0)
    n_total = hc + sr + er

    print(f"\nTransaction counts:")
    print(f"  N_HC_no_action : {hc:>6}   (health checks — no rebalance needed)")
    print(f"  N_SR           : {sr:>6}   (safety rebalances — HF < {config.agent_rebalancing_hf})")
    print(f"  N_ER           : {er:>6}   (efficiency rebalances — HF > {config.agent_initial_hf})")
    print(f"  N_total        : {n_total:>6}   (≤ 8,760 hourly slots in 365 days)")

    print(f"\nValidation outputs:")
    survived = agent.get("survived", None)
    final_hf = agent.get("final_health_factor", None)
    btc_remaining = agent.get("btc_amount", None)
    moet_debt = agent.get("current_moet_debt", None)
    liq_events = len([e for e in agent.get("rebalancing_events_list", []) if e.get("type") == "liquidation"])

    print(f"  liquidation_events         : {liq_events}   (must be 0)")
    print(f"  survived                   : {survived}")
    print(f"  final_hf                   : {final_hf:.4f}" if final_hf is not None else "  final_hf                   : N/A")
    print(f"  btc_collateral_remaining   : {btc_remaining:.6f} BTC" if btc_remaining is not None else "  btc_collateral_remaining   : N/A")
    print(f"  moet_debt_remaining        : ${moet_debt:,.2f}" if moet_debt is not None else "  moet_debt_remaining        : N/A")

    print(f"\nCost formula (fill in compute unit costs to get USD total):")
    print(f"  Total = {hc} × cost_HC  +  {sr} × cost_SR  +  {er} × cost_ER")

    # --- Build detail report from the agent's rebalance_event_log ---
    _write_rebalance_detail_report(sim, config, final_hf)

    print()
    print(f"Results saved to: tidal_protocol_sim/results/{config.test_name}/")
    print("=" * 80)


def _write_rebalance_detail_report(sim, config, final_hf):
    """Extract per-event rebalance log from the agent and write a CSV report."""
    # Reach into the engine to get the live agent objects
    engine = sim.results.get("ht_engine")

    if engine is None or not hasattr(engine, 'high_tide_agents') or not engine.high_tide_agents:
        print("\n⚠  Could not locate live agent — detail report skipped.")
        return

    agent = engine.high_tide_agents[0]
    log = agent.state.rebalance_event_log

    if not log:
        print("\n⚠  Rebalance event log is empty — detail report skipped.")
        return

    # Write CSV
    out_dir = Path("tidal_protocol_sim/results") / config.test_name
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "fcm_rebalance_detail_report.csv"

    fieldnames = [
        "event_id", "type", "day", "hour_of_day", "minute",
        "btc_price", "pct_price_change_from_prev",
        "prev_type",
        "hf_before", "hf_after",
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in log:
            out = dict(row)
            # Round floats for readability
            if out.get("btc_price") is not None:
                out["btc_price"] = round(out["btc_price"], 2)
            if out.get("pct_price_change_from_prev") is not None:
                out["pct_price_change_from_prev"] = round(out["pct_price_change_from_prev"], 4)
            if out.get("hf_before") is not None:
                out["hf_before"] = round(out["hf_before"], 6)
            if out.get("hf_after") is not None:
                out["hf_after"] = round(out["hf_after"], 6)
            writer.writerow(out)

    total = len(log)
    sr_rows = sum(1 for r in log if r["type"] == "SR")
    er_rows = sum(1 for r in log if r["type"] == "ER")

    print(f"\nDetail report: {csv_path}")
    print(f"  {total} rebalance events  ({sr_rows} SR, {er_rows} ER)")
    print(f"  Columns: event_id | type | day | hour_of_day | minute |")
    print(f"           btc_price | pct_price_change_from_prev | prev_type |")
    print(f"           hf_before | hf_after")

    # Write hourly HF history
    hf_history = agent.state.hf_history
    if hf_history:
        hf_csv_path = out_dir / "fcm_hf_history.csv"
        with open(hf_csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["minute", "hf", "event_type"])
            writer.writeheader()
            for row in hf_history:
                writer.writerow({"minute": row["minute"], "hf": round(row["hf"], 6), "event_type": row["event_type"]})
        print(f"\nHF history: {hf_csv_path}")
        print(f"  {len(hf_history)} data points")


if __name__ == "__main__":
    main()
