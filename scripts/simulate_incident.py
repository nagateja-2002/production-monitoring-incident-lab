#!/usr/bin/env python3
"""Generate bounded request traffic against the local monitoring lab."""
import argparse
import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8000"


def request(path, method="GET"):
    req = urllib.request.Request(BASE_URL + path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return None, str(exc)


def main():
    parser = argparse.ArgumentParser(description="Generate traffic for the local incident lab.")
    parser.add_argument("--mode", choices=["normal", "errors", "latency", "stress"], default="normal")
    parser.add_argument("--requests", type=int, default=60, help="Number of requests (max 500).")
    parser.add_argument("--interval", type=float, default=0.1, help="Seconds between requests.")
    args = parser.parse_args()
    if not 1 <= args.requests <= 500:
        parser.error("--requests must be between 1 and 500")
    if args.interval < 0:
        parser.error("--interval must be >= 0")

    status, body = request(f"/admin/incident/{args.mode}", method="POST")
    if status != 200:
        raise SystemExit(f"Could not set incident mode (status={status}): {body}")
    print(f"Mode set to {args.mode}; generating {args.requests} requests...")
    counts = {}
    for _ in range(args.requests):
        status, _ = request("/api/work")
        key = str(status) if status is not None else "connection-error"
        counts[key] = counts.get(key, 0) + 1
        if args.interval:
            time.sleep(args.interval)
    print("Request results:", json.dumps(counts, sort_keys=True))
    print("Reset with: curl -X POST http://localhost:8000/admin/incident/normal")


if __name__ == "__main__":
    main()
