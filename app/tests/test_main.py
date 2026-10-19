from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_returns_service_metadata():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "monitoring-lab-api"


def test_health_is_up():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_incident_mode_can_be_changed_and_reset():
    response = client.post("/admin/incident/latency")
    assert response.status_code == 200
    assert response.json()["mode"] == "latency"
    response = client.post("/admin/incident/normal")
    assert response.status_code == 200
    assert response.json()["mode"] == "normal"


def test_metrics_endpoint_exposes_prometheus_metrics():
    client.get("/api/work")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
