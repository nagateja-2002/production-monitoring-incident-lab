# Incident Response Runbook

Use the runbook in the local lab and record observed output. Do not assume a test passed without evidence.

## 1. API unavailable / target down

**Signals**
- API health endpoint fails.
- Prometheus scrape target reports down.
- `MonitoringLabTargetDown` fires after its configured delay.

**Investigate**
```powershell
docker compose ps
docker compose logs --tail 100 api prometheus
Invoke-RestMethod -Uri "http://localhost:8000/health"
(Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts").data.alerts
```

**Response**
1. Check whether the API container is running.
2. Inspect API logs for startup/runtime errors.
3. Check Prometheus target and alert state.
4. Restore the service after collecting evidence.
5. Verify the health endpoint returns `UP` and the target-down alert clears.

**Test status:** confirmed. Stopping the API caused `MonitoringLabTargetDown` to fire with critical severity. Starting the API restored the health endpoint and the alert disappeared from the active-alert output.

## 2. High 5xx error rate

**Signals**
- 5xx samples appear in request metrics.
- `MonitoringLabHighErrorRate` fires when the observed ratio exceeds 20% for 30 seconds.

**Investigate**
- Inspect `http://localhost:9090/alerts`.
- Inspect `http://localhost:9093`.
- Review API logs and incident mode.
- Check the request counter grouped by status code.

**Response**
1. Identify the request path or simulated mode generating errors.
2. Return the simulated incident mode to `normal` after collecting evidence.
3. Allow the metric window and alert duration to update.
4. Verify the alert clears in Prometheus and Alertmanager.

**Test status:** confirmed previously. The alert fired, was received by Alertmanager, and later cleared.

## 3. High latency

**Signals**
- Estimated p95 latency for `/api/work` exceeds 0.8 seconds for 30 seconds.
- `MonitoringLabHighLatency` enters firing state.

**Investigate**
- Inspect request-duration histogram metrics at `/metrics`.
- Inspect the alert state in Prometheus.
- Review API logs and the active incident mode.

**Response**
1. Enable the simulated latency mode to reproduce the incident.
2. Generate requests and allow Prometheus to evaluate the rule.
3. Record the alert state and severity.
4. Return the mode to `normal` after collecting evidence.
5. Verify the latency alert clears.

**Test status:** confirmed. With latency mode enabled and requests generated, `MonitoringLabHighLatency` was observed in `firing` state with warning severity.

## Incident record template

- Incident / alert:
- Start and end time:
- Symptom and impact:
- Evidence (metrics, logs, target state):
- Root cause:
- Mitigation:
- Recovery verification:
- Follow-up / prevention:
