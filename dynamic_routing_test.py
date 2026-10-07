from backend.network_manager import NetworkManager
from backend.simulation_engine import SimulationEngine
from algorithms.routing import RoutingEngine


def build_network():

    network = NetworkManager()

    network.add_node("PC1", "computer")
    network.add_node("Router1", "router")
    network.add_node("Router2", "router")
    network.add_node("Router3", "router")
    network.add_node("Server", "server")

    network.add_link(
        "PC1",
        "Router1",
        bandwidth=100,
        delay=10
    )

    network.add_link(
        "Router1",
        "Router2",
        bandwidth=100,
        delay=20
    )

    network.add_link(
        "Router2",
        "Server",
        bandwidth=100,
        delay=15
    )

    network.add_link(
        "Router1",
        "Router3",
        bandwidth=100,
        delay=40
    )

    network.add_link(
        "Router3",
        "Server",
        bandwidth=100,
        delay=10
    )

    return network


if __name__ == "__main__":

    network = build_network()

    simulation = SimulationEngine(network)

    routing = RoutingEngine(
        network.get_network()
    )

    print("\nDYNAMIC CONGESTION-AWARE ROUTING")
    print("=" * 70)

    print("\nSTEP 1: NORMAL NETWORK")
    print("-" * 70)

    result = routing.find_intelligent_route(
        "PC1",
        "Server"
    )

    print(
        "Selected Route:",
        " -> ".join(result["path"])
    )

    print(
        "Delay:",
        result["delay"],
        "ms"
    )

    print("\nSTEP 2: SIMULATING HEAVY TRAFFIC")
    print("-" * 70)

    simulation.simulate_link_traffic(
        "Router1",
        "Router2",
        packet_count=11875,
        average_packet_size=1000
    )

    simulation.simulate_link_traffic(
        "Router2",
        "Server",
        packet_count=11875,
        average_packet_size=1000
    )

    print("\nLINK STATUS")
    print("-" * 70)

    for link in simulation.get_network_status():

        print(
            f"{link['source']} -> {link['destination']} | "
            f"Utilization: {link['utilization']:.1f}% | "
            f"Congestion: {link['congestion']} | "
            f"Packet Loss: {link['packet_loss']}%"
        )

    print("\nSTEP 3: SELECTING NEW ROUTE")
    print("-" * 70)

    result = routing.find_intelligent_route(
        "PC1",
        "Server"
    )
    simulation.save_route_result(
    source="PC1",
    destination="Server",
    route_result=result,
    traffic_mbps=95,
    utilization=95,
    congestion="CRITICAL",
    packet_loss=5
)

    print(
        "Selected Route:",
        " -> ".join(result["path"])
    )

    print(
        "Delay:",
        result["delay"],
        "ms"
    )

    print(
        "Routing Cost:",
        f"{result['cost']:.2f}"
    )