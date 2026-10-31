
import os
import sys
import random
import time
from datetime import datetime

PROJECT_DIR = r"C:\Hadoop\web-log-project"
REALTIME_DIR = os.path.join(PROJECT_DIR, "realtime", "input")
OUTPUT_FILE = os.path.join(REALTIME_DIR, "live_access.log")

CLIENTS = [
    "192.168.1.10",
    "192.168.1.20",
    "192.168.1.30",
    "10.0.0.15",
    "10.0.0.25",
    "student.example.com",
    "admin.example.com",
    "visitor.example.com",
]

NORMAL_PATHS = [
    "/", "/index.html", "/about.html",
    "/products.html", "/contact.html", "/images/logo.png"
]

ERROR_PATHS = [
    "/missing-page.html", "/admin/login",
    "/private/data", "/api/unknown"
]

USER_AGENTS = [
    "Mozilla/5.0",
    "Chrome/120.0",
    "Firefox/115.0",
    "Python-requests/2.31",
]


def generate_log_entry(anomaly_mode=False):
    """Generate one synthetic HTTP access-log entry."""

    client = random.choice(CLIENTS)
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")

    if anomaly_mode:
        # Deliberately generate repeated selected HTTP errors.
        path = random.choice(ERROR_PATHS)
        status = random.choice([403, 404, 404, 500, 501])
    else:
        path = random.choice(NORMAL_PATHS)
        status = random.choices(
            [200, 302, 304, 404],
            weights=[80, 8, 10, 2],
            k=1
        )[0]

    size = random.randint(100, 5000)
    agent = random.choice(USER_AGENTS)

    return (
        f'{client} - - [{timestamp}] '
        f'"GET {path} HTTP/1.1" '
        f'{status} {size} "-" "{agent}"\n'
    )


def main():
    os.makedirs(REALTIME_DIR, exist_ok=True)

    print("=" * 55)
    print("INTERACTIVE SIMULATED WEB TRAFFIC GENERATOR")
    print("=" * 55)
    print("1. Normal traffic")
    print("2. Anomaly traffic")
    print("3. Exit")

    if not sys.stdin.isatty():
        choice = sys.stdin.readline().strip()
    else:
        choice = input("Select a mode (1/2/3): ").strip()

    if choice == "3":
        print("Simulator closed.")
        return

    if choice not in ("1", "2"):
        print("Invalid choice. Run the program again and select 1, 2, or 3.")
        return

    anomaly_mode = choice == "2"
    mode_name = "ANOMALY" if anomaly_mode else "NORMAL"

    batch_size = 20
    interval_seconds = 1
    total_written = 0

    print(f"\nSelected mode: {mode_name}")
    print(f"Output file: {OUTPUT_FILE}")
    print("Generating 20 log entries per second.")
    print("Press Ctrl+C to stop the simulator.\n")

    try:
        # Append entries so the running monitor can process new traffic.
        with open(
            OUTPUT_FILE, "a", encoding="utf-8", buffering=1
        ) as output:

            while True:
                for _ in range(batch_size):
                    output.write(generate_log_entry(anomaly_mode))
                    total_written += 1

                output.flush()

                print(
                    f"Mode={mode_name} | "
                    f"Generated this run={total_written:,}"
                )

                time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
        print(f"Total entries generated this run: {total_written:,}")


if __name__ == "__main__":
    main()

