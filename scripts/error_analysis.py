import re
import sys
from collections import Counter


CONNECTION_ERROR = re.compile(
    r'^(?P<date>\d{4}/\d{2}/\d{2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'\[(?P<level>\w+)\].*?'
    r'(?P<message>connect\(\) failed \(\d+: [^)]+\) while connecting to upstream),\s+'
    r'request_id=(?P<request_id>[^,]+),\s+'
    r'request:\s+"(?P<method>\S+)\s+(?P<path>\S+)\s+HTTP/[^"]+",\s+'
    r'upstream:\s+"(?P<upstream>[^"]+)"'
)


TIMEOUT_ERROR = re.compile(
    r'^(?P<date>\d{4}/\d{2}/\d{2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'\[(?P<level>\w+)\].*?'
    r'(?P<message>upstream timed out \(\d+: [^)]+\) while reading response header from upstream),\s+'
    r'request_id=(?P<request_id>[^,]+),\s+'
    r'request:\s+"(?P<method>\S+)\s+(?P<path>\S+)\s+HTTP/[^"]+",\s+'
    r'upstream:\s+"(?P<upstream>[^"]+)"'
)


NOTICE = re.compile(
    r'^(?P<date>\d{4}/\d{2}/\d{2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'\[(?P<level>\w+)\]'
)


def analyze_error_log(path):
    total = 0
    parsed_errors = []

    with open(path) as f:
        for line in f:
            total += 1
            raw = line.rstrip("\n")

            match = CONNECTION_ERROR.match(raw)

            if not match:
                match = TIMEOUT_ERROR.match(raw)

            if match:
                record = match.groupdict()

                # Keep the complete original log line
                # for exact duplicate detection.
                record["raw"] = raw

                record["timestamp"] = (
                    f"{record.pop('date')}T{record.pop('time')}Z"
                )

                parsed_errors.append(record)

    print(f"File: {path}")
    print(f"Total lines: {total}")
    print(f"Parsed error records: {len(parsed_errors)}")

    if not parsed_errors:
        return

    timestamps = [record["timestamp"] for record in parsed_errors]
    request_ids = [record["request_id"] for record in parsed_errors]
    paths = [record["path"] for record in parsed_errors]
    upstreams = [record["upstream"] for record in parsed_errors]

    print(f"Earliest error timestamp: {min(timestamps)}")
    print(f"Latest error timestamp: {max(timestamps)}")

    print(f"\nDistinct error request IDs: {len(set(request_ids))}")

    print("\nError categories:")

    categories = []

    for record in parsed_errors:
        message = record["message"]

        if message.startswith("connect() failed"):
            category = "connection refused"
        elif message.startswith("upstream timed out"):
            category = "upstream timeout"
        else:
            category = "other"

        categories.append(category)

    for category, count in Counter(categories).items():
        print(f"  {category}: {count}")

    print("\nPaths:")

    for path_name, count in Counter(paths).items():
        print(f"  {path_name}: {count}")

    print("\nUpstreams:")

    for upstream, count in Counter(upstreams).items():
        print(f"  {upstream}: {count}")

    # Exact duplicate records:
    # the complete original log line must be identical.
    exact_duplicate_counts = Counter(
        record["raw"] for record in parsed_errors
    )

    exact_duplicates = {
        raw: count
        for raw, count in exact_duplicate_counts.items()
        if count > 1
    }

    print("\nExact duplicate error records:")

    if not exact_duplicates:
        print("  None")
    else:
        total_duplicate_occurrences = 0

        for raw, count in exact_duplicates.items():
            total_duplicate_occurrences += count

            print(f"  {count} occurrences")
            print(f"    {raw}")

        print(
            f"\nTotal duplicate occurrences: "
            f"{total_duplicate_occurrences}"
        )

        print(
            f"Unique duplicated records: "
            f"{len(exact_duplicates)}"
        )


if len(sys.argv) != 2:
    print("Usage: python3 scripts/error_analysis.py <error_log>")
    sys.exit(1)


analyze_error_log(sys.argv[1])
