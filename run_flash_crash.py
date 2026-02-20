#!/usr/bin/env python3
"""
Flash Crash Simulation Runner

Simple script to run flash crash simulations with different scenarios.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sim_tests.flash_crash_simulation import FlashCrashSimulation, FlashCrashSimConfig


def run_scenario(scenario_name: str):
    """Run a specific flash crash scenario"""
    
    print(f"🚀 Running Flash Crash Simulation - {scenario_name.upper()} Scenario")
    print("=" * 70)
    
    # Create configuration for the scenario
    config = FlashCrashSimConfig(scenario_name)
    
    # Display scenario details
    print(f"📊 Scenario Details:")
    print(f"   YT Crash: {config.yt_crash_magnitude:.0%} drop")
    print(f"   BTC Crash: {config.btc_crash_magnitude:.0%} drop")
    print(f"   Liquidity Reduction: {config.liquidity_reduction_start:.0%} → {config.liquidity_reduction_peak:.0%}")
    
    # `oracle_outlier_magnitude` doesn't exist anywhere in the codebase. This script is not able to run in the form we received it.
    # print(f"   Oracle Outliers: {config.oracle_outlier_magnitude:.0%}")
    #
    # replaced with `oracle_volatility` and `yt_wick_magnitude` for the following reason:
    # The intent of that print presumably was to show the oracle-related stress parameter for the selected scenario. `oracle_volatility` is the only scenario-varying 
    # oracle parameter (5% / 8% / 12% for mild/moderate/severe). The other two oracle config fields (`oracle_outlier_duration_minutes = 5` and `extreme_tick_magnitude = 0.45`) 
    # are scenario-independent constants, so they wouldn't be meaningful to display in a per-scenario summary.
    print(f"   Oracle Volatility: ±{config.oracle_volatility:.0%} per tick") # parameter is the ±% random walk applied at each tick during the crash
    print(f"   Oracle Wicks: {config.yt_wick_magnitude:.0%} drop per wick event (~12% chance/min during crash)") # magnitude of sharp drop (wick event) during the crash

    print(f"   Duration: {config.simulation_duration_minutes:,} minutes ({config.simulation_duration_minutes//1440} days)")
    print(f"   Agents: {config.num_agents} with ${config.target_total_debt:,.0f} target debt")
    print()
    
    # Run the simulation
    simulation = FlashCrashSimulation(config)
    results = simulation.run_flash_crash_test()
    
    return results


def main():
    """Main runner function"""
    
    print("Flash Crash Simulation Runner")
    print("=" * 40)
    print()
    
    # Available scenarios
    scenarios = {
        "1": ("mild", "35% YT drop, 12% BTC drop, 60% liquidity reduction"),
        "2": ("moderate", "50% YT drop, 20% BTC drop, 70% liquidity reduction"),
        "3": ("severe", "70% YT drop, 25% BTC drop, 80% liquidity reduction")
    }
    
    print("Available scenarios:")
    for key, (name, description) in scenarios.items():
        print(f"  {key}. {name.title()}: {description}")
    print()
    
    # Get user choice or default to moderate
    choice = input("Select scenario (1-3) or press Enter for moderate: ").strip()
    
    if choice in scenarios:
        scenario_name = scenarios[choice][0]
    elif choice == "":
        scenario_name = "moderate"
    else:
        print(f"Invalid choice '{choice}', defaulting to moderate scenario")
        scenario_name = "moderate"
    
    print()
    
    try:
        results = run_scenario(scenario_name)
        
        if results:
            print("\n✅ Simulation completed successfully!")
            print(f"📁 Results saved in: tidal_protocol_sim/results/Flash_Crash_YT_BTC_{scenario_name.title()}_Scenario/")
            
            # Quick summary
            agent_perf = results.get("agent_performance", {})
            if agent_perf:
                print(f"\n📊 Quick Summary:")
                print(f"   Survival Rate: {agent_perf.get('survival_rate', 0):.1%}")
                print(f"   Liquidation Events: {agent_perf.get('total_liquidation_events', 0)}")
                print(f"   Oracle Events: {agent_perf.get('oracle_manipulation_events', 0)}")
        else:
            print("\n❌ Simulation failed or was interrupted")
            
    except Exception as e:
        print(f"\n❌ Error running simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
