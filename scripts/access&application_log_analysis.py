import json
import sys
from collections import Counter


def analyze_log(path):
    total = 0
    valid = 0
    malformed = 0

    seen = {}
    duplicates = []

    timestamps = []

    # Keep unique records for further analysis
    unique_records = []

    with open(path) as f:
        for line_number, line in enumerate(f, 1):
            total += 1

            raw = line.rstrip("\n")

            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                malformed += 1
                continue

            valid += 1

            if "timestamp" in record:
                timestamps.append(record["timestamp"])

            key = json.dumps(
                record,
                sort_keys=True,
                separators=(",", ":")
            )

            if key in seen:
                duplicates.append(
                    (seen[key], line_number, record)
                )
            else:
                seen[key] = line_number
                unique_records.append(record)

    # -----------------------------
    # Q1: Basic log statistics
    # -----------------------------

    print(f"File: {path}")
    print(f"Total lines: {total}")
    print(f"Valid JSON: {valid}")
    print(f"Malformed: {malformed}")
    print(f"Exact duplicate records: {len(duplicates)}")

    if timestamps:
        print(f"Earliest timestamp: {min(timestamps)}")
        print(f"Latest timestamp: {max(timestamps)}")

    if duplicates:
        print("\nDuplicates:")
        for first_line, duplicate_line, record in duplicates:
            print(
                f"  lines {first_line} and {duplicate_line}"
                f" | request_id={record.get('request_id')}"
            )

    # -----------------------------
    # Q2/Q3: Client requests
    # -----------------------------

    # Use request_id as the identity of a client request
    requests = {}

    for record in unique_records:
        request_id = record.get("request_id")

        if request_id is not None:
            requests[request_id] = record

    total_requests = len(requests)

    # -----------------------------
    # Q3: Final client status counts
    # -----------------------------

    status_counts = Counter(
        record.get("status")
        for record in requests.values()
    )

    error_count = sum(
        count
        for status, count in status_counts.items()
        if isinstance(status, int) and 400 <= status <= 599
    )

    error_rate = (
        (error_count / total_requests) * 100
        if total_requests
        else 0
    )

    print("\nClient request analysis:")
    print(f"Distinct client requests (denominator): {total_requests}")

    print("\nFinal client status counts:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print(f"\nClient errors (4xx + 5xx): {error_count}")
    print(f"Error rate: {error_rate:.2f}%")


if len(sys.argv) != 2:
    print("Usage: python3 scripts/access_analysis.py <log_file>")
    sys.exit(1)


analyze_log(sys.argv[1])
