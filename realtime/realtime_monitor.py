import os
import re
import csv
import time
from collections import defaultdict, deque
from datetime import datetime

PROJECT_DIR = r"C:\Hadoop\web-log-project"

INPUT_FILE = os.path.join(
    PROJECT_DIR, "realtime", "input", "live_access.log"
)
ALERT_DIR = os.path.join(PROJECT_DIR, "realtime", "alerts")
ALERT_FILE = os.path.join(ALERT_DIR, "realtime_alerts.csv")
METRICS_FILE = os.path.join(ALERT_DIR, "realtime_metrics.csv")

POLL_INTERVAL = 0.5
METRICS_INTERVAL = 2
MIN_REQUESTS_FOR_ALERT = 30
MIN_ERRORS_FOR_ALERT = 10
ERROR_CODES = {403, 404, 500, 501}

LOG_PATTERN = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+'
    r'"([^"]*)"\s+(\d{3})\s+(\S+)'
)

client_requests = defaultdict(int)
client_errors = defaultdict(int)
recent_requests = defaultdict(deque)
last_alert_time = {}
ALERT_COOLDOWN_SECONDS = 15

processed_lines = 0
invalid_lines = 0
total_errors = 0

interval_requests = 0
interval_errors = 0
interval_status_counts = defaultdict(int)


def prepare_files():
    os.makedirs(ALERT_DIR, exist_ok=True)

    if not os.path.exists(ALERT_FILE) or os.path.getsize(ALERT_FILE) == 0:
        with open(ALERT_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow([
                "Detection_Time", "Client", "Reason", "Total_Requests",
                "Selected_HTTP_Errors", "HTTP_Status"
            ])

    if not os.path.exists(METRICS_FILE) or os.path.getsize(METRICS_FILE) == 0:
        with open(METRICS_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow([
                "Timestamp", "Requests", "Selected_HTTP_Errors",
                "HTTP_403", "HTTP_404", "HTTP_500", "HTTP_501",
                "Total_Processed"
            ])


def write_alert(client, reason, status):
    with open(ALERT_FILE, "a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow([
            datetime.now().isoformat(timespec="seconds"),
            client,
            reason,
            client_requests[client],
            client_errors[client],
            status
        ])

    print(
        f"\n[POTENTIAL ANOMALY] Client={client} | Reason={reason} | "
        f"Requests={client_requests[client]} | Errors={client_errors[client]}",
        flush=True
    )


def save_metrics():
    global interval_requests, interval_errors

    with open(METRICS_FILE, "a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow([
            datetime.now().isoformat(timespec="seconds"),
            interval_requests,
            interval_errors,
            interval_status_counts[403],
            interval_status_counts[404],
            interval_status_counts[500],
            interval_status_counts[501],
            processed_lines
        ])

    interval_requests = 0
    interval_errors = 0
    interval_status_counts.clear()


def process_line(line):
    global processed_lines, invalid_lines, total_errors
    global interval_requests, interval_errors

    match = LOG_PATTERN.match(line.strip())
    if not match:
        invalid_lines += 1
        return

    client, _source_timestamp, _request, status_text, _size = match.groups()
    status = int(status_text)

    processed_lines += 1
    client_requests[client] += 1
    interval_requests += 1
    interval_status_counts[status] += 1

    if status in ERROR_CODES:
        client_errors[client] += 1
        total_errors += 1
        interval_errors += 1

    now = time.time()
    recent = recent_requests[client]
    recent.append(now)
    while recent and now - recent[0] > 10:
        recent.popleft()

    reason = None
    if len(recent) >= MIN_REQUESTS_FOR_ALERT:
        reason = f"{len(recent)} requests observed within 10 seconds"
    elif client_errors[client] >= MIN_ERRORS_FOR_ALERT:
        reason = f"{client_errors[client]} selected HTTP errors observed"

    if reason:
        current_time = time.time()
        previous_alert = last_alert_time.get(client, 0)

        if current_time - previous_alert >= ALERT_COOLDOWN_SECONDS:
            last_alert_time[client] = current_time
            write_alert(client, reason, status)


def main():
    prepare_files()

    print("=" * 65)
    print("REAL-TIME WEB LOG MONITOR")
    print("=" * 65)
    print(f"Input:   {INPUT_FILE}")
    print(f"Alerts:  {ALERT_FILE}")
    print(f"Metrics: {METRICS_FILE}")
    print("Waiting for new log entries. Press Ctrl+C to stop.\n", flush=True)

    if not os.path.isfile(INPUT_FILE):
        print("ERROR: Input file not found. Start the log generator first.")
        return

    # Begin at EOF: only records appended after monitor startup are processed.
    with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as logfile:
        logfile.seek(0, os.SEEK_END)
        last_report = time.time()
        last_metrics = time.time()

        try:
            while True:
                line = logfile.readline()
                if line:
                    process_line(line)
                else:
                    time.sleep(POLL_INTERVAL)

                now = time.time()
                if now - last_metrics >= METRICS_INTERVAL:
                    # Save zero-count intervals too, so graphs show idle periods.
                    save_metrics()
                    last_metrics = now

                if now - last_report >= 5:
                    print(
                        f"[STATUS] Processed={processed_lines:,} | "
                        f"Clients={len(client_requests):,} | "
                        f"Selected errors={total_errors:,} | "
                        f"Invalid lines={invalid_lines:,}",
                        flush=True
                    )
                    last_report = now

        except KeyboardInterrupt:
            if interval_requests > 0 or interval_errors > 0:
                save_metrics()
            print("\nMonitoring stopped.")
            print(f"Processed entries: {processed_lines:,}")
            print(f"Unique clients: {len(client_requests):,}")
            print(f"Selected HTTP errors: {total_errors:,}")
            print(f"Invalid entries: {invalid_lines:,}")
            print(f"Alerts file: {ALERT_FILE}")
            print(f"Metrics file: {METRICS_FILE}")


if __name__ == "__main__":
    main()
