from backend.network_manager import NetworkManager
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

    routing = RoutingEngine(
        network.get_network()
    )

    print("\nINTELLIGENT ROUTING TEST")
    print("=" * 70)

    result = routing.find_intelligent_route(
        "PC1",
        "Server"
    )

    print("\nSelected Route:")
    print(" -> ".join(result["path"]))

    print("\nTotal Delay:")
    print(f"{result['delay']} ms")

    print("\nRouting Cost:")
    print(f"{result['cost']:.2f}")
