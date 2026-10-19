import random
import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

APP_NAME = "monitoring-lab-api"
APP_VERSION = "1.0.0"
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status_code"])
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
APP_UP = Gauge("application_up", "Whether the application process is serving requests")
INCIDENT_MODE = Gauge("incident_mode", "0=normal, 1=errors, 2=latency, 3=stress")
MODE: Literal["normal", "errors", "latency", "stress"] = "normal"


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        REQUESTS.labels(request.method, request.url.path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(time.perf_counter() - start)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    APP_UP.set(1)
    INCIDENT_MODE.set(0)
    yield
    APP_UP.set(0)


app = FastAPI(
    title="Production Monitoring Incident Lab",
    description="A small API for practising metrics, alerting, and incident response.",
    version=APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(MetricsMiddleware)


@app.get("/")
def root():
    return {"service": APP_NAME, "version": APP_VERSION, "mode": MODE}


@app.get("/health")
def health():
    return {"status": "UP", "service": APP_NAME}


@app.get("/api/work")
def work():
    if MODE == "latency":
        time.sleep(1.2)
    if MODE == "errors" and random.random() < 0.8:
        return Response(
            content='{"detail":"simulated application error"}',
            status_code=500,
            media_type="application/json",
        )
    if MODE == "stress":
        sum(i * i for i in range(15000))
    return {"status": "OK", "mode": MODE}


@app.post("/admin/incident/{mode}")
def set_incident(mode: Literal["normal", "errors", "latency", "stress"]):
    global MODE
    MODE = mode
    INCIDENT_MODE.set({"normal": 0, "errors": 1, "latency": 2, "stress": 3}[mode])
    return {"mode": MODE, "incident_mode": INCIDENT_MODE._value.get()}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
