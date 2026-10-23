# Production Monitoring & Incident Response Lab

A local observability lab for practising application metrics, Prometheus alert rules, Grafana dashboards, and incident-response workflows with Docker Compose.

> **Learning-lab warning:** This project is intended for local experimentation, not production use. The incident-control endpoint has no authentication, Grafana uses a lab password, and Alertmanager has no external notification receiver. Do not expose these services publicly.

## What this demonstrates

- FastAPI health, workload, incident-control, and metrics endpoints
- Prometheus counters, gauges, and latency histograms
- Grafana datasource and dashboard provisioning
- Alert rules for an unavailable target, elevated HTTP 5xx rate, and high p95 latency
- Bounded, repeatable local incident simulations and recovery checks
- Automated application tests and a health-check script
- Runbooks and validation evidence that distinguish observed results from limitations

## Architecture

```text
Traffic simulator / curl
          |
          v
    FastAPI API (:8000) ---- /metrics ----> Prometheus (:9090)
          ^                                   |          |
          |                                   |          +--> Alertmanager (:9093)
          |                                   +------------> Grafana (:3000)
          |
          +---- incident-control endpoint for local simulations
```

Prometheus scrapes the API every five seconds and evaluates the configured rules. Alertmanager receives and groups alerts, but the current configuration does not deliver email, Slack, or webhook notifications. Grafana is provisioned with a Prometheus datasource and a starter dashboard.

## Prerequisites

- Docker Desktop or Docker Engine with the Docker Compose plugin
- Python 3.10+ for the optional traffic-generation script
- `curl` for command-line checks

## Start the lab

From the repository root:

```bash
docker compose up --build -d
docker compose ps
```

| Component | Local URL | Purpose |
|---|---|---|
| API health | http://localhost:8000/health | Application health |
| API docs | http://localhost:8000/docs | FastAPI API documentation |
| API metrics | http://localhost:8000/metrics | Metrics endpoint |
| Prometheus | http://localhost:9090 | Query and inspect metrics |
| Prometheus targets | http://localhost:9090/targets | Check scrape health |
| Prometheus alerts | http://localhost:9090/alerts | Check alert state |
| Alertmanager | http://localhost:9093 | Check received/grouped alerts |
| Grafana | http://localhost:3000 | Explore the dashboard |

Grafana lab login is `admin` / `lab-admin-change-me`. This is a documented demo credential, not a secure deployment setting. Keep the services local and change the credential before any use beyond local experimentation. Dashboard: **Production Monitoring Incident Lab**, in the **Incident Lab** folder.

## Generate simulated incidents

The traffic generator supports `normal`, `errors`, `latency`, and `stress` modes. A run is bounded to at most 500 requests.

```bash
python scripts/simulate_incident.py --mode normal --requests 60
python scripts/simulate_incident.py --mode errors --requests 100 --interval 0.05
python scripts/simulate_incident.py --mode latency --requests 30 --interval 0.1
python scripts/simulate_incident.py --mode stress --requests 200 --interval 0
```

After each simulation, inspect status counts, Prometheus metrics, alert state, and dashboard changes. Alert rules use rate windows and `for` durations, so they will not necessarily fire immediately.

Reset the application mode:

```bash
curl -X POST http://localhost:8000/admin/incident/normal
```

Simulate an unavailable API target:

```bash
docker compose stop api
# Inspect http://localhost:9090/targets and http://localhost:9090/alerts
docker compose start api
```

Wait for the service health check and Prometheus evaluation cycle, then confirm recovery from observed target and alert state. Do not assume the alert has cleared immediately after the container starts.

## Useful PromQL queries

Request rate:

```promql
sum(rate(http_requests_total[1m]))
```

Rate of HTTP 5xx responses:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[1m]))
```

Fraction of requests returning 5xx:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[1m]))
/
clamp_min(sum(rate(http_requests_total[1m])), 0.001)
```

Estimated p95 latency for the workload endpoint:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{path="/api/work"}[2m])
  )
)
```

Target health:

```promql
up{job="monitoring-lab-api"}
```

## Incident workflow

1. **Detect:** inspect Prometheus alerts and Grafana panels.
2. **Investigate:** check target health, status-code counts, request rate, latency, and container logs.
3. **Hypothesize:** compare metrics before and during the simulated incident.
4. **Recover:** reset the incident mode or restart the stopped API.
5. **Verify:** confirm health and alert state from observed output.
6. **Document:** record the symptom, evidence, likely cause, mitigation, and recovery check.

Detailed guides: [incident runbooks](docs/incident-runbooks.md), [architecture](docs/architecture.md), [validation status](docs/validation-status.md), and [incident validation evidence](docs/incident-validation-evidence.md).

## Testing

Create a virtual environment, install the application dependencies, and run the test suite:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r app/requirements.txt
python -m pytest app/tests -q
```

Automated tests and repeatable validation steps are included. See the validation-status document for the observations recorded during prior test sessions and their caveats. This README update does not rerun tests.

## Stop and clean up

Stop the containers:

```bash
docker compose down
```

To also remove the Grafana data volume for a clean local reset:

```bash
docker compose down -v
```

## Validation and limitations

Previously recorded evidence reports that the API health endpoint returned `UP`, Prometheus loaded all three alert rules, and high-error-rate, high-latency, and target-down scenarios were observed. The record also documents limitations in the post-restart target query output. Alert receipt in Alertmanager does not mean an external message was delivered.

Use the linked validation documents for detail. Rerun checks in your own environment before relying on the results.

## License

A license will be added after the project has been validated.
