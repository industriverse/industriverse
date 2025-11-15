"""
AI Shield v2 - Telemetry Module
================================

High-throughput telemetry ingestion and processing pipeline.

Phase 1: Base telemetry pipeline (>10k samples/sec)
Phase 4: Multi-layer aggregation and correlation (>100k samples/sec)

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

from .multi_layer_aggregator import (
    # Multi-layer aggregator (Phase 4.1)
    MultiLayerAggregator,
    LayerExtractor,
    TemporalAligner,

    # Enums
    TelemetryLayer,
    AggregationStatus,

    # Data classes
    LayerData,
    AggregatedTelemetry,
    AggregatorMetrics
)

from .cross_layer_correlator import (
    # Cross-layer correlator (Phase 4.2)
    CrossLayerCorrelator,
    StatisticalCorrelator,
    PatternDetector,

    # Enums
    CorrelationType,
    CorrelationStrength,
    AttackPattern,

    # Data classes
    CorrelationPair,
    CrossLayerPattern,
    CorrelationAnalysis,
    CorrelatorMetrics
)

from .high_throughput_pipeline import (
    # High-throughput pipeline (Phase 4.3)
    HighThroughputPipeline,
    ParallelPipelineExecutor,
    BatchCollector,
    VectorizedProcessor,

    # Enums
    ProcessingMode,

    # Data classes
    BatchProcessingConfig,
    ThroughputMetrics
)

__all__ = [
    # Phase 1: Base pipeline
    "TelemetryIngestionPipeline",
    "TelemetrySource",
    "TelemetryStatus",
    "TelemetryRecord",
    "ProcessedTelemetry",
    "PipelineMetrics",
    "TelemetryValidator",
    "TelemetryNormalizer",

    # Phase 4.1: Multi-layer aggregation
    "MultiLayerAggregator",
    "LayerExtractor",
    "TemporalAligner",
    "TelemetryLayer",
    "AggregationStatus",
    "LayerData",
    "AggregatedTelemetry",
    "AggregatorMetrics",

    # Phase 4.2: Cross-layer correlation
    "CrossLayerCorrelator",
    "StatisticalCorrelator",
    "PatternDetector",
    "CorrelationType",
    "CorrelationStrength",
    "AttackPattern",
    "CorrelationPair",
    "CrossLayerPattern",
    "CorrelationAnalysis",
    "CorrelatorMetrics",

    # Phase 4.3: High-throughput optimization
    "HighThroughputPipeline",
    "ParallelPipelineExecutor",
    "BatchCollector",
    "VectorizedProcessor",
    "ProcessingMode",
    "BatchProcessingConfig",
    "ThroughputMetrics"
]
