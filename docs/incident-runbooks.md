# Incident Runbooks

## Start
```bash
docker compose up --build -d
docker compose ps
```
Open API health at http://localhost:8000/health, Prometheus targets at http://localhost:9090/targets, alerts at http://localhost:9090/alerts, Alertmanager at http://localhost:9093, and Grafana at http://localhost:3000.

## Elevated 5xx errors
1. Run `python scripts/simulate_incident.py --mode errors --requests 100 --interval 0.05`.
2. Check the printed status counts.
3. Query `sum(rate(http_requests_total{status_code=~"5.."}[1m]))` in Prometheus.
4. Check `MonitoringLabHighErrorRate`. Allow time for the rate window and `for` duration.
5. Recover with `curl -X POST http://localhost:8000/admin/incident/normal`.
6. Generate normal requests and observe the error ratio decline.

## High latency
1. Run `python scripts/simulate_incident.py --mode latency --requests 30 --interval 0.1`.
2. Query p95 latency:
   `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{path="/api/work"}[2m])))`
3. Check `MonitoringLabHighLatency` after enough observations and evaluation time.
4. Recover with `curl -X POST http://localhost:8000/admin/incident/normal`.

## Request traffic increase
1. Run `python scripts/simulate_incident.py --mode stress --requests 200 --interval 0`.
2. Compare request rate and latency in Grafana.
3. Reset with `curl -X POST http://localhost:8000/admin/incident/normal`.

## Unavailable target
1. Stop the API: `docker compose stop api`.
2. Check Prometheus targets and wait for `MonitoringLabTargetDown`.
3. Recover: `docker compose start api`.
4. Wait for the target to return to `UP`.

## Troubleshooting checklist
- `docker compose ps`
- `docker compose logs --tail=100 api prometheus alertmanager grafana`
- Check http://localhost:9090/targets and http://localhost:9090/alerts
- `curl -s http://localhost:8000/metrics`
- After recovery, verify target health, request results, error ratio, and latency rather than assuming the incident is resolved.
