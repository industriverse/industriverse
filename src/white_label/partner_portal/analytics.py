"""
Analytics and Metrics Tracking

Tracks usage metrics, performance data, and revenue for partner deployments.
Enables data-driven decision making and billing calculations.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict


class MetricType(Enum):
    """Types of metrics tracked"""
    API_CALL = "api_call"
    WIDGET_IMPRESSION = "widget_impression"
    WIDGET_INTERACTION = "widget_interaction"
    DEPLOYMENT_EVENT = "deployment_event"
    ERROR_EVENT = "error_event"
    SECURITY_EVENT = "security_event"
    DATA_VOLUME = "data_volume"


class TimeGranularity(Enum):
    """Time granularity for aggregation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricEvent:
    """Individual metric event"""
    event_id: str
    partner_id: str
    metric_type: str
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'partner_id': self.partner_id,
            'metric_type': self.metric_type,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'metadata': self.metadata,
        }


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a time period"""
    partner_id: str
    start_time: datetime
    end_time: datetime
    granularity: str

    # Usage metrics
    total_api_calls: int = 0
    total_widget_impressions: int = 0
    total_widget_interactions: int = 0
    unique_users: int = 0

    # Performance metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0

    # Security metrics
    total_threats_detected: int = 0
    critical_threats: int = 0
    blocked_requests: int = 0

    # Data volume
    data_in_gb: float = 0.0
    data_out_gb: float = 0.0

    # Widget-specific
    widget_usage: Dict[str, int] = field(default_factory=dict)

    # Revenue
    estimated_revenue: float = 0.0
    partner_share: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'partner_id': self.partner_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'granularity': self.granularity,
            'metrics': {
                'api_calls': self.total_api_calls,
                'widget_impressions': self.total_widget_impressions,
                'widget_interactions': self.total_widget_interactions,
                'unique_users': self.unique_users,
                'avg_response_time_ms': self.avg_response_time_ms,
                'p95_response_time_ms': self.p95_response_time_ms,
                'error_rate_percent': self.error_rate_percent,
                'threats_detected': self.total_threats_detected,
                'critical_threats': self.critical_threats,
                'blocked_requests': self.blocked_requests,
                'data_in_gb': self.data_in_gb,
                'data_out_gb': self.data_out_gb,
            },
            'widget_usage': self.widget_usage,
            'revenue': {
                'estimated_revenue': self.estimated_revenue,
                'partner_share': self.partner_share,
            }
        }


@dataclass
class RevenueReport:
    """Revenue report for billing period"""
    partner_id: str
    billing_period_start: datetime
    billing_period_end: datetime

    # Base subscription
    base_subscription_fee: float
    tier: str

    # Usage-based charges
    usage_charges: Dict[str, float] = field(default_factory=dict)
    total_usage_charges: float = 0.0

    # Revenue share from partner's customers
    partner_customer_revenue: float = 0.0
    industriverse_share: float = 0.0
    partner_share: float = 0.0

    # Totals
    total_charges: float = 0.0
    net_amount: float = 0.0

    # Metrics
    total_api_calls: int = 0
    total_deployments: int = 0
    total_users: int = 0

    def calculate_totals(self, revenue_share_percent: float):
        """Calculate revenue totals"""
        self.total_usage_charges = sum(self.usage_charges.values())
        self.total_charges = self.base_subscription_fee + self.total_usage_charges

        # Calculate revenue share
        self.partner_share = self.partner_customer_revenue * (revenue_share_percent / 100)
        self.industriverse_share = self.partner_customer_revenue - self.partner_share

        # Net = what partner owes (charges) minus what we owe them (their share)
        self.net_amount = self.total_charges - self.partner_share

    def to_dict(self) -> Dict[str, Any]:
        return {
            'partner_id': self.partner_id,
            'billing_period': {
                'start': self.billing_period_start.isoformat(),
                'end': self.billing_period_end.isoformat(),
            },
            'subscription': {
                'base_fee': self.base_subscription_fee,
                'tier': self.tier,
            },
            'usage': {
                'charges': self.usage_charges,
                'total': self.total_usage_charges,
            },
            'revenue_share': {
                'partner_customer_revenue': self.partner_customer_revenue,
                'industriverse_share': self.industriverse_share,
                'partner_share': self.partner_share,
            },
            'totals': {
                'total_charges': self.total_charges,
                'net_amount': self.net_amount,
            },
            'metrics': {
                'api_calls': self.total_api_calls,
                'deployments': self.total_deployments,
                'users': self.total_users,
            }
        }


class AnalyticsTracker:
    """
    Analytics and metrics tracking system

    Responsibilities:
    - Track real-time events
    - Aggregate metrics
    - Generate reports
    - Calculate revenue
    - Performance monitoring
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("./analytics_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory buffers for real-time events
        self.event_buffer: List[MetricEvent] = []
        self.buffer_size = 1000  # Flush to disk after 1000 events

    def track_event(
        self,
        partner_id: str,
        metric_type: MetricType,
        value: float = 1.0,
        metadata: Dict[str, Any] = None
    ):
        """Track a metric event"""
        import uuid

        event = MetricEvent(
            event_id=str(uuid.uuid4()),
            partner_id=partner_id,
            metric_type=metric_type.value,
            timestamp=datetime.now(),
            value=value,
            metadata=metadata or {}
        )

        self.event_buffer.append(event)

        # Flush if buffer is full
        if len(self.event_buffer) >= self.buffer_size:
            self._flush_events()

    def track_api_call(
        self,
        partner_id: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int
    ):
        """Track API call with response metrics"""
        self.track_event(
            partner_id=partner_id,
            metric_type=MetricType.API_CALL,
            value=1.0,
            metadata={
                'endpoint': endpoint,
                'response_time_ms': response_time_ms,
                'status_code': status_code,
                'error': status_code >= 400
            }
        )

    def track_widget_impression(
        self,
        partner_id: str,
        widget_type: str,
        dac_id: str
    ):
        """Track widget impression"""
        self.track_event(
            partner_id=partner_id,
            metric_type=MetricType.WIDGET_IMPRESSION,
            value=1.0,
            metadata={
                'widget_type': widget_type,
                'dac_id': dac_id
            }
        )

    def track_widget_interaction(
        self,
        partner_id: str,
        widget_type: str,
        interaction_type: str
    ):
        """Track widget interaction (click, hover, etc.)"""
        self.track_event(
            partner_id=partner_id,
            metric_type=MetricType.WIDGET_INTERACTION,
            value=1.0,
            metadata={
                'widget_type': widget_type,
                'interaction_type': interaction_type
            }
        )

    def track_deployment(
        self,
        partner_id: str,
        dac_id: str,
        environment: str
    ):
        """Track deployment event"""
        self.track_event(
            partner_id=partner_id,
            metric_type=MetricType.DEPLOYMENT_EVENT,
            value=1.0,
            metadata={
                'dac_id': dac_id,
                'environment': environment,
                'event': 'deployed'
            }
        )

    def track_security_event(
        self,
        partner_id: str,
        event_type: str,
        severity: str
    ):
        """Track security event"""
        self.track_event(
            partner_id=partner_id,
            metric_type=MetricType.SECURITY_EVENT,
            value=1.0,
            metadata={
                'event_type': event_type,
                'severity': severity
            }
        )

    def get_metrics(
        self,
        partner_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[AggregatedMetrics]:
        """Get aggregated metrics for time period"""
        # Load events from storage
        events = self._load_events(partner_id, start_time, end_time)

        # Aggregate by time buckets
        time_buckets = self._create_time_buckets(start_time, end_time, granularity)
        aggregated = []

        for bucket_start, bucket_end in time_buckets:
            bucket_events = [
                e for e in events
                if bucket_start <= e.timestamp < bucket_end
            ]

            metrics = self._aggregate_events(partner_id, bucket_events, bucket_start, bucket_end, granularity)
            aggregated.append(metrics)

        return aggregated

    def generate_revenue_report(
        self,
        partner_id: str,
        billing_period_start: datetime,
        billing_period_end: datetime,
        base_subscription_fee: float,
        tier: str,
        revenue_share_percent: float
    ) -> RevenueReport:
        """Generate revenue report for billing period"""
        # Get metrics for period
        metrics = self.get_metrics(
            partner_id,
            billing_period_start,
            billing_period_end,
            TimeGranularity.MONTH
        )

        # Aggregate totals
        total_api_calls = sum(m.total_api_calls for m in metrics)
        total_deployments = len(self._load_deployment_events(partner_id, billing_period_start, billing_period_end))

        # Calculate usage charges (example pricing)
        usage_charges = {}

        # API calls: $0.001 per call after 100k included
        if total_api_calls > 100000:
            usage_charges['api_calls'] = (total_api_calls - 100000) * 0.001

        # Deployments: $500 per deployment after 5 included
        if total_deployments > 5:
            usage_charges['deployments'] = (total_deployments - 5) * 500

        # Create report
        report = RevenueReport(
            partner_id=partner_id,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            base_subscription_fee=base_subscription_fee,
            tier=tier,
            usage_charges=usage_charges,
            total_api_calls=total_api_calls,
            total_deployments=total_deployments,
        )

        # Calculate revenue (in real implementation, this would come from partner's billing system)
        report.partner_customer_revenue = self._estimate_partner_revenue(partner_id, billing_period_start, billing_period_end)

        report.calculate_totals(revenue_share_percent)

        # Save report
        self._save_report(report)

        return report

    def get_dashboard_summary(self, partner_id: str) -> Dict[str, Any]:
        """Get dashboard summary for partner"""
        # Last 30 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)

        metrics = self.get_metrics(partner_id, start_time, end_time, TimeGranularity.DAY)

        # Calculate summaries
        total_api_calls = sum(m.total_api_calls for m in metrics)
        total_impressions = sum(m.total_widget_impressions for m in metrics)
        total_interactions = sum(m.total_widget_interactions for m in metrics)
        avg_error_rate = sum(m.error_rate_percent for m in metrics) / len(metrics) if metrics else 0

        # Widget usage breakdown
        widget_usage = defaultdict(int)
        for m in metrics:
            for widget, count in m.widget_usage.items():
                widget_usage[widget] += count

        # Trends (compare to previous 30 days)
        previous_start = start_time - timedelta(days=30)
        previous_metrics = self.get_metrics(partner_id, previous_start, start_time, TimeGranularity.DAY)
        previous_api_calls = sum(m.total_api_calls for m in previous_metrics)

        api_call_trend = ((total_api_calls - previous_api_calls) / previous_api_calls * 100) if previous_api_calls > 0 else 0

        return {
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'days': 30
            },
            'totals': {
                'api_calls': total_api_calls,
                'widget_impressions': total_impressions,
                'widget_interactions': total_interactions,
                'error_rate': round(avg_error_rate, 2),
            },
            'trends': {
                'api_calls_change_percent': round(api_call_trend, 1)
            },
            'widget_usage': dict(widget_usage),
            'top_widgets': sorted(widget_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def _flush_events(self):
        """Flush event buffer to storage"""
        if not self.event_buffer:
            return

        # Group by partner and date
        by_partner_date = defaultdict(list)
        for event in self.event_buffer:
            date_key = event.timestamp.strftime('%Y-%m-%d')
            by_partner_date[(event.partner_id, date_key)].append(event)

        # Save to files
        for (partner_id, date_key), events in by_partner_date.items():
            self._append_events_to_file(partner_id, date_key, events)

        # Clear buffer
        self.event_buffer.clear()

    def _append_events_to_file(self, partner_id: str, date_key: str, events: List[MetricEvent]):
        """Append events to daily log file"""
        log_dir = self.storage_path / partner_id / 'events'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{date_key}.jsonl"

        with open(log_file, 'a') as f:
            for event in events:
                f.write(json.dumps(event.to_dict()) + '\n')

    def _load_events(self, partner_id: str, start_time: datetime, end_time: datetime) -> List[MetricEvent]:
        """Load events from storage for time period"""
        events = []

        # Include buffered events
        for event in self.event_buffer:
            if event.partner_id == partner_id and start_time <= event.timestamp < end_time:
                events.append(event)

        # Load from files
        log_dir = self.storage_path / partner_id / 'events'
        if not log_dir.exists():
            return events

        current_date = start_time.date()
        end_date = end_time.date()

        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            log_file = log_dir / f"{date_key}.jsonl"

            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        data = json.loads(line)
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        if start_time <= timestamp < end_time:
                            events.append(MetricEvent(
                                event_id=data['event_id'],
                                partner_id=data['partner_id'],
                                metric_type=data['metric_type'],
                                timestamp=timestamp,
                                value=data['value'],
                                metadata=data.get('metadata', {})
                            ))

            current_date += timedelta(days=1)

        return events

    def _load_deployment_events(self, partner_id: str, start_time: datetime, end_time: datetime) -> List[MetricEvent]:
        """Load deployment events"""
        all_events = self._load_events(partner_id, start_time, end_time)
        return [e for e in all_events if e.metric_type == MetricType.DEPLOYMENT_EVENT.value]

    def _create_time_buckets(self, start_time: datetime, end_time: datetime, granularity: TimeGranularity):
        """Create time buckets for aggregation"""
        buckets = []

        if granularity == TimeGranularity.HOUR:
            delta = timedelta(hours=1)
        elif granularity == TimeGranularity.DAY:
            delta = timedelta(days=1)
        elif granularity == TimeGranularity.WEEK:
            delta = timedelta(weeks=1)
        else:  # MONTH
            delta = timedelta(days=30)

        current = start_time
        while current < end_time:
            bucket_end = min(current + delta, end_time)
            buckets.append((current, bucket_end))
            current = bucket_end

        return buckets

    def _aggregate_events(
        self,
        partner_id: str,
        events: List[MetricEvent],
        start_time: datetime,
        end_time: datetime,
        granularity: TimeGranularity
    ) -> AggregatedMetrics:
        """Aggregate events into metrics"""
        metrics = AggregatedMetrics(
            partner_id=partner_id,
            start_time=start_time,
            end_time=end_time,
            granularity=granularity.value
        )

        # Count by type
        widget_usage = defaultdict(int)
        response_times = []
        errors = 0

        for event in events:
            if event.metric_type == MetricType.API_CALL.value:
                metrics.total_api_calls += 1
                if 'response_time_ms' in event.metadata:
                    response_times.append(event.metadata['response_time_ms'])
                if event.metadata.get('error'):
                    errors += 1

            elif event.metric_type == MetricType.WIDGET_IMPRESSION.value:
                metrics.total_widget_impressions += 1
                widget_type = event.metadata.get('widget_type', 'unknown')
                widget_usage[widget_type] += 1

            elif event.metric_type == MetricType.WIDGET_INTERACTION.value:
                metrics.total_widget_interactions += 1

            elif event.metric_type == MetricType.SECURITY_EVENT.value:
                metrics.total_threats_detected += 1
                if event.metadata.get('severity') == 'critical':
                    metrics.critical_threats += 1

        # Calculate derived metrics
        if response_times:
            metrics.avg_response_time_ms = sum(response_times) / len(response_times)
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            metrics.p95_response_time_ms = sorted_times[p95_index] if p95_index < len(sorted_times) else 0

        if metrics.total_api_calls > 0:
            metrics.error_rate_percent = (errors / metrics.total_api_calls) * 100

        metrics.widget_usage = dict(widget_usage)

        return metrics

    def _estimate_partner_revenue(self, partner_id: str, start_time: datetime, end_time: datetime) -> float:
        """Estimate revenue from partner's customers"""
        # In real implementation, this would integrate with partner's billing system
        # For now, estimate based on usage
        metrics = self.get_metrics(partner_id, start_time, end_time, TimeGranularity.MONTH)
        total_impressions = sum(m.total_widget_impressions for m in metrics)

        # Estimate $0.01 per impression
        return total_impressions * 0.01

    def _save_report(self, report: RevenueReport):
        """Save revenue report"""
        report_dir = self.storage_path / report.partner_id / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"{report.billing_period_start.strftime('%Y-%m')}.json"

        with open(report_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)


# Global analytics tracker
_analytics_tracker: Optional[AnalyticsTracker] = None


def get_analytics_tracker(storage_path: Optional[Path] = None) -> AnalyticsTracker:
    """Get or create global analytics tracker"""
    global _analytics_tracker
    if _analytics_tracker is None:
        _analytics_tracker = AnalyticsTracker(storage_path)
    return _analytics_tracker
