#!/usr/bin/env python3

"""Test backend failure and continued availability."""

import json
import subprocess
import sys
import time

BACKEND_TO_STOP = "app-01"
OTHER_BACKEND = "app-02"
URL = "http://127.0.0.1:8080/instance"

REQUEST_COUNT = 10
REQUEST_TIMEOUT = 2


def is_running(service):
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", service],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0 and result.stdout.strip() == "true"


def stop_backend():
    result = subprocess.run(
        ["docker", "stop", BACKEND_TO_STOP],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[FAIL] Could not stop {BACKEND_TO_STOP}")
        return False

    print(f"[PASS] Stopped {BACKEND_TO_STOP}")
    return True


def start_backend():
    result = subprocess.run(
        ["docker", "start", BACKEND_TO_STOP],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[FAIL] Could not start {BACKEND_TO_STOP}")
        return False

    print(f"[PASS] Started {BACKEND_TO_STOP}")
    return True


def request_instance():
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "--max-time",
            str(REQUEST_TIMEOUT),
            URL,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    return data.get("instance_id")


def test_continued_availability():
    observed_instances = []
    failed_requests = 0

    for _ in range(REQUEST_COUNT):
        instance_id = request_instance()

        if instance_id is None:
            failed_requests += 1
        else:
            observed_instances.append(instance_id)

        time.sleep(0.2)

    print(
        f"During failure: {len(observed_instances)} successful requests, "
        f"{failed_requests} failed requests"
    )

    if failed_requests == 0 and all(
        instance == OTHER_BACKEND for instance in observed_instances
    ):
        print(
            f"[PASS] Traffic continued through {OTHER_BACKEND} "
            f"while {BACKEND_TO_STOP} was stopped"
        )
        return True

    print(
        f"[FAIL] Traffic was not served correctly during "
        f"{BACKEND_TO_STOP} failure"
    )

    if observed_instances:
        print(f"Observed instances: {sorted(set(observed_instances))}")

    return False


def main():
    # Do not start with a backend already down.
    if not is_running(BACKEND_TO_STOP):
        print(
            f"[FAIL] {BACKEND_TO_STOP} is not running before the test"
        )
        return 1

    if not is_running(OTHER_BACKEND):
        print(
            f"[FAIL] {OTHER_BACKEND} is not running before the test"
        )
        return 1

    print("Starting backend failure test...")
    print()

    stopped = False

    try:
        if not stop_backend():
            return 1

        stopped = True

        # Confirm that the intended backend is actually stopped.
        if is_running(BACKEND_TO_STOP):
            print(f"[FAIL] {BACKEND_TO_STOP} is still running")
            return 1

        print(f"[PASS] Confirmed {BACKEND_TO_STOP} is stopped")
        print()

        if test_continued_availability():
            print()
            print("Failure test passed.")
            return 0

        print()
        print("Failure test failed.")
        return 1

    finally:
        # Restore the backend after the failure test.
        if stopped and not is_running(BACKEND_TO_STOP):
            print()
            print(f"[INFO] Restoring {BACKEND_TO_STOP}...")
            start_backend()


if __name__ == "__main__":
    sys.exit(main())
