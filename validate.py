#!/usr/bin/env python3
import time
import subprocess
import sys


"""Validate that the required BARQ services are running."""

REQUIRED_SERVICES = [
    "nginx",
    "app-01",
    "app-02",
    "postgres",
    "redis",
]



def wait_for_http(url, timeout=30):
    start = time.time()

    while time.time() - start < timeout:
        result = subprocess.run(
            ["curl", "-sf", "--max-time", "2", url],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True

        time.sleep(1)

    return False



def check_services():
    failed = 0

    for service in REQUIRED_SERVICES:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", service],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip() == "true":
            print(f"[PASS] {service} is running")
        else:
            print(f"[FAIL] {service} is not running")
            failed += 1

    return failed


def main():
    failed = check_services()

    if wait_for_http("http://127.0.0.1:8080/health"):
        print("[PASS] NGINX /health is reachable")
    else:
        print("[FAIL] NGINX /health did not become ready within 30 seconds")
        failed += 1
        
    print()
    if failed == 0:
        print("Validation passed.")
        return 0

    print(f"Validation failed: {failed} check(s) failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
