"""
Partner Configuration API

REST API for partners to customize themes, configure widgets,
and manage their white-label deployments.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import json
from pathlib import Path

from ..dac import DACManifest, DACTier, create_example_manifest
from .partner_manager import get_partner_manager, Partner, PartnerTier
from .analytics import get_analytics_tracker


# Pydantic models for API requests/responses

class ThemeCustomizationRequest(BaseModel):
    """Request to customize theme"""
    theme_base: str = Field(..., description="Base theme: cosmic, chrome, or light")
    custom_colors: Optional[Dict[str, str]] = Field(None, description="Custom color overrides")
    logo_url: Optional[str] = Field(None, description="URL to partner logo")
    brand_name: Optional[str] = Field(None, description="Partner brand name")
    custom_domain: Optional[str] = Field(None, description="Custom domain for deployment")


class WidgetConfigurationRequest(BaseModel):
    """Request to configure widget"""
    widget_type: str = Field(..., description="Widget type identifier")
    enabled: bool = Field(True, description="Whether widget is enabled")
    refresh_interval_ms: int = Field(5000, ge=100, description="Refresh interval in milliseconds")
    enable_animations: bool = Field(True, description="Enable animations")
    enable_websocket: bool = Field(True, description="Enable WebSocket updates")
    custom_features: Dict[str, Any] = Field(default_factory=dict, description="Custom feature flags")


class DACConfigurationRequest(BaseModel):
    """Request to configure DAC"""
    name: str = Field(..., description="DAC name")
    tier: str = Field(..., description="Deployment tier")
    target_environments: List[str] = Field(..., description="Target deployment environments")
    theme: ThemeCustomizationRequest
    widgets: List[WidgetConfigurationRequest]
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")


class PartnerDashboardResponse(BaseModel):
    """Partner dashboard summary"""
    partner_info: Dict[str, Any]
    analytics_summary: Dict[str, Any]
    active_dacs: int
    total_deployments: int
    monthly_usage: Dict[str, Any]


# API implementation

def get_partner_from_api_key(api_key: str = Header(..., alias="X-API-Key")) -> Partner:
    """Dependency to authenticate partner from API key"""
    partner_manager = get_partner_manager()
    partner = partner_manager.get_partner_by_api_key(api_key)

    if not partner:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not partner.is_active():
        raise HTTPException(status_code=403, detail="Partner account is not active")

    return partner


# Create APIRouter
router = APIRouter(
    tags=["Partner Configuration"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root():
    """API root"""
    return {
        "service": "Industriverse Partner Configuration API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@router.get("/partner/info")
async def get_partner_info(partner: Partner = Depends(get_partner_from_api_key)):
    """Get partner account information"""
    return {
        "partner_id": partner.partner_id,
        "company_name": partner.company_name,
        "tier": partner.tier,
        "status": partner.status,
        "enabled_features": partner.enabled_features,
        "created_at": partner.created_at.isoformat(),
        "total_dacs": partner.total_dacs,
    }


@router.get("/partner/dashboard")
async def get_dashboard(partner: Partner = Depends(get_partner_from_api_key)) -> PartnerDashboardResponse:
    """Get partner dashboard summary"""
    analytics = get_analytics_tracker()
    summary = analytics.get_dashboard_summary(partner.partner_id)

    return PartnerDashboardResponse(
        partner_info={
            "partner_id": partner.partner_id,
            "company_name": partner.company_name,
            "tier": partner.tier,
        },
        analytics_summary=summary,
        active_dacs=partner.billing.active_deployments if partner.billing else 0,
        total_deployments=partner.billing.total_deployments if partner.billing else 0,
        monthly_usage={
            "api_calls": partner.billing.total_api_calls if partner.billing else 0,
            "widget_impressions": partner.billing.total_widget_impressions if partner.billing else 0,
        }
    )


@router.get("/partner/analytics")
async def get_analytics(
    days: int = 30,
    granularity: str = "day",
    partner: Partner = Depends(get_partner_from_api_key)
):
    """Get detailed analytics"""
    from datetime import datetime, timedelta
    from ..partner_portal.analytics import TimeGranularity

    analytics = get_analytics_tracker()

    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    try:
        gran = TimeGranularity(granularity)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid granularity: {granularity}")

    metrics = analytics.get_metrics(partner.partner_id, start_time, end_time, gran)

    return {
        "period": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "granularity": granularity
        },
        "metrics": [m.to_dict() for m in metrics]
    }


@router.post("/theme/customize")
async def customize_theme(
    request: ThemeCustomizationRequest,
    partner: Partner = Depends(get_partner_from_api_key)
):
    """Customize partner theme"""
    # Validate theme base
    valid_themes = ["cosmic", "chrome", "light"]
    if request.theme_base not in valid_themes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid theme base. Must be one of: {valid_themes}"
        )

    # Validate custom colors against allowed overrides
    if request.custom_colors:
        # Load design tokens to check allowed overrides
        from pathlib import Path
        tokens_path = Path(__file__).parent.parent / "design_tokens.json"
        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        allowed_overrides = tokens.get('partner_customization', {}).get('allowed_overrides', [])

        for key in request.custom_colors.keys():
            # Check if override is allowed
            allowed = any(
                key.startswith(pattern.replace('*', ''))
                for pattern in allowed_overrides
            )
            if not allowed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Color override not allowed: {key}. Allowed: {allowed_overrides}"
                )

    # Update partner branding
    partner_manager = get_partner_manager()
    partner.custom_branding = {
        'theme_base': request.theme_base,
        'custom_colors': request.custom_colors,
        'logo_url': request.logo_url,
        'brand_name': request.brand_name,
        'custom_domain': request.custom_domain,
    }

    partner_manager._save_partner(partner)

    return {
        "message": "Theme customization saved",
        "theme": partner.custom_branding
    }


@router.get("/theme/current")
async def get_current_theme(partner: Partner = Depends(get_partner_from_api_key)):
    """Get current theme configuration"""
    if not partner.custom_branding:
        return {
            "theme_base": "cosmic",
            "custom_colors": None,
            "logo_url": None,
            "brand_name": partner.company_name,
            "custom_domain": None,
        }

    return partner.custom_branding


@router.get("/widgets/available")
async def list_available_widgets(partner: Partner = Depends(get_partner_from_api_key)):
    """List widgets available for partner's tier"""
    # All widgets
    all_widgets = [
        {
            "widget_type": "ai-shield-dashboard",
            "name": "AI Shield Dashboard",
            "description": "Real-time threat monitoring and security status",
            "category": "security",
            "min_tier": "security-essentials"
        },
        {
            "widget_type": "compliance-score",
            "name": "Compliance Score",
            "description": "NIST, ISO, GDPR, SOC 2 compliance tracking",
            "category": "compliance",
            "min_tier": "security-essentials"
        },
        {
            "widget_type": "threat-heatmap",
            "name": "Threat Heatmap",
            "description": "Thermodynamic threat topology visualization",
            "category": "security",
            "min_tier": "domain-intelligence"
        },
        {
            "widget_type": "security-orb",
            "name": "Security Orb",
            "description": "Ambient threat level indicator",
            "category": "security",
            "min_tier": "security-essentials"
        },
        {
            "widget_type": "energy-flow-graph",
            "name": "Energy Flow Graph",
            "description": "Operational thermodynamics and efficiency",
            "category": "operations",
            "min_tier": "domain-intelligence"
        },
        {
            "widget_type": "predictive-maintenance",
            "name": "Predictive Maintenance",
            "description": "AI-powered failure forecasting",
            "category": "operations",
            "min_tier": "domain-intelligence"
        },
        {
            "widget_type": "shadow-twin-3d",
            "name": "Shadow Twin 3D",
            "description": "Interactive 3D system visualization",
            "category": "discovery",
            "min_tier": "full-discovery"
        },
        {
            "widget_type": "research-explorer",
            "name": "Research Explorer",
            "description": "I³ knowledge graph and research browser",
            "category": "discovery",
            "min_tier": "full-discovery"
        },
    ]

    # Filter by partner tier
    tier_hierarchy = {
        "security-essentials": 0,
        "domain-intelligence": 1,
        "full-discovery": 2,
    }

    partner_tier_level = tier_hierarchy.get(partner.tier, 0)

    available = [
        w for w in all_widgets
        if tier_hierarchy.get(w["min_tier"], 0) <= partner_tier_level
    ]

    return {
        "partner_tier": partner.tier,
        "total_available": len(available),
        "widgets": available
    }


