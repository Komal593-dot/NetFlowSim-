import networkx as nx


class RoutingEngine:

    def __init__(self, network):
        self.network = network

    def shortest_path(self, source, destination):

        path = nx.shortest_path(
            self.network,
            source=source,
            target=destination,
            weight="delay"
        )

        return path

    def calculate_path_delay(self, path):

        total_delay = 0

        for i in range(len(path) - 1):

            source = path[i]
            destination = path[i + 1]

            edge_data = self.network.get_edge_data(
                source,
                destination
            )

            total_delay += edge_data["delay"]

        return total_delay

    def calculate_path_cost(self, path):

        total_cost = 0

        for i in range(len(path) - 1):

            source = path[i]
            destination = path[i + 1]

            edge_data = self.network.get_edge_data(
                source,
                destination
            )

            delay = edge_data.get("delay", 0)
            utilization = edge_data.get("utilization", 0)
            packet_loss = edge_data.get("packet_loss", 0)

            cost = (
                delay
                + (utilization * 0.5)
                + (packet_loss * 5)
            )

            total_cost += cost

        return total_cost

    def find_best_route(self, source, destination):

        path = self.shortest_path(
            source,
            destination
        )

        delay = self.calculate_path_delay(path)

        return {
            "path": path,
            "delay": delay
        }

    def find_intelligent_route(
        self,
        source,
        destination
    ):

        paths = list(
            nx.all_simple_paths(
                self.network,
                source=source,
                target=destination
            )
        )

        if not paths:
            return None

        best_path = None
        best_cost = float("inf")

        for path in paths:

            cost = self.calculate_path_cost(path)

            if cost < best_cost:

                best_cost = cost
                best_path = path

        delay = self.calculate_path_delay(
            best_path
        )

        return {
            "path": best_path,
            "delay": delay,
            "cost": best_cost
        }
