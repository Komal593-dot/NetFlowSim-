from database.db import DatabaseManager


if __name__ == "__main__":

    db = DatabaseManager()

    db.save_simulation(
        source="PC1",
        destination="Server",
        route="PC1 -> Router1 -> Router2 -> Server",
        delay=45,
        traffic_mbps=95,
        utilization=95,
        congestion="CRITICAL",
        packet_loss=5
    )

    results = db.get_simulations()

    print("\nDATABASE TEST")
    print("=" * 70)

    for row in results:
        print(row)