"""
Simulation Runner
Entry point for running the full city-scale simulation.
"""
import os
import sys
import asyncio

# Add paths
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
ml_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")
sys.path.insert(0, backend_dir)
sys.path.insert(0, ml_dir)

from simulation import SimulationEngine


async def run_standalone_simulation():
    """Run the simulation without the web server (CLI mode)."""
    print("=" * 60)
    print("Food Delivery Route Optimizer - Simulation Runner")
    print("=" * 60)

    engine = SimulationEngine()
    engine.initialize()

    print(f"\nSimulation Parameters:")
    print(f"  Orders: {len(engine.orders)}")
    print(f"  Drivers: {len(engine.drivers)}")
    print(f"  Graph Nodes: {engine.graph.number_of_nodes()}")
    print(f"  Graph Edges: {engine.graph.number_of_edges()}")
    print()

    # Run simulation with console output
    async def console_output(state):
        metrics = state["metrics"]
        tick = metrics["tick"]
        if tick % 5 == 0:  # Print every 5 ticks
            print(
                f"  Tick {tick:4d} | "
                f"Released: {metrics['total_orders_released']:4d} | "
                f"Pending: {metrics['orders_pending']:4d} | "
                f"Transit: {metrics['orders_in_transit']:4d} | "
                f"Delivered: {metrics['orders_delivered']:4d} | "
                f"Active Drivers: {metrics['active_drivers']:2d} | "
                f"Avg Time: {metrics['avg_delivery_time_min']:.1f}min"
            )

    print("Starting simulation...")
    print("-" * 100)
    await engine.run(ws_broadcast_callback=console_output)
    print("-" * 100)

    print(f"\nFinal Metrics:")
    for key, value in engine.metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(run_standalone_simulation())
