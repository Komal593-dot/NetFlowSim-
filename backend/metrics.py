class NetworkMetrics:

    @staticmethod
    def transmission_time(packet_size_bytes, bandwidth_mbps):

        if bandwidth_mbps <= 0:
            return 0

        packet_size_bits = packet_size_bytes * 8

        bandwidth_bits_per_second = bandwidth_mbps * 1_000_000

        time_seconds = (
            packet_size_bits /
            bandwidth_bits_per_second
        )

        return time_seconds * 1000

    @staticmethod
    def throughput(total_data_bytes, total_time_ms):

        if total_time_ms <= 0:
            return 0

        total_data_bits = total_data_bytes * 8

        total_time_seconds = total_time_ms / 1000

        throughput_mbps = (
            total_data_bits /
            total_time_seconds /
            1_000_000
        )

        return throughput_mbps

    @staticmethod
    def bandwidth_utilization(
        data_bytes,
        duration_ms,
        bandwidth_mbps
    ):

        if duration_ms <= 0 or bandwidth_mbps <= 0:
            return 0

        data_bits = data_bytes * 8

        duration_seconds = duration_ms / 1000

        actual_rate_mbps = (
            data_bits /
            duration_seconds /
            1_000_000
        )

        utilization = (
            actual_rate_mbps /
            bandwidth_mbps
        ) * 100

        return min(utilization, 100)

    @staticmethod
    def packet_loss(sent, lost):

        if sent <= 0:
            return 0

        return (lost / sent) * 100
