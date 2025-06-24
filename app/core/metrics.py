from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

OLLAMA_REQUEST_LATENCY = Histogram(
    'ollama_request_duration_seconds',
    'Ollama API request latency in seconds',
    ['operation']
)

CIRCUIT_BREAKER_STATE = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open)',
)

def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def track_ollama_request(operation: str, duration: float):
    OLLAMA_REQUEST_LATENCY.labels(operation=operation).observe(duration)

def update_circuit_breaker_state(is_open: bool):
    CIRCUIT_BREAKER_STATE.set(1 if is_open else 0) 