import networkx as nx


class NetworkManager:

    def __init__(self):
        self.network = nx.Graph()

    def add_node(self, name, node_type="router"):
        self.network.add_node(
            name,
            type=node_type
        )

    def add_link(
        self,
        source,
        destination,
        bandwidth=100,
        delay=10,
        packet_loss=0.0
    ):
        self.network.add_edge(
            source,
            destination,
            bandwidth=bandwidth,
            delay=delay,
            packet_loss=packet_loss
        )

    def remove_node(self, name):
        if name in self.network:
            self.network.remove_node(name)

    def remove_link(self, source, destination):
        if self.network.has_edge(source, destination):
            self.network.remove_edge(source, destination)

    def get_nodes(self):
        return list(self.network.nodes(data=True))

    def get_links(self):
        return list(self.network.edges(data=True))

    def get_neighbors(self, node):
        return list(self.network.neighbors(node))

    def get_network(self):
        return self.network

    def display_network(self):
        print("\nNETWORK NODES")
        print("-" * 40)

        for node, data in self.network.nodes(data=True):
            print(f"{node} -> {data['type']}")

        print("\nNETWORK LINKS")
        print("-" * 60)

        for source, destination, data in self.network.edges(data=True):
            print(
                f"{source} <-> {destination} | "
                f"Bandwidth: {data['bandwidth']} Mbps | "
                f"Delay: {data['delay']} ms | "
                f"Packet Loss: {data['packet_loss']}%"
            )
