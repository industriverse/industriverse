"""
Partner Portal

Self-service platform for partners to configure white-label deployments,
customize themes, track analytics, and manage billing.

Components:
- Partner management and authentication
- Analytics and metrics tracking
- Revenue reporting and billing
- Configuration API
- Theme customization
- Widget configuration
"""

from .partner_manager import (
    Partner,
    PartnerTier,
    PartnerStatus,
    PartnerManager,
    PartnerContact,
    PartnerCredentials,
    PartnerBilling,
    get_partner_manager,
)

from .analytics import (
    AnalyticsTracker,
    MetricType,
    TimeGranularity,
    MetricEvent,
    AggregatedMetrics,
    RevenueReport,
    get_analytics_tracker,
)

from .configuration_api import app as config_api_app

__all__ = [
    # Partner Management
    "Partner",
    "PartnerTier",
    "PartnerStatus",
    "PartnerManager",
    "PartnerContact",
    "PartnerCredentials",
    "PartnerBilling",
    "get_partner_manager",

    # Analytics
    "AnalyticsTracker",
    "MetricType",
    "TimeGranularity",
    "MetricEvent",
    "AggregatedMetrics",
    "RevenueReport",
    "get_analytics_tracker",

    # API
    "config_api_app",
]
