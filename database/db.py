import sqlite3
from datetime import datetime


class DatabaseManager:

    def __init__(self, database_path="data/netflowsim.db"):

        self.database_path = database_path

        self.create_table()

    def connect(self):

        return sqlite3.connect(
            self.database_path
        )

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

                timestamp TEXT
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
        traffic_mbps,
        utilization,
        congestion,
        packet_loss
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
                packet_loss,
                timestamp
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source,
            destination,
            route,
            delay,
            traffic_mbps,
            utilization,
            congestion,
            packet_loss,
            datetime.now().isoformat()
        ))

        connection.commit()

        connection.close()

    def get_simulations(self):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM simulations
            ORDER BY id DESC
        """)

        results = cursor.fetchall()

        connection.close()

        return results