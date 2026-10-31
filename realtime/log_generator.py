
import os
import time

# Project paths
PROJECT_DIR = r"C:\Hadoop\web-log-project"

SOURCE_FILE = os.path.join(
    PROJECT_DIR, "data", "access_log_Jul95"
)

REALTIME_DIR = os.path.join(
    PROJECT_DIR, "realtime", "input"
)

OUTPUT_FILE = os.path.join(
    REALTIME_DIR, "live_access.log"
)

# Simulation settings
BATCH_SIZE = 20
INTERVAL_SECONDS = 1

def main():
    if not os.path.isfile(SOURCE_FILE):
        print(f"ERROR: Source log file not found: {SOURCE_FILE}")
        return

    os.makedirs(REALTIME_DIR, exist_ok=True)

    print("=" * 60)
    print("REAL-TIME WEB LOG GENERATOR")
    print("=" * 60)
    print(f"Source: {SOURCE_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Batch size: {BATCH_SIZE} log entries")
    print(f"Interval: {INTERVAL_SECONDS} second(s)")
    print("\nPress Ctrl+C to stop.\n")

    total_written = 0

    try:
        # Start from the beginning of the historical dataset.
        with open(SOURCE_FILE, "r", encoding="latin-1") as source:
            # Create a fresh simulation output file.
            with open(
                OUTPUT_FILE,"a", encoding="utf-8", buffering=1
            ) as output:

                while True:
                    batch_count = 0

                    for _ in range(BATCH_SIZE):
                        line = source.readline()

                        if not line:
                            print("\nEnd of NASA dataset reached.")
                            print(f"Total entries written: {total_written:,}")
                            return

                        output.write(line)
                        batch_count += 1
                        total_written += 1

                    output.flush()

                    print(
                        f"Written: {total_written:,} entries "
                        f"| Latest batch: {batch_count}"
                    )

                    time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        print(f"Total entries written: {total_written:,}")

if __name__ == "__main__":
    main()

