"""
Phase 5 EIL Monitoring

Prometheus metrics and observability for Energy Intelligence Layer.
"""

from .prometheus_metrics import (
    PrometheusMetrics,
    get_metrics,
    MetricsSnapshot,
    PROMETHEUS_AVAILABLE
)

__all__ = [
    'PrometheusMetrics',
    'get_metrics',
    'MetricsSnapshot',
    'PROMETHEUS_AVAILABLE'
]

__version__ = "1.0.0"
