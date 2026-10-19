#!/usr/bin/env sh
set -eu
BASE_URL="${BASE_URL:-http://localhost:8000}"
printf 'Checking %s/health ...\n' "$BASE_URL"
curl --fail --silent --show-error "$BASE_URL/health"
printf '\nChecking %s/metrics ...\n' "$BASE_URL"
curl --fail --silent --show-error "$BASE_URL/metrics" | grep -m 1 '^http_requests_total' || {
  echo "Expected request metric not found yet. Make a request to /api/work and retry."
  exit 1
}
printf '\nHealth and metrics endpoints are reachable.\n'
