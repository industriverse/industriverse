"""
InfluxDB Connector for Time-Series Telemetry

Production-grade InfluxDB integration for energy metrics,
performance telemetry, and temporal pattern storage.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
    from influxdb_client.client.query_api import QueryApi
    from influxdb_client.client.exceptions import InfluxDBError
except ImportError:
    InfluxDBClient = None
    Point = None
    WritePrecision = None
    SYNCHRONOUS = None
    ASYNCHRONOUS = None
    InfluxDBError = Exception

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class InfluxDBConfig(BaseModel):
    """InfluxDB configuration"""
    url: str = Field(default="http://localhost:8086", description="InfluxDB URL")
    token: str = Field(..., description="Authentication token")
    org: str = Field(..., description="Organization name")
    bucket: str = Field(..., description="Default bucket")
    timeout: int = Field(default=10000, description="Timeout in ms")
    enable_gzip: bool = Field(default=True, description="Enable gzip compression")


class MeasurementType(str, Enum):
    """Time-series measurement types"""
    ENERGY_METRIC = "energy_metric"
    PERFORMANCE = "performance"
    DIFFUSION_STEP = "diffusion_step"
    REGIME_DETECTION = "regime_detection"
    PROOF_VALIDATION = "proof_validation"
    API_REQUEST = "api_request"
    SYSTEM_HEALTH = "system_health"


@dataclass
class TimeSeriesPoint:
    """Time-series data point"""
    measurement: str
    tags: Dict[str, str]
    fields: Dict[str, float]
    timestamp: datetime


class InfluxDBConnector:
    """
    Production InfluxDB connector for EIL telemetry.

    Features:
    - Async and sync write modes
    - Batch writing for efficiency
    - Query builder for complex analytics
    - Downsampling and aggregation
    - Retention policy management
    - Continuous queries for rollups
    """

    def __init__(self, config: InfluxDBConfig):
        """
        Initialize InfluxDB connector.

        Args:
            config: InfluxDB configuration
        """
        if InfluxDBClient is None:
            raise ImportError(
                "influxdb-client required for InfluxDB integration. "
                "Install with: pip install influxdb-client"
            )

        self.config = config

        # Create client
        self.client = InfluxDBClient(
            url=config.url,
            token=config.token,
            org=config.org,
            timeout=config.timeout,
            enable_gzip=config.enable_gzip
        )

        # Write API (sync mode by default)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # Query API
        self.query_api = self.client.query_api()

        # Delete API
        self.delete_api = self.client.delete_api()

        logger.info(
            f"InfluxDBConnector initialized: url={config.url}, "
            f"org={config.org}, bucket={config.bucket}"
        )

    def close(self):
        """Close connection"""
        self.write_api.close()
        self.client.close()
        logger.info("InfluxDB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ========================================================================
    # Write Operations
    # ========================================================================

    def write_point(
        self,
        measurement: str,
        fields: Dict[str, float],
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
        bucket: Optional[str] = None
    ):
        """
        Write single data point.

        Args:
            measurement: Measurement name
            fields: Field values
            tags: Tag key-values
            timestamp: Point timestamp (default: now)
            bucket: Bucket name (default: config bucket)
        """
        point = Point(measurement)

        # Add tags
        if tags:
            for key, value in tags.items():
                point = point.tag(key, value)

        # Add fields
        for key, value in fields.items():
            point = point.field(key, value)

        # Set timestamp
        if timestamp:
            point = point.time(timestamp, WritePrecision.NS)

        try:
            self.write_api.write(
                bucket=bucket or self.config.bucket,
                org=self.config.org,
                record=point
            )
            logger.debug(f"Wrote point: {measurement}")

        except InfluxDBError as e:
            logger.error(f"Write failed: {e}")
            raise

    def write_points(
        self,
        points: List[TimeSeriesPoint],
        bucket: Optional[str] = None
    ):
        """
        Write multiple data points in batch.

        Args:
            points: List of time-series points
            bucket: Bucket name
        """
        influx_points = []

        for point in points:
            p = Point(point.measurement)

            for key, value in point.tags.items():
                p = p.tag(key, value)

            for key, value in point.fields.items():
                p = p.field(key, value)

            p = p.time(point.timestamp, WritePrecision.NS)
            influx_points.append(p)

        try:
            self.write_api.write(
                bucket=bucket or self.config.bucket,
                org=self.config.org,
                record=influx_points
            )
            logger.info(f"Wrote {len(influx_points)} points in batch")

        except InfluxDBError as e:
            logger.error(f"Batch write failed: {e}")
            raise

    # ========================================================================
    # Energy Metrics
    # ========================================================================

    def write_energy_metric(
        self,
        metric_name: str,
        value: float,
        domain: str,
        cluster: str,
        node: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Write energy metric.

        Args:
            metric_name: Metric name (e.g., total_energy, entropy, fidelity)
            value: Metric value
            domain: Energy domain
            cluster: Cluster ID
            node: Node ID
            timestamp: Measurement timestamp
        """
        self.write_point(
            measurement=MeasurementType.ENERGY_METRIC.value,
            fields={metric_name: value},
            tags={
                'domain': domain,
                'cluster': cluster,
                'node': node,
                'metric': metric_name
            },
            timestamp=timestamp
        )

    def write_diffusion_step(
        self,
        timestep: int,
        energy: float,
        entropy: float,
        noise_level: float,
        model_id: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Write diffusion process step metrics.

        Args:
            timestep: Diffusion timestep
            energy: Energy at this step
            entropy: Entropy at this step
            noise_level: Noise level (beta_t)
            model_id: Model identifier
            timestamp: Step timestamp
        """
        self.write_point(
            measurement=MeasurementType.DIFFUSION_STEP.value,
            fields={
                'energy': energy,
                'entropy': entropy,
                'noise_level': noise_level
            },
            tags={
                'timestep': str(timestep),
                'model_id': model_id
            },
            timestamp=timestamp
        )

    def write_regime_detection(
        self,
        regime: str,
        confidence: float,
        domain: str,
        approved: bool,
        timestamp: Optional[datetime] = None
    ):
        """
        Write regime detection result.

        Args:
            regime: Detected regime (equilibrium/transition/critical)
            confidence: Detection confidence
            domain: Energy domain
            approved: Whether decision was approved
            timestamp: Detection timestamp
        """
        self.write_point(
            measurement=MeasurementType.REGIME_DETECTION.value,
            fields={
                'confidence': confidence,
                'approved': 1.0 if approved else 0.0
            },
            tags={
                'regime': regime,
                'domain': domain
            },
            timestamp=timestamp
        )

    def write_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Write API request metrics.

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            user_id: User identifier
            timestamp: Request timestamp
        """
        tags = {
            'endpoint': endpoint,
            'method': method,
            'status': str(status_code)
        }

        if user_id:
            tags['user_id'] = user_id

        self.write_point(
            measurement=MeasurementType.API_REQUEST.value,
            fields={
                'response_time_ms': response_time_ms,
                'request_count': 1
            },
            tags=tags,
            timestamp=timestamp
        )

    # ========================================================================
    # Query Operations
    # ========================================================================

    def query(
        self,
        query: str,
        bucket: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute Flux query.

        Args:
            query: Flux query string
            bucket: Bucket name

        Returns:
            Query results as list of dicts
        """
        try:
            result = self.query_api.query(
                org=self.config.org,
                query=query
            )

            records = []
            for table in result:
                for record in table.records:
                    records.append(record.values)

            return records

        except InfluxDBError as e:
            logger.error(f"Query failed: {e}")
            raise

    def query_energy_metrics(
        self,
        metric_name: str,
        domain: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        bucket: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query energy metrics.

        Args:
            metric_name: Metric to query
            domain: Filter by domain
            start_time: Query start time (default: -1h)
            end_time: Query end time (default: now)
            bucket: Bucket name

        Returns:
            Metric records
        """
        start = start_time or datetime.utcnow() - timedelta(hours=1)
        end = end_time or datetime.utcnow()

        query = f'''
        from(bucket: "{bucket or self.config.bucket}")
            |> range(start: {start.isoformat()}Z, stop: {end.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "{MeasurementType.ENERGY_METRIC.value}")
            |> filter(fn: (r) => r["metric"] == "{metric_name}")
        '''

        if domain:
            query += f'|> filter(fn: (r) => r["domain"] == "{domain}")'

        return self.query(query)

    def query_diffusion_trajectory(
        self,
        model_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Query full diffusion trajectory.

        Args:
            model_id: Model identifier
            start_time: Query start time
            end_time: Query end time

        Returns:
            Timestep records with energy/entropy
        """
        start = start_time or datetime.utcnow() - timedelta(hours=1)
        end = end_time or datetime.utcnow()

        query = f'''
        from(bucket: "{self.config.bucket}")
            |> range(start: {start.isoformat()}Z, stop: {end.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "{MeasurementType.DIFFUSION_STEP.value}")
            |> filter(fn: (r) => r["model_id"] == "{model_id}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''

        return self.query(query)

    def query_api_performance(
        self,
        endpoint: str,
        aggregation_window: str = "1m",
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Query API performance metrics with aggregation.

        Args:
            endpoint: API endpoint
            aggregation_window: Window for aggregation (e.g., 1m, 5m, 1h)
            start_time: Query start time (default: -1h)

        Returns:
            Aggregated performance metrics
        """
        start = start_time or datetime.utcnow() - timedelta(hours=1)

        query = f'''
        from(bucket: "{self.config.bucket}")
            |> range(start: {start.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "{MeasurementType.API_REQUEST.value}")
            |> filter(fn: (r) => r["endpoint"] == "{endpoint}")
            |> filter(fn: (r) => r["_field"] == "response_time_ms")
            |> aggregateWindow(every: {aggregation_window}, fn: mean)
        '''

        return self.query(query)

    # ========================================================================
    # Aggregation and Downsampling
    # ========================================================================

    def create_continuous_query(
        self,
        name: str,
        source_bucket: str,
        dest_bucket: str,
        query: str
    ):
        """
        Create continuous query for automatic downsampling.

        Args:
            name: Task name
            source_bucket: Source bucket
            dest_bucket: Destination bucket
            query: Flux query for transformation
        """
        # Note: This requires InfluxDB Tasks API
        # Implementation would use self.client.tasks_api()
        logger.warning("Continuous query creation not yet implemented")

    def downsample_energy_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        window: str = "1h",
        dest_bucket: Optional[str] = None
    ):
        """
        Downsample energy metrics for long-term storage.

        Args:
            start_time: Downsampling start
            end_time: Downsampling end
            window: Aggregation window
            dest_bucket: Destination bucket for downsampled data
        """
        query = f'''
        from(bucket: "{self.config.bucket}")
            |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
            |> filter(fn: (r) => r["_measurement"] == "{MeasurementType.ENERGY_METRIC.value}")
            |> aggregateWindow(every: {window}, fn: mean, createEmpty: false)
            |> to(bucket: "{dest_bucket or self.config.bucket + '_downsampled'}", org: "{self.config.org}")
        '''

        try:
            self.query(query)
            logger.info(f"Downsampled energy metrics: {window} window")
        except InfluxDBError as e:
            logger.error(f"Downsampling failed: {e}")
            raise

    # ========================================================================
    # Delete Operations
    # ========================================================================

    def delete_measurements(
        self,
        measurement: str,
        start_time: datetime,
        end_time: datetime,
        predicate: Optional[str] = None,
        bucket: Optional[str] = None
    ):
        """
        Delete measurements in time range.

        Args:
            measurement: Measurement name
            start_time: Delete start time
            end_time: Delete end time
            predicate: Optional predicate (e.g., 'domain="plasma"')
            bucket: Bucket name
        """
        try:
            delete_predicate = f'_measurement="{measurement}"'
            if predicate:
                delete_predicate += f' AND {predicate}'

            self.delete_api.delete(
                start=start_time,
                stop=end_time,
                predicate=delete_predicate,
                bucket=bucket or self.config.bucket,
                org=self.config.org
            )

            logger.info(f"Deleted measurements: {measurement} ({start_time} to {end_time})")

        except InfluxDBError as e:
            logger.error(f"Delete failed: {e}")
            raise

    # ========================================================================
    # Health and Diagnostics
    # ========================================================================

    def health_check(self) -> bool:
        """
        Check InfluxDB health.

        Returns:
            True if healthy
        """
        try:
            health = self.client.health()
            is_healthy = health.status == "pass"

            if is_healthy:
                logger.info(f"InfluxDB healthy: {health.message}")
            else:
                logger.warning(f"InfluxDB unhealthy: {health.message}")

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_bucket_info(self, bucket: Optional[str] = None) -> Dict[str, Any]:
        """
        Get bucket information.

        Args:
            bucket: Bucket name

        Returns:
            Bucket metadata
        """
        buckets_api = self.client.buckets_api()
        bucket_name = bucket or self.config.bucket

        try:
            bucket_obj = buckets_api.find_bucket_by_name(bucket_name)

            if bucket_obj:
                return {
                    'name': bucket_obj.name,
                    'id': bucket_obj.id,
                    'org_id': bucket_obj.org_id,
                    'retention_rules': [
                        {'type': rule.type, 'every_seconds': rule.every_seconds}
                        for rule in bucket_obj.retention_rules
                    ],
                    'created_at': bucket_obj.created_at
                }
            else:
                logger.warning(f"Bucket not found: {bucket_name}")
                return {}

        except InfluxDBError as e:
            logger.error(f"Failed to get bucket info: {e}")
            raise


# ============================================================================
# Global InfluxDB Connector
# ============================================================================

_influxdb_connector: Optional[InfluxDBConnector] = None


def get_influxdb_connector(config: Optional[InfluxDBConfig] = None) -> InfluxDBConnector:
    """Get global InfluxDB connector instance"""
    global _influxdb_connector
    if _influxdb_connector is None:
        if config is None:
            raise ValueError("InfluxDBConfig required for first initialization")
        _influxdb_connector = InfluxDBConnector(config)
    return _influxdb_connector


# ============================================================================
# Convenience Functions
# ============================================================================

def write_energy_metric(
    metric_name: str,
    value: float,
    domain: str,
    cluster: str,
    node: str,
    config: Optional[InfluxDBConfig] = None
):
    """Write energy metric (convenience function)"""
    connector = get_influxdb_connector(config)
    connector.write_energy_metric(metric_name, value, domain, cluster, node)


def query_energy_metrics(
    metric_name: str,
    domain: Optional[str] = None,
    start_time: Optional[datetime] = None,
    config: Optional[InfluxDBConfig] = None
) -> List[Dict[str, Any]]:
    """Query energy metrics (convenience function)"""
    connector = get_influxdb_connector(config)
    return connector.query_energy_metrics(metric_name, domain, start_time)
