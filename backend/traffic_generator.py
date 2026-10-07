import random
from simulation.packet import Packet


class TrafficGenerator:

    def __init__(self, network_manager):
        self.network_manager = network_manager

    def generate_packet(
        self,
        source,
        destination,
        protocol="TCP",
        min_size=256,
        max_size=1500
    ):

        size = random.randint(
            min_size,
            max_size
        )

        packet = Packet(
            source=source,
            destination=destination,
            size=size,
            protocol=protocol
        )

        return packet

    def generate_traffic(
        self,
        source,
        destination,
        count=10
    ):

        protocols = [
            "TCP",
            "UDP",
            "ICMP"
        ]

        packets = []

        for _ in range(count):

            protocol = random.choice(
                protocols
            )

            packet = self.generate_packet(
                source,
                destination,
                protocol
            )

            packets.append(packet)

        return packets
