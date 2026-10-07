from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Packet:

    source: str
    destination: str
    size: int
    protocol: str = "TCP"

    packet_id: str = None
    created_at: str = None

    def __post_init__(self):

        if self.packet_id is None:
            self.packet_id = str(uuid.uuid4())[:8]

        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def information(self):

        return {
            "packet_id": self.packet_id,
            "source": self.source,
            "destination": self.destination,
            "size": self.size,
            "protocol": self.protocol,
            "created_at": self.created_at
        }
