class CongestionModel:

    def __init__(
        self,
        bandwidth=100,
        queue_capacity=50
    ):

        self.bandwidth = bandwidth
        self.queue_capacity = queue_capacity

    def calculate_load(
        self,
        packet_count,
        average_packet_size
    ):

        total_bits = (
            packet_count *
            average_packet_size *
            8
        )

        return total_bits / 1_000_000

    def calculate_utilization(
        self,
        traffic_mbps
    ):

        if self.bandwidth <= 0:
            return 0

        utilization = (
            traffic_mbps /
            self.bandwidth
        ) * 100

        return min(utilization, 100)

    def congestion_level(
        self,
        utilization
    ):

        if utilization < 40:
            return "LOW"

        elif utilization < 70:
            return "MEDIUM"

        elif utilization < 90:
            return "HIGH"

        return "CRITICAL"

    def packet_loss_probability(
        self,
        utilization
    ):

        if utilization < 70:
            return 0

        if utilization < 90:
            return 2

        if utilization < 100:
            return 5

        return 10

    def queue_status(
        self,
        packet_count
    ):

        if packet_count >= self.queue_capacity:
            return "QUEUE FULL"

        if packet_count >= self.queue_capacity * 0.8:
            return "QUEUE HIGH"

        if packet_count >= self.queue_capacity * 0.5:
            return "QUEUE MEDIUM"

        return "QUEUE LOW"
