from backend.metrics import NetworkMetrics
from database.db import DatabaseManager
from algorithms.routing import RoutingEngine


class SimulationEngine:

    def __init__(self, network_manager):
        self.network_manager = network_manager
        self.metrics = NetworkMetrics()
        self.database = DatabaseManager()

    def simulate_link_traffic(
        self,
        source,
        destination,
        packet_count,
        average_packet_size
    ):
        network = self.network_manager.get_network()

        # If direct edge exists, simulate on that single edge
        if network.has_edge(source, destination):
            path = [source, destination]
        else:
            # Multi-hop path: use RoutingEngine to find path across intermediate nodes
            routing_engine = RoutingEngine(network)
            route_res = routing_engine.find_intelligent_route(source, destination)
            if not route_res or "path" not in route_res:
                return None
            path = route_res["path"]

        total_data_bytes = packet_count * average_packet_size
        total_data_bits = total_data_bytes * 8
        traffic_mbps = total_data_bits / 1_000_000

        max_utilization = 0
        overall_congestion = "LOW"
        max_packet_loss = 0

        # Update metrics across every link segment along the path
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if not network.has_edge(u, v):
                continue

            edge = network[u][v]
            bandwidth = edge.get("bandwidth", 100)

            if bandwidth <= 0:
                utilization = 100.0
            else:
                utilization = min((traffic_mbps / bandwidth) * 100, 100.0)

            if utilization < 40:
                congestion = "LOW"
                packet_loss = 0
            elif utilization < 70:
                congestion = "MEDIUM"
                packet_loss = 0
            elif utilization < 90:
                congestion = "HIGH"
                packet_loss = 2
            else:
                congestion = "CRITICAL"
                packet_loss = 5 if utilization < 100 else 10

            edge["utilization"] = utilization
            edge["packet_loss"] = packet_loss
            edge["congestion"] = congestion
            edge["traffic_mbps"] = traffic_mbps
            edge["queue_size"] = min(packet_count, 50)

            if utilization > max_utilization:
                max_utilization = utilization
                overall_congestion = congestion
                max_packet_loss = packet_loss

        return {
            "source": source,
            "destination": destination,
            "traffic_mbps": traffic_mbps,
            "utilization": max_utilization,
            "congestion": overall_congestion,
            "packet_loss": max_packet_loss,
            "queue_size": min(packet_count, 50)
        }

    def save_route_result(
        self,
        source,
        destination,
        route_result,
        traffic_mbps=0,
        utilization=0,
        congestion="LOW",
        packet_loss=0
    ):
        route = " -> ".join(route_result["path"])

        self.database.save_simulation(
            source=source,
            destination=destination,
            route=route,
            delay=route_result["delay"],
            traffic_mbps=traffic_mbps,
            utilization=utilization,
            congestion=congestion,
            packet_loss=packet_loss
        )

    def get_network_status(self):
        network = self.network_manager.get_network()
        status = []

        for source, destination, data in network.edges(data=True):
            status.append({
                "source": source,
                "destination": destination,
                "bandwidth": data.get("bandwidth", 100),
                "traffic_mbps": data.get("traffic_mbps", 0),
                "utilization": data.get("utilization", 0),
                "congestion": data.get("congestion", "LOW"),
                "packet_loss": data.get("packet_loss", 0),
                "queue_size": data.get("queue_size", 0)
            })

        return status