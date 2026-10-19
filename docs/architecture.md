# Architecture

```text
Browser/curl -> FastAPI API :8000 -- /metrics --> Prometheus :9090
                                                     |       |
                                                     |       +--> Alertmanager :9093
                                                     +----------> Grafana :3000
```

- FastAPI exposes health, workload, incident-control, and Prometheus metrics endpoints.
- Prometheus scrapes the API every five seconds and evaluates alert rules.
- Alertmanager groups alerts. No email, Slack, or webhook receiver is configured.
- Grafana is provisioned with a Prometheus datasource and starter dashboard.
- This is a local learning lab, not a production deployment.
