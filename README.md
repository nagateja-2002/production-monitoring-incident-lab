# Production Monitoring & Incident Response Lab

A local observability lab for practising application metrics, Prometheus alert rules, Grafana dashboards, and incident-response workflows with Docker Compose.

## What this demonstrates
- FastAPI health and workload endpoints
- Prometheus counters, gauges, and latency histograms
- Grafana datasource and dashboard provisioning
- Alert rules for an unavailable target, elevated 5xx rate, and high p95 latency
- Reproducible local incident modes and recovery checks
- Automated application tests and a health-check script

> **Learning-lab warning:** This project is intended for local experimentation, not production use. The incident-control endpoint has no authentication, Grafana uses a lab password, and Alertmanager has no external notification receiver. Do not expose these services publicly.

## Prerequisites
- Docker Desktop or Docker Engine with Docker Compose plugin
- Python 3.10+ for the optional traffic-generation script
- `curl` for command-line checks

## Start
```bash
docker compose up --build -d
docker compose ps
```

| Service | Address |
|---|---|
| API health | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Prometheus targets | http://localhost:9090/targets |
| Prometheus alerts | http://localhost:9090/alerts |
| Alertmanager | http://localhost:9093 |
| Grafana | http://localhost:3000 |

Grafana lab login: `admin` / `lab-admin-change-me`. Change it before any non-local use. Dashboard: **Production Monitoring Incident Lab**, in the **Incident Lab** folder.

## Generate incidents
Run these from the repository root:
```bash
python scripts/simulate_incident.py --mode normal --requests 60
python scripts/simulate_incident.py --mode errors --requests 100 --interval 0.05
python scripts/simulate_incident.py --mode latency --requests 30 --interval 0.1
python scripts/simulate_incident.py --mode stress --requests 200 --interval 0
```
The simulator is bounded to 500 requests per run. Reset the application mode:
```bash
curl -X POST http://localhost:8000/admin/incident/normal
```
Simulate an unavailable target:
```bash
docker compose stop api
# Check Prometheus targets and alerts
docker compose start api
```
Alerts use rate windows and `for` durations, so they will not necessarily fire immediately. Generate enough traffic and allow evaluation time.

## Test the application
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r app/requirements.txt
python -m pytest app/tests -q
```

## Useful PromQL queries
```promql
sum(rate(http_requests_total[1m]))
sum(rate(http_requests_total{status_code=~"5.."}[1m]))
sum(rate(http_requests_total{status_code=~"5.."}[1m])) / clamp_min(sum(rate(http_requests_total[1m])), 0.001)
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{path="/api/work"}[2m])))
up{job="monitoring-lab-api"}
```

## Incident workflow
1. **Detect:** inspect Prometheus alerts and Grafana panels.
2. **Investigate:** check target state, status-code counts, request rate, and latency.
3. **Hypothesize:** compare metrics before and during the simulated incident.
4. **Recover:** reset the incident mode or restart the stopped API.
5. **Verify:** confirm the target is healthy and relevant metrics trend toward normal.

Detailed runbooks: [`docs/incident-runbooks.md`](docs/incident-runbooks.md). Architecture: [`docs/architecture.md`](docs/architecture.md).

## Stop and clean up
```bash
docker compose down
```
To also delete Grafana state stored in the local volume:
```bash
docker compose down -v
```

## Validation status
Automated tests and repeatable validation steps are included. Run them in your environment before treating the lab as verified; results depend on your local Docker/Python setup.

## License
A license will be added after the project has been validated.
