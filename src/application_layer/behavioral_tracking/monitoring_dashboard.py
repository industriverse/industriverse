"""
Monitoring Dashboard for Behavioral Vector Metrics.

Real-time visualization and monitoring of behavioral tracking system health,
user engagement metrics, and BV computation statistics. Week 9 Day 7 deliverable.

Features:
- Real-time metrics collection
- System health monitoring
- User engagement analytics
- BV computation statistics
- Performance metrics
- Alerting for anomalies
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System-level metrics for monitoring."""
    timestamp: str
    events_logged_total: int
    events_logged_last_hour: int
    events_logged_last_minute: int
    bv_computations_total: int
    bv_computations_last_hour: int
    active_users_last_hour: int
    active_sessions_current: int
    avg_event_processing_time_ms: float
    avg_bv_computation_time_ms: float
    storage_operations_total: int
    cache_hit_rate: float
    error_rate: float
    system_health: str  # healthy, degraded, critical


@dataclass
class UserEngagementMetrics:
    """User engagement metrics."""
    timestamp: str
    total_users: int
    active_users_today: int
    active_users_this_week: int
    avg_session_duration_minutes: float
    avg_interactions_per_session: float
    most_active_capsule_types: Dict[str, int]
    most_common_interaction_types: Dict[str, int]
    user_archetype_distribution: Dict[str, int]


@dataclass
class BVComputationMetrics:
    """BV computation statistics."""
    timestamp: str
    total_bvs_computed: int
    bvs_computed_last_hour: int
    avg_computation_time_ms: float
    max_computation_time_ms: float
    min_computation_time_ms: float
    avg_events_per_bv: float
    computation_errors: int
    cache_hits: int
    cache_misses: int


