# White-Label API Reference

Complete API documentation for the Industriverse White-Label Platform.

**Base URL**: `https://api.industriverse.ai/v2`

**Authentication**: API Key via `X-API-Key` header

## Table of Contents

1. [Authentication](#authentication)
2. [Partner Management](#partner-management)
3. [Theme Customization](#theme-customization)
4. [Widget Configuration](#widget-configuration)
5. [DAC Management](#dac-management)
6. [Analytics](#analytics)
7. [Billing](#billing)
8. [Marketplace](#marketplace) (Tier 3 only)
9. [Rate Limits](#rate-limits)
10. [Error Handling](#error-handling)

---

## Authentication

All API requests require authentication via API key.

### Headers

```
X-API-Key: iv_your_api_key_here
Content-Type: application/json
```

### Example Request

```bash
curl -X GET \
  https://api.industriverse.ai/v2/partner/info \
  -H "X-API-Key: iv_xxxxxxxxxxxxxx"
```

---

## Partner Management

### GET /partner/info

Get partner account information.

**Response**:
```json
{
  "partner_id": "acme-corp",
  "company_name": "Acme Corporation",
  "tier": "domain-intelligence",
  "status": "active",
  "enabled_features": {
    "ai_shield": true,
    "compliance": true,
    "predictive_maintenance": true
  },
  "created_at": "2024-01-15T10:00:00Z",
  "total_dacs": 3
}
```

---

### GET /partner/dashboard

Get partner dashboard summary.

**Response**:
```json
{
  "partner_info": {
    "partner_id": "acme-corp",
    "company_name": "Acme Corporation",
    "tier": "domain-intelligence"
  },
  "analytics_summary": {
    "total_api_calls": 1250000,
    "total_widget_impressions": 45000,
    "total_deployments": 3,
    "active_users": 1250
  },
  "active_dacs": 3,
  "total_deployments": 5,
  "monthly_usage": {
    "api_calls": 125000,
    "widget_impressions": 4500
  }
}
```

---

## Theme Customization

### POST /theme/customize

Customize partner theme.

**Request Body**:
```json
{
  "theme_base": "cosmic",
  "custom_colors": {
    "primary": "#1E40AF",
    "accent": "#F59E0B"
  },
  "logo_url": "https://acme.com/logo.svg",
  "brand_name": "Acme Security Platform",
  "custom_domain": "security.acme.com"
}
```

**Allowed `theme_base` values**:
- `cosmic`: Dark theme with plasma effects (default)
- `chrome`: Light professional theme
- `light`: Minimal light theme

**Allowed `custom_colors` keys**:
- `colors.primary`: Primary brand color
- `colors.accent`: Accent/highlight color
- `colors.text-primary`: Primary text color (light themes only)

**Response**:
```json
{
  "message": "Theme customization saved",
  "theme": {
    "theme_base": "cosmic",
    "custom_colors": {
      "primary": "#1E40AF",
      "accent": "#F59E0B"
    },
    "logo_url": "https://acme.com/logo.svg",
    "brand_name": "Acme Security Platform",
    "custom_domain": "security.acme.com"
  }
}
```

**Errors**:
- `400`: Invalid theme base or color override not allowed
- `401`: Invalid API key
- `403`: Partner account not active

---

### GET /theme/current

Get current theme configuration.

**Response**:
```json
{
  "theme_base": "cosmic",
  "custom_colors": {
    "primary": "#1E40AF",
    "accent": "#F59E0B"
  },
  "logo_url": "https://acme.com/logo.svg",
  "brand_name": "Acme Security Platform",
  "custom_domain": "security.acme.com"
}
```

---

## Widget Configuration

### GET /widgets/available

List widgets available for partner's tier.

**Response**:
```json
{
  "partner_tier": "domain-intelligence",
  "total_available": 6,
  "widgets": [
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
      "widget_type": "energy-flow-graph",
      "name": "Energy Flow Graph",
      "description": "Operational thermodynamics and efficiency",
      "category": "operations",
      "min_tier": "domain-intelligence"
    }
  ]
}
```

**Widget Categories**:
- `security`: Security monitoring and threat detection
- `compliance`: Regulatory compliance tracking
- `operations`: Operational efficiency and maintenance
- `discovery`: Research and knowledge discovery

---

## DAC Management

### POST /dac/configure

Configure a new DAC (Deploy Anywhere Capsule).

**Request Body**:
```json
{
  "name": "acme-security-platform",
  "tier": "domain-intelligence",
  "target_environments": ["kubernetes", "docker"],

  "theme": {
    "theme_base": "cosmic",
    "custom_colors": {
      "primary": "#1E40AF"
    },
    "logo_url": "https://acme.com/logo.svg",
    "brand_name": "Acme Security"
  },

  "widgets": [
    {
      "widget_type": "ai-shield-dashboard",
      "enabled": true,
      "refresh_interval_ms": 5000,
      "enable_animations": true,
      "enable_websocket": true
    },
    {
      "widget_type": "compliance-score",
      "enabled": true,
      "refresh_interval_ms": 10000,
      "custom_features": {
        "frameworks": ["NIST", "ISO27001"]
      }
    }
  ],

  "allowed_origins": [
    "https://security.acme.com",
    "https://app.acme.com"
  ],

  "webhook_url": "https://acme.com/webhooks/industriverse"
}
```

**Target Environments**:
- `kubernetes`: Kubernetes deployment manifests
- `docker`: Docker Compose configuration
- `aws`: AWS ECS task definitions
- `gcp`: Google Cloud Run configurations
- `azure`: Azure Container Apps specs

**Widget Configuration Fields**:
- `widget_type` (required): Widget identifier
- `enabled` (optional, default: `true`): Enable/disable widget
- `refresh_interval_ms` (optional, default: `5000`): Refresh interval (100-60000)
- `enable_animations` (optional, default: `true`): Enable animations
- `enable_websocket` (optional, default: `true`): Enable WebSocket updates
- `custom_features` (optional): Widget-specific features

**Response**:
```json
{
  "message": "DAC configured successfully",
  "dac_id": "acme-corp:acme-security-platform",
  "manifest_version": "1.0.0",
  "widgets_configured": 2
}
```

**Errors**:
- `400`: Invalid tier, widget not available, or validation error
- `403`: Partner tier doesn't match requested tier

---

### GET /dac/list

List partner's DACs.

**Response**:
```json
{
  "total": 3,
  "dacs": [
    {
      "dac_id": "acme-corp:acme-security-platform",
      "name": "acme-security-platform",
      "tier": "domain-intelligence",
      "latest_version": "1.2.0",
      "total_deployments": 5,
      "active_deployments": 3,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

### GET /dac/{dac_id}/manifest

Get DAC manifest (YAML or JSON).

**Query Parameters**:
- `version` (optional): Specific version (default: latest)
- `format` (optional): `yaml` or `json` (default: `json`)

**Response**:
```json
{
  "name": "acme-security-platform",
  "version": "1.2.0",
  "tier": "domain-intelligence",
  "target_environments": ["kubernetes", "docker"],
  "resources": {
    "cpu_cores": 4.0,
    "memory_gb": 8.0,
    "storage_gb": 100.0,
    "gpu_required": false
  },
  "widgets": [...],
  "theme": {...}
}
```

---

### GET /dac/{dac_id}/download

Download DAC deployment package.

**Query Parameters**:
- `version` (optional): Specific version (default: latest)
- `environment` (optional): Specific environment (default: all)

**Response**: Binary `.tar.gz` file

**Example**:
```bash
curl -H "X-API-Key: your_api_key" \
  "https://api.industriverse.ai/v2/dac/acme-corp:acme-security-platform/download" \
  -o dac-package.tar.gz
```

---

## Analytics

### GET /partner/analytics

Get detailed analytics.

**Query Parameters**:
- `days` (optional, default: `30`): Number of days to retrieve
- `granularity` (optional, default: `day`): `hour`, `day`, `week`, or `month`

**Response**:
```json
{
  "period": {
    "start": "2024-11-01T00:00:00Z",
    "end": "2024-11-30T23:59:59Z",
    "granularity": "day"
  },
  "metrics": [
    {
      "timestamp": "2024-11-01T00:00:00Z",
      "api_calls": 4250,
      "widget_impressions": 150,
      "active_deployments": 3,
      "unique_users": 42,
      "error_rate": 0.002
    },
    {
      "timestamp": "2024-11-02T00:00:00Z",
      "api_calls": 4100,
      "widget_impressions": 145,
      "active_deployments": 3,
      "unique_users": 38,
      "error_rate": 0.001
    }
  ]
}
```

---

## Billing

### GET /billing/current

Get current billing information.

**Response**:
```json
{
  "tier": "domain-intelligence",
  "monthly_fee": 35000.00,
  "revenue_share_percent": 35.0,
  "next_billing_date": "2024-12-01T00:00:00Z",
  "usage": {
    "total_deployments": 5,
    "active_deployments": 3,
    "total_api_calls": 1250000,
    "total_widget_impressions": 45000
  }
}
```

---

### GET /billing/invoice/preview

Preview next invoice.

**Response**:
```json
{
  "billing_period": {
    "start": "2024-11-01T00:00:00Z",
    "end": "2024-11-30T23:59:59Z"
  },
  "base_subscription": 35000.00,
  "usage_charges": {
    "api_calls_overage": 125.00,
    "deployment_overage": 500.00,
    "total": 625.00
  },
  "revenue_share": {
    "gross_revenue": 15000.00,
    "partner_share_percent": 35.0,
    "partner_share_amount": 5250.00
  },
  "total_due": 30375.00,
  "breakdown": [
    {
      "description": "Domain Intelligence Tier - November 2024",
      "amount": 35000.00
    },
    {
      "description": "API calls overage (125,000 calls @ $0.001)",
      "amount": 125.00
    },
    {
      "description": "Revenue share (35% of $15,000)",
      "amount": -5250.00
    }
  ]
}
```

---

## Marketplace

**Note**: Only available for Tier 3 (Full Discovery) partners.

### POST /marketplace/insights/list

List insight on marketplace.

**Request Body**:
```json
{
  "utid": "UTID-20241119-a1b2c3d4-095",
  "title": "Novel Quantum Computing Error Correction",
  "description": "Breakthrough method for reducing quantum decoherence",
  "listing_type": "sale",
  "price": 100.00,
  "tags": ["quantum", "error-correction", "computing"]
}
```

**Listing Types**:
- `sale`: One-time purchase
- `license`: Time-limited license
- `citation_royalty`: Pay-per-citation

**Response**:
```json
{
  "listing_id": "sale-UTID-20241119-xxx",
  "utid": "UTID-20241119-a1b2c3d4-095",
  "status": "active",
  "created_at": "2024-11-19T10:00:00Z"
}
```

---

### GET /marketplace/insights/search

Search marketplace listings.

**Query Parameters**:
- `tags` (optional): Comma-separated tags
- `min_proof_score` (optional, default: `0.0`): Minimum proof score (0-1)
- `max_price` (optional): Maximum price in credits
- `listing_type` (optional): Filter by type

**Response**:
```json
{
  "total": 42,
  "listings": [
    {
      "listing_id": "sale-UTID-xxx",
      "utid": "UTID-20241119-a1b2c3d4-095",
      "title": "Novel Quantum Computing Error Correction",
      "price": 100.00,
      "proof_score": 0.95,
      "citation_count": 12,
      "seller_name": "Acme Research Labs"
    }
  ]
}
```

---

## Rate Limits

Rate limits vary by tier:

| Tier | Requests/minute | Requests/hour | Requests/day |
|------|-----------------|---------------|--------------|
| Tier 1 | 60 | 1,000 | 10,000 |
| Tier 2 | 120 | 5,000 | 50,000 |
| Tier 3 | 300 | 15,000 | 200,000 |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 115
X-RateLimit-Reset: 1637155200
```

**When Rate Limited**:
```json
{
  "error": "Rate limit exceeded",
  "status_code": 429,
  "retry_after": 45
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message describing what went wrong",
  "status_code": 400,
  "details": {
    "field": "theme_base",
    "issue": "Invalid value 'dark'. Must be one of: cosmic, chrome, light"
  }
}
```

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Partner account inactive or insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error (contact support)
- **503 Service Unavailable**: Temporary outage (check status.industriverse.ai)

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | API key is invalid or expired |
| `ACCOUNT_INACTIVE` | Partner account is not active |
| `TIER_MISMATCH` | Requested feature not available in your tier |
| `INVALID_THEME` | Theme configuration invalid |
| `WIDGET_NOT_FOUND` | Widget type doesn't exist |
| `DAC_NOT_FOUND` | DAC ID not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `VALIDATION_ERROR` | Request validation failed |
| `INSUFFICIENT_CREDITS` | Not enough credits (marketplace) |

### Retrying Failed Requests

For `5xx` errors and `429` rate limits:

```python
import time
import requests

def api_call_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            # Rate limited - wait and retry
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            continue

        if response.status_code >= 500:
            # Server error - exponential backoff
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## Webhooks

Configure webhook URL to receive events:

**Event Types**:
- `deployment.created`: New deployment activated
- `deployment.failed`: Deployment failed
- `widget.error`: Widget encountered error
- `billing.invoice.created`: New invoice generated
- `marketplace.sale`: Insight sold (Tier 3)

**Webhook Payload**:
```json
{
  "event": "deployment.created",
  "timestamp": "2024-11-19T10:00:00Z",
  "data": {
    "dac_id": "acme-corp:acme-security-platform",
    "deployment_id": "dep-xxx",
    "environment": "kubernetes",
    "status": "active"
  }
}
```

**Webhook Signature**:

Verify webhook authenticity using HMAC:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

## API Libraries

Official SDKs:

**Python**:
```bash
pip install industriverse-sdk
```

```python
from industriverse import Client

client = Client(api_key="your_api_key")
partner = client.partner.get_info()
print(partner.tier)
```

**JavaScript/Node.js**:
```bash
npm install @industriverse/sdk
```

```javascript
const { IndustriverseClient } = require('@industriverse/sdk');

const client = new IndustriverseClient({ apiKey: 'your_api_key' });
const partner = await client.partner.getInfo();
console.log(partner.tier);
```

**Go**:
```bash
go get github.com/industriverse/go-sdk
```

```go
import "github.com/industriverse/go-sdk/industriverse"

client := industriverse.NewClient("your_api_key")
partner, _ := client.Partner.GetInfo()
fmt.Println(partner.Tier)
```

---

## OpenAPI Specification

Full OpenAPI 3.0 spec available at:
```
https://api.industriverse.ai/v2/openapi.json
```

Generate client in any language:
```bash
openapi-generator generate \
  -i https://api.industriverse.ai/v2/openapi.json \
  -g python \
  -o ./industriverse-client
```

---

## Support

**API Questions**: api-support@industriverse.ai

**Bug Reports**: https://github.com/industriverse/api-issues

**Feature Requests**: https://feedback.industriverse.ai

**Status Page**: https://status.industriverse.ai
