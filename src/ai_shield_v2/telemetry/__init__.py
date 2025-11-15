"""
AI Shield v2 - Telemetry Module
================================

High-throughput telemetry ingestion and processing pipeline.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .telemetry_pipeline import (
    # Main pipeline
    TelemetryIngestionPipeline,

    # Enums
    TelemetrySource,
    TelemetryStatus,

    # Data classes
    TelemetryRecord,
    ProcessedTelemetry,
    PipelineMetrics,

    # Utilities
    TelemetryValidator,
    TelemetryNormalizer
)

__all__ = [
    "TelemetryIngestionPipeline",
    "TelemetrySource",
    "TelemetryStatus",
    "TelemetryRecord",
    "ProcessedTelemetry",
    "PipelineMetrics",
    "TelemetryValidator",
    "TelemetryNormalizer"
]
