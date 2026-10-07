import os
import sqlite3

class DatabaseManager:

    def __init__(self, db_path="data/netflowsim.db"):
        self.database_path = db_path
        # Ensure the target directory exists before opening SQLite connection
        db_dir = os.path.dirname(self.database_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception:
                # Fallback to current working directory if folder creation fails
                self.database_path = "netflowsim.db"

        self.create_table()

    def connect(self):
        try:
            return sqlite3.connect(self.database_path, check_same_thread=False)
        except sqlite3.OperationalError:
            # Secondary fallback if path is read-only
            self.database_path = "netflowsim.db"
            return sqlite3.connect(self.database_path, check_same_thread=False)

    def create_table(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                destination TEXT,
                route TEXT,
                delay REAL,
                traffic_mbps REAL,
                utilization REAL,
                congestion TEXT,
                packet_loss REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        connection.close()

    def save_simulation(
        self,
        source,
        destination,
        route,
        delay,
        traffic_mbps=0,
        utilization=0,
        congestion="LOW",
        packet_loss=0
    ):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO simulations (
                source,
                destination,
                route,
                delay,
                traffic_mbps,
                utilization,
                congestion,
                packet_loss
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source,
            destination,
            route,
            delay,
            traffic_mbps,
            utilization,
            congestion,
            packet_loss
        ))

        connection.commit()
        connection.close()

    def get_simulations(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, source, destination, route, delay, traffic_mbps, utilization, congestion, packet_loss, timestamp
            FROM simulations
            ORDER BY timestamp DESC
        """)

        records = cursor.fetchall()
        connection.close()
        return records