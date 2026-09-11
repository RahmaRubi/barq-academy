#!/usr/bin/env python3
import time
import subprocess
import sys
import json


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


def check_endpoint(path, expected_status=200):
    url = f"http://127.0.0.1:8080{path}"

    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
         "--max-time", "2", url],
        capture_output=True,
        text=True,
    )

    status = result.stdout.strip()

    if status == str(expected_status):
        print(f"[PASS] GET {path} returns {status}")
        return 0

    print(f"[FAIL] GET {path} returned {status}, expected {expected_status}")
    return 1



def check_instance():
    url = "http://127.0.0.1:8080/instance"

    result = subprocess.run(
        ["curl", "-s", "--max-time", "2", url],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("[FAIL] GET /instance request failed")
        return 1

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[FAIL] GET /instance returned invalid JSON")
        return 1

    instance_id = data.get("instance_id")

    if instance_id in {"app-01", "app-02"}:
        print(f"[PASS] GET /instance identifies {instance_id}")
        return 0

    print(f"[FAIL] GET /instance returned invalid instance_id: {instance_id}")
    return 1



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
    
    
    failed += check_endpoint("/")
    failed += check_endpoint("/health")
    failed += check_endpoint("/ready")
    failed += check_instance()

        
    print()
    if failed == 0:
        print("Validation passed.")
        return 0

    print(f"Validation failed: {failed} check(s) failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
