"""
Integration Hub

Production-grade connectors for external systems:
- S3: Cloud storage for energy maps and checkpoints
- InfluxDB: Time-series telemetry and metrics
- Neo4j: Energy Atlas graph database
- IoT: Device adapters for sensors and industrial equipment
"""

from .s3_connector import (
    S3Connector,
    S3Config,
    S3Object,
    get_s3_connector,
    save_energy_map_to_s3,
    load_energy_map_from_s3
)

from .influxdb_connector import (
    InfluxDBConnector,
    InfluxDBConfig,
    MeasurementType,
    TimeSeriesPoint,
    get_influxdb_connector,
    write_energy_metric,
    query_energy_metrics
)

from .neo4j_connector import (
    Neo4jConnector,
    Neo4jConfig,
    NodeType,
    RelationType,
    get_neo4j_connector,
    create_energy_network
)

from .iot_adapters import (
    IoTDeviceManager,
    MQTTAdapter,
    MQTTConfig,
    Device,
    DeviceType,
    DeviceReading,
    Protocol,
    EnergySensorAdapter,
    get_iot_manager,
    register_energy_sensor
)

__all__ = [
    # S3
    "S3Connector",
    "S3Config",
    "S3Object",
    "get_s3_connector",
    "save_energy_map_to_s3",
    "load_energy_map_from_s3",

    # InfluxDB
    "InfluxDBConnector",
    "InfluxDBConfig",
    "MeasurementType",
    "TimeSeriesPoint",
    "get_influxdb_connector",
    "write_energy_metric",
    "query_energy_metrics",

    # Neo4j
    "Neo4jConnector",
    "Neo4jConfig",
    "NodeType",
    "RelationType",
    "get_neo4j_connector",
    "create_energy_network",

    # IoT
    "IoTDeviceManager",
    "MQTTAdapter",
    "MQTTConfig",
    "Device",
    "DeviceType",
    "DeviceReading",
    "Protocol",
    "EnergySensorAdapter",
    "get_iot_manager",
    "register_energy_sensor",
]