class MetricsCollector:
    """Collects and aggregates metrics from the behavioral tracking system."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics_history: List[SystemMetrics] = []
        self.engagement_history: List[UserEngagementMetrics] = []
        self.bv_metrics_history: List[BVComputationMetrics] = []
        
        # Real-time counters
        self.events_logged = 0
        self.bv_computations = 0
        self.storage_operations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        
        # Timing metrics
        self.event_processing_times: List[float] = []
        self.bv_computation_times: List[float] = []
        
        # Active tracking
        self.active_users: set = set()
        self.active_sessions: set = set()
        
        logger.info("MetricsCollector initialized")
    
    def record_event_logged(self, user_id: str, session_id: str, processing_time_ms: float):
        """Record an event being logged."""
        self.events_logged += 1
        self.event_processing_times.append(processing_time_ms)
        self.active_users.add(user_id)
        self.active_sessions.add(session_id)
    
    def record_bv_computation(self, computation_time_ms: float, num_events: int):
        """Record a BV computation."""
        self.bv_computations += 1
        self.bv_computation_times.append(computation_time_ms)
    
    def record_storage_operation(self):
        """Record a storage operation."""
        self.storage_operations += 1
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def record_error(self):
        """Record an error."""
        self.errors += 1
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        one_minute_ago = now - timedelta(minutes=1)
        
        # Calculate rates
        events_last_hour = sum(
            1 for t in self.event_processing_times
            if datetime.fromisoformat(str(t)) > one_hour_ago
        ) if self.event_processing_times else 0
        
        events_last_minute = sum(
            1 for t in self.event_processing_times
            if datetime.fromisoformat(str(t)) > one_minute_ago
        ) if self.event_processing_times else 0
        
        # Calculate averages
        avg_event_time = (
            sum(self.event_processing_times) / len(self.event_processing_times)
            if self.event_processing_times else 0
        )
        
        avg_bv_time = (
            sum(self.bv_computation_times) / len(self.bv_computation_times)
            if self.bv_computation_times else 0
        )
        
        # Calculate cache hit rate
        total_cache_ops = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            self.cache_hits / total_cache_ops if total_cache_ops > 0 else 0
        )
        
        # Calculate error rate
        total_ops = self.events_logged + self.bv_computations
        error_rate = self.errors / total_ops if total_ops > 0 else 0
        
        # Determine system health
        if error_rate > 0.1:
            health = "critical"
        elif error_rate > 0.05 or cache_hit_rate < 0.5:
            health = "degraded"
        else:
            health = "healthy"
        
        metrics = SystemMetrics(
            timestamp=now.isoformat(),
            events_logged_total=self.events_logged,
            events_logged_last_hour=events_last_hour,
            events_logged_last_minute=events_last_minute,
            bv_computations_total=self.bv_computations,
            bv_computations_last_hour=0,  # TODO: implement time-based tracking
            active_users_last_hour=len(self.active_users),
            active_sessions_current=len(self.active_sessions),
            avg_event_processing_time_ms=avg_event_time,
            avg_bv_computation_time_ms=avg_bv_time,
            storage_operations_total=self.storage_operations,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            system_health=health
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    async def collect_engagement_metrics(self, bv_storage) -> UserEngagementMetrics:
        """Collect user engagement metrics."""
        now = datetime.utcnow()
        
        # Query storage for engagement data
        # TODO: Implement actual queries to bv_storage
        
        metrics = UserEngagementMetrics(
            timestamp=now.isoformat(),
            total_users=len(self.active_users),
            active_users_today=len(self.active_users),
            active_users_this_week=len(self.active_users),
            avg_session_duration_minutes=15.5,  # Placeholder
            avg_interactions_per_session=8.2,  # Placeholder
            most_active_capsule_types={"task": 45, "alert": 32, "workflow": 23},
            most_common_interaction_types={"tap": 120, "expand": 45, "action": 38},
            user_archetype_distribution={
                "novice": 15,
                "intermediate": 35,
                "proficient": 28,
                "advanced": 18,
                "power_user": 4
            }
        )
        
        self.engagement_history.append(metrics)
        return metrics
    
    async def collect_bv_computation_metrics(self) -> BVComputationMetrics:
        """Collect BV computation metrics."""
        now = datetime.utcnow()
        
        metrics = BVComputationMetrics(
            timestamp=now.isoformat(),
            total_bvs_computed=self.bv_computations,
            bvs_computed_last_hour=0,  # TODO: implement time-based tracking
            avg_computation_time_ms=(
                sum(self.bv_computation_times) / len(self.bv_computation_times)
                if self.bv_computation_times else 0
            ),
            max_computation_time_ms=(
                max(self.bv_computation_times) if self.bv_computation_times else 0
            ),
            min_computation_time_ms=(
                min(self.bv_computation_times) if self.bv_computation_times else 0
            ),
            avg_events_per_bv=0,  # TODO: track this
            computation_errors=self.errors,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses
        )
        
        self.bv_metrics_history.append(metrics)
        return metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        return {
            "system": asdict(self.metrics_history[-1]) if self.metrics_history else None,
            "engagement": asdict(self.engagement_history[-1]) if self.engagement_history else None,
            "bv_computation": asdict(self.bv_metrics_history[-1]) if self.bv_metrics_history else None,
            "history_length": {
                "system": len(self.metrics_history),
                "engagement": len(self.engagement_history),
                "bv_computation": len(self.bv_metrics_history)
            }
        }


class MonitoringDashboard:
    """
    Monitoring dashboard for behavioral tracking system.
    
    Provides real-time metrics, alerts, and visualizations.
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize monitoring dashboard."""
        self.metrics_collector = metrics_collector
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "error_rate": 0.05,
            "cache_hit_rate_min": 0.5,
            "avg_processing_time_max_ms": 100,
            "active_sessions_min": 1
        }
        logger.info("MonitoringDashboard initialized")
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring loop."""
        logger.info(f"Starting monitoring loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.collect_and_check_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def collect_and_check_metrics(self):
        """Collect metrics and check for alerts."""
        # Collect all metrics
        system_metrics = await self.metrics_collector.collect_system_metrics()
        
        # Check for alerts
        await self.check_alerts(system_metrics)
        
        # Log current status
        logger.info(
            f"System Health: {system_metrics.system_health} | "
            f"Events: {system_metrics.events_logged_last_minute}/min | "
            f"Active Users: {system_metrics.active_users_last_hour} | "
            f"Cache Hit Rate: {system_metrics.cache_hit_rate:.2%} | "
            f"Error Rate: {system_metrics.error_rate:.2%}"
        )
    
    async def check_alerts(self, metrics: SystemMetrics):
        """Check metrics against thresholds and generate alerts."""
        now = datetime.utcnow()
        
        # Check error rate
        if metrics.error_rate > self.alert_thresholds["error_rate"]:
            alert = {
                "timestamp": now.isoformat(),
                "severity": "critical",
                "metric": "error_rate",
                "value": metrics.error_rate,
                "threshold": self.alert_thresholds["error_rate"],
                "message": f"Error rate {metrics.error_rate:.2%} exceeds threshold"
            }
            self.alerts.append(alert)
            logger.warning(f"ALERT: {alert['message']}")
        
        # Check cache hit rate
        if metrics.cache_hit_rate < self.alert_thresholds["cache_hit_rate_min"]:
            alert = {
                "timestamp": now.isoformat(),
                "severity": "warning",
                "metric": "cache_hit_rate",
                "value": metrics.cache_hit_rate,
                "threshold": self.alert_thresholds["cache_hit_rate_min"],
                "message": f"Cache hit rate {metrics.cache_hit_rate:.2%} below threshold"
            }
            self.alerts.append(alert)
            logger.warning(f"ALERT: {alert['message']}")
        
        # Check processing time
        if metrics.avg_event_processing_time_ms > self.alert_thresholds["avg_processing_time_max_ms"]:
            alert = {
                "timestamp": now.isoformat(),
                "severity": "warning",
                "metric": "avg_processing_time",
                "value": metrics.avg_event_processing_time_ms,
                "threshold": self.alert_thresholds["avg_processing_time_max_ms"],
                "message": f"Avg processing time {metrics.avg_event_processing_time_ms:.1f}ms exceeds threshold"
            }
            self.alerts.append(alert)
            logger.warning(f"ALERT: {alert['message']}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data for visualization."""
        return {
            "metrics": self.metrics_collector.get_metrics_summary(),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "thresholds": self.alert_thresholds,
            "status": {
                "monitoring_active": True,
                "last_update": datetime.utcnow().isoformat()
            }
        }
    
    def get_metrics_for_timerange(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics for a specific time range."""
        system_metrics = [
            asdict(m) for m in self.metrics_collector.metrics_history
            if start_time <= datetime.fromisoformat(m.timestamp) <= end_time
        ]
        
        engagement_metrics = [
            asdict(m) for m in self.metrics_collector.engagement_history
            if start_time <= datetime.fromisoformat(m.timestamp) <= end_time
        ]
        
        bv_metrics = [
            asdict(m) for m in self.metrics_collector.bv_metrics_history
            if start_time <= datetime.fromisoformat(m.timestamp) <= end_time
        ]
        
        return {
            "system": system_metrics,
            "engagement": engagement_metrics,
            "bv_computation": bv_metrics
        }
    
    def export_metrics_json(self, filepath: str):
        """Export all metrics to JSON file."""
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "metrics": self.get_dashboard_data(),
            "history": {
                "system": [asdict(m) for m in self.metrics_collector.metrics_history],
                "engagement": [asdict(m) for m in self.metrics_collector.engagement_history],
                "bv_computation": [asdict(m) for m in self.metrics_collector.bv_metrics_history]
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")


# FastAPI integration for dashboard API
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

dashboard_app = FastAPI(title="Behavioral Tracking Monitoring Dashboard")

# Global metrics collector and dashboard
metrics_collector = MetricsCollector()
monitoring_dashboard = MonitoringDashboard(metrics_collector)


@dashboard_app.get("/dashboard")
async def get_dashboard():
    """Get complete dashboard data."""
    return monitoring_dashboard.get_dashboard_data()


@dashboard_app.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics."""
    metrics = await metrics_collector.collect_system_metrics()
    return asdict(metrics)


@dashboard_app.get("/metrics/engagement")
async def get_engagement_metrics():
    """Get current engagement metrics."""
    metrics = await metrics_collector.collect_engagement_metrics(None)
    return asdict(metrics)


@dashboard_app.get("/metrics/bv-computation")
async def get_bv_computation_metrics():
    """Get BV computation metrics."""
    metrics = await metrics_collector.collect_bv_computation_metrics()
    return asdict(metrics)


@dashboard_app.get("/alerts")
async def get_alerts():
    """Get recent alerts."""
    return {"alerts": monitoring_dashboard.alerts[-20:]}


@dashboard_app.get("/health")
async def health_check():
    """Health check endpoint."""
    system_metrics = await metrics_collector.collect_system_metrics()
    return {
        "status": system_metrics.system_health,
        "timestamp": system_metrics.timestamp
    }


# CLI interface for monitoring
if __name__ == "__main__":
    import uvicorn
    
    # Start monitoring loop in background
    async def start_monitoring():
        await monitoring_dashboard.start_monitoring(interval_seconds=60)
    
    # Run FastAPI server with monitoring
    logger.info("Starting Monitoring Dashboard API server on port 8001")
    uvicorn.run(dashboard_app, host="0.0.0.0", port=8001)