@router.post("/dac/configure")
async def configure_dac(
    request: DACConfigurationRequest,
    partner: Partner = Depends(get_partner_from_api_key)
):
    """Configure a new DAC"""
    from ..dac import (
        DACManifest,
        ResourceRequirements,
        NetworkConfig,
        SecurityConfig,
        ThemeCustomization,
        WidgetConfig,
        ManifestValidator
    )

    # Map tier string to enum
    try:
        tier = DACTier(request.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")

    # Check tier matches partner tier
    if tier.value != partner.tier:
        raise HTTPException(
            status_code=403,
            detail=f"Partner tier ({partner.tier}) does not match requested tier ({tier.value})"
        )

    # Set up resources based on tier
    resources_map = {
        "security-essentials": ResourceRequirements(cpu_cores=2.0, memory_gb=4.0, storage_gb=50.0),
        "domain-intelligence": ResourceRequirements(cpu_cores=4.0, memory_gb=8.0, storage_gb=100.0),
        "full-discovery": ResourceRequirements(cpu_cores=8.0, memory_gb=16.0, storage_gb=200.0, gpu_required=True, gpu_memory_gb=8.0),
    }

    # Create manifest
    manifest = DACManifest(
        name=request.name,
        version="1.0.0",
        description=f"{partner.company_name} - {request.tier}",
        partner_id=partner.partner_id,
        tier=tier.value,
        target_environments=request.target_environments,
        resources=resources_map[tier.value],
        network=NetworkConfig(
            api_endpoint="https://api.industriverse.ai"
        ),
        security=SecurityConfig(
            allowed_origins=request.allowed_origins if request.allowed_origins else [f"https://{partner.company_name.lower()}.com"]
        ),
        widgets=[
            WidgetConfig(
                widget_type=w.widget_type,
                enabled=w.enabled,
                refresh_interval_ms=w.refresh_interval_ms,
                enable_animations=w.enable_animations,
                enable_websocket=w.enable_websocket,
                custom_features=w.custom_features
            )
            for w in request.widgets
        ],
        theme=ThemeCustomization(
            theme_base=request.theme.theme_base,
            custom_colors=request.theme.custom_colors,
            logo_url=request.theme.logo_url,
            brand_name=request.theme.brand_name or partner.company_name,
            custom_domain=request.theme.custom_domain
        ),
        features=partner.enabled_features
    )

    # Validate manifest
    is_valid, errors = ManifestValidator.validate(manifest)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid manifest: {', '.join(errors)}")

    # Register with DAC registry
    from ..dac import get_dac_registry

    registry = get_dac_registry()
    package = registry.register(manifest)

    # Update partner stats
    partner_manager = get_partner_manager()
    partner_manager.record_deployment(partner.partner_id)

    return {
        "message": "DAC configured successfully",
        "dac_id": package.dac_id,
        "manifest_version": manifest.version,
        "widgets_configured": len(manifest.widgets),
    }


@router.get("/dac/list")
async def list_dacs(partner: Partner = Depends(get_partner_from_api_key)):
    """List partner's DACs"""
    from ..dac import get_dac_registry

    registry = get_dac_registry()
    packages = registry.get_by_partner(partner.partner_id)

    return {
        "total": len(packages),
        "dacs": [
            {
                "dac_id": p.dac_id,
                "name": p.name,
                "tier": p.tier,
                "latest_version": p.latest_version,
                "total_deployments": p.total_deployments,
                "active_deployments": p.active_deployments,
                "created_at": p.created_at.isoformat(),
            }
            for p in packages
        ]
    }


@router.get("/dac/{dac_id}/manifest")
async def get_dac_manifest(
    dac_id: str,
    version: Optional[str] = None,
    partner: Partner = Depends(get_partner_from_api_key)
):
    """Get DAC manifest"""
    from ..dac import get_dac_registry

    # Verify DAC belongs to partner
    if not dac_id.startswith(f"{partner.partner_id}:"):
        raise HTTPException(status_code=403, detail="Access denied")

    registry = get_dac_registry()
    manifest = registry.get_manifest(dac_id, version)

    if not manifest:
        raise HTTPException(status_code=404, detail="DAC not found")

    return manifest.to_dict()


@router.get("/billing/current")
async def get_current_billing(partner: Partner = Depends(get_partner_from_api_key)):
    """Get current billing information"""
    if not partner.billing:
        raise HTTPException(status_code=404, detail="No billing information available")

    return {
        "tier": partner.billing.tier,
        "monthly_fee": partner.billing.monthly_fee,
        "revenue_share_percent": partner.billing.revenue_share_percent,
        "next_billing_date": partner.billing.next_billing_date.isoformat() if partner.billing.next_billing_date else None,
        "usage": {
            "total_deployments": partner.billing.total_deployments,
            "active_deployments": partner.billing.active_deployments,
            "total_api_calls": partner.billing.total_api_calls,
            "total_widget_impressions": partner.billing.total_widget_impressions,
        }
    }


@router.get("/billing/invoice/preview")
async def preview_invoice(partner: Partner = Depends(get_partner_from_api_key)):
    """Preview next invoice"""
    from datetime import datetime, timedelta

    analytics = get_analytics_tracker()

    # Generate preview for current month
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

    report = analytics.generate_revenue_report(
        partner_id=partner.partner_id,
        billing_period_start=start_of_month,
        billing_period_end=end_of_month,
        base_subscription_fee=partner.billing.monthly_fee,
        tier=partner.tier,
        revenue_share_percent=partner.billing.revenue_share_percent
    )

    return report.to_dict()


# Error handlers

# Error handlers - Handled by main app


# Run with: uvicorn configuration_api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
