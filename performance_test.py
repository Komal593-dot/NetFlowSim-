from backend.metrics import NetworkMetrics
from simulation.congestion import CongestionModel


if __name__ == "__main__":

    print("\nNETWORK PERFORMANCE TEST")
    print("=" * 70)

    packet_size = 1000
    bandwidth = 100

    transmission = NetworkMetrics.transmission_time(
        packet_size,
        bandwidth
    )

    print(f"\nPacket Size: {packet_size} bytes")
    print(f"Bandwidth: {bandwidth} Mbps")
    print(f"Transmission Time: {transmission:.4f} ms")

    congestion = CongestionModel(
        bandwidth=100,
        queue_capacity=50
    )

    traffic_levels = [
        20,
        50,
        75,
        95,
        110
    ]

    print("\nCONGESTION ANALYSIS")
    print("-" * 70)

    for traffic in traffic_levels:

        utilization = congestion.calculate_utilization(
            traffic
        )

        level = congestion.congestion_level(
            utilization
        )

        loss = congestion.packet_loss_probability(
            utilization
        )

        queue = congestion.queue_status(
            int(traffic / 2)
        )

        print(
            f"Traffic: {traffic:>3} Mbps | "
            f"Utilization: {utilization:>5.1f}% | "
            f"Congestion: {level:<8} | "
            f"Packet Loss: {loss:>2}% | "
            f"{queue}"
        )
