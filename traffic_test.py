from backend.network_manager import NetworkManager
from backend.traffic_generator import TrafficGenerator
from algorithms.routing import RoutingEngine


def build_network():

    network = NetworkManager()

    network.add_node("PC1", "computer")
    network.add_node("PC2", "computer")
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
        "PC2",
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

    traffic = TrafficGenerator(network)

    routing = RoutingEngine(network.get_network())

    packets = traffic.generate_traffic(
        source="PC1",
        destination="Server",
        count=10
    )

    print("\nGENERATED NETWORK TRAFFIC")
    print("=" * 70)

    for packet in packets:

        route = routing.find_best_route(
            packet.source,
            packet.destination
        )

        print(f"\nPacket ID: {packet.packet_id}")
        print(f"Source: {packet.source}")
        print(f"Destination: {packet.destination}")
        print(f"Protocol: {packet.protocol}")
        print(f"Size: {packet.size} bytes")
        print(f"Route: {' -> '.join(route['path'])}")
        print(f"Delay: {route['delay']} ms")
