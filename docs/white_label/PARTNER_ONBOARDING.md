# Partner Onboarding Guide

Welcome to the Industriverse White-Label Platform! This guide will help you get started with embedding Industriverse capabilities into your own products.

## Table of Contents

1. [Overview](#overview)
2. [Tier Selection](#tier-selection)
3. [Account Setup](#account-setup)
4. [Theme Customization](#theme-customization)
5. [Widget Integration](#widget-integration)
6. [DAC Deployment](#dac-deployment)
7. [Going Live](#going-live)

## Overview

The Industriverse White-Label Platform enables you to:

- **Rebrand**: Apply your logo, colors, and domain
- **Embed**: Integrate 8 powerful widgets into your products
- **Deploy**: Use DACs (Deploy Anywhere Capsules) for multi-environment deployment
- **Monetize**: Earn 30-40% revenue share on usage

### Platform Architecture

```
┌─────────────────────────────────────────────────┐
│            Your Product (Rebranded)             │
├─────────────────────────────────────────────────┤
│  Widgets (AI Shield, Compliance, Threat, etc.)  │
├─────────────────────────────────────────────────┤
│         DAC (Deploy Anywhere Capsule)           │
├─────────────────────────────────────────────────┤
│    I³ Intelligence Layer (RDR, Shadow Twin)     │
├─────────────────────────────────────────────────┤
│       Credit Protocol Economy (Optional)        │
└─────────────────────────────────────────────────┘
```

## Tier Selection

Choose the tier that matches your needs:

### Tier 1: Security Essentials ($5K-$15K/mo)
**Best for**: Companies needing core security monitoring

**Includes**:
- 4 security widgets:
  - AI Shield Dashboard
  - Compliance Score
  - Security Orb
  - Threat Heatmap (basic)
- Basic theme customization (colors, logo)
- Docker deployment
- Email support

**Resources**: 2 CPU cores, 4GB RAM, 50GB storage

**Use Cases**:
- SMB security monitoring
- Compliance dashboards
- Security SaaS products

---

### Tier 2: Domain Intelligence ($25K-$50K/mo)
**Best for**: Advanced analytics and predictive capabilities

**Includes**:
- All Tier 1 widgets +
- Energy Flow Graph
- Predictive Maintenance
- Advanced threat topology
- Full theme customization
- Kubernetes deployment
- Priority support
- Partner co-marketing

**Resources**: 4 CPU cores, 8GB RAM, 100GB storage

**Use Cases**:
- Industrial IoT platforms
- Predictive maintenance SaaS
- Energy management systems

---

### Tier 3: Full Discovery Platform ($100K-$500K/mo)
**Best for**: Research platforms and advanced discovery

**Includes**:
- All Tier 1 & 2 widgets +
- Shadow Twin 3D
- Research Explorer
- I³ Intelligence Layer:
  - RDR Engine (6D embeddings)
  - MSEP.one simulation
  - OBMI operators
- Credit Protocol Economy
- White-glove support
- Dedicated account manager
- Custom feature development

**Resources**: 8 CPU cores, 16GB RAM, 200GB storage, GPU (8GB VRAM)

**Use Cases**:
- Research platforms
- Knowledge discovery tools
- Scientific collaboration platforms

## Account Setup

### 1. Request Partner Account

Contact: partners@industriverse.ai

Provide:
- Company name
- Primary contact information
- Desired tier
- Target go-live date

### 2. Receive API Credentials

You'll receive:
```json
{
  "partner_id": "acme-corp",
  "api_key": "iv_xxxxxxxxxxxxxx",
  "api_secret": "secret_xxxxxxxxxxxxxx",
  "api_endpoint": "https://api.industriverse.ai/v2"
}
```

**Store these securely!** Never commit to version control.

### 3. Verify Access

Test your credentials:

```bash
curl -H "X-API-Key: your_api_key" \
  https://api.industriverse.ai/v2/partner/info
```

Expected response:
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
  }
}
```

## Theme Customization

### Design Token System

Industriverse uses a design token system that preserves the thermodynamic aesthetic while allowing customization.

### Allowed Customizations

You can customize:
- Primary color
- Accent color
- Logo URL
- Brand name
- Custom domain

You **cannot** customize:
- Core thermodynamic effects (glow, plasma gradients)
- Motion animations
- Shadow styles

This ensures brand consistency while preventing visual dilution.

### Apply Theme via API

```python
import requests

api_key = "your_api_key"
endpoint = "https://api.industriverse.ai/v2"

theme_config = {
    "theme_base": "cosmic",  # or "chrome", "light"
    "custom_colors": {
        "primary": "#1E40AF",      # Your brand blue
        "accent": "#F59E0B"         # Your brand orange
    },
    "logo_url": "https://acme.com/logo.svg",
    "brand_name": "Acme Security Platform",
    "custom_domain": "security.acme.com"
}

response = requests.post(
    f"{endpoint}/theme/customize",
    headers={"X-API-Key": api_key},
    json=theme_config
)

print(response.json())
```

### Preview Theme

Use the theme preview tool:

```bash
# Install CLI
npm install -g @industriverse/theme-preview

# Preview your theme
iv-theme preview --config theme.json
```

Opens browser at `http://localhost:3000` with your customized theme.

## Widget Integration

### Available Widgets (by tier)

| Widget | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| AI Shield Dashboard | ✓ | ✓ | ✓ |
| Compliance Score | ✓ | ✓ | ✓ |
| Security Orb | ✓ | ✓ | ✓ |
| Threat Heatmap | ✓ | ✓ | ✓ |
| Energy Flow Graph | | ✓ | ✓ |
| Predictive Maintenance | | ✓ | ✓ |
| Shadow Twin 3D | | | ✓ |
| Research Explorer | | | ✓ |

### Integration Methods

#### 1. iframe Embed (Easiest)

```html
<iframe
  src="https://widgets.industriverse.ai/ai-shield-dashboard?partner=acme-corp&token=xxx"
  width="100%"
  height="600px"
  frameborder="0"
></iframe>
```

**Pros**: Zero setup, automatic updates
**Cons**: Limited customization, separate DOM

---

#### 2. JavaScript SDK (Recommended)

```html
<!-- Load SDK -->
<script src="https://cdn.industriverse.ai/widget-sdk/v2.js"></script>

<!-- Mount widget -->
<div id="ai-shield-widget"></div>

<script>
  IndustriverseWidgets.init({
    partnerId: 'acme-corp',
    apiKey: 'your_api_key'
  });

  IndustriverseWidgets.mount('ai-shield-dashboard', {
    container: '#ai-shield-widget',
    theme: 'cosmic',
    refreshInterval: 5000,
    onThreatDetected: (threat) => {
      console.log('Threat detected:', threat);
      // Your custom handling
    }
  });
</script>
```

**Pros**: More control, event callbacks, custom styling
**Cons**: Requires JavaScript

---

#### 3. React Component (For React Apps)

```bash
npm install @industriverse/react-widgets
```

```jsx
import { AIShieldDashboard } from '@industriverse/react-widgets';

function SecurityPage() {
  return (
    <AIShieldDashboard
      partnerId="acme-corp"
      apiKey={process.env.INDUSTRIVERSE_API_KEY}
      theme="cosmic"
      onThreatDetected={(threat) => {
        // Handle threat
      }}
    />
  );
}
```

**Pros**: Native React integration, TypeScript support
**Cons**: React only

---

#### 4. Web Components (Framework Agnostic)

```html
<script type="module">
  import '@industriverse/web-components';
</script>

<iv-widget-ai-shield
  partner-id="acme-corp"
  api-key="your_api_key"
  theme="cosmic">
</iv-widget-ai-shield>
```

**Pros**: Works with any framework (Vue, Angular, Svelte)
**Cons**: Modern browsers only

### Widget Configuration

Each widget accepts these common options:

```javascript
{
  // Identity
  partnerId: 'acme-corp',
  apiKey: 'your_api_key',

  // Theme
  theme: 'cosmic',          // 'cosmic', 'chrome', 'light'
  customColors: {
    primary: '#1E40AF'
  },

  // Behavior
  refreshInterval: 5000,     // ms between updates
  enableAnimations: true,
  enableWebSocket: true,     // Real-time updates

  // Callbacks
  onMount: () => {},
  onDataUpdate: (data) => {},
  onError: (error) => {},

  // Custom features (widget-specific)
  customFeatures: {
    showDetails: true,
    enableDrillDown: true
  }
}
```

## DAC Deployment

### What is a DAC?

A **Deploy Anywhere Capsule (DAC)** is a complete deployment package containing:
- All widget frontends
- Backend services
- Database schemas
- Configuration
- Resource specifications

### Create DAC Configuration

```python
import requests

dac_config = {
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
            "custom_features": {
                "frameworks": ["NIST", "ISO27001", "GDPR"]
            }
        }
    ],

    "allowed_origins": [
        "https://security.acme.com",
        "https://app.acme.com"
    ]
}

response = requests.post(
    "https://api.industriverse.ai/v2/dac/configure",
    headers={"X-API-Key": "your_api_key"},
    json=dac_config
)

dac_id = response.json()['dac_id']
print(f"DAC created: {dac_id}")
```

### Download DAC Package

```bash
curl -H "X-API-Key: your_api_key" \
  "https://api.industriverse.ai/v2/dac/{dac_id}/download" \
  -o industriverse-dac.tar.gz

tar -xzf industriverse-dac.tar.gz
cd industriverse-dac/
```

### Deploy to Kubernetes

```bash
# Review generated manifests
ls -la kubernetes/

# Apply to cluster
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Check status
kubectl get pods -n acme-security
kubectl get ingress -n acme-security
```

### Deploy with Docker Compose

```bash
# Review docker-compose.yml
cat docker-compose.yml

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access at http://localhost:8080
```

### Deploy to Cloud

#### AWS ECS
```bash
./deploy/aws/deploy-ecs.sh --region us-east-1 --cluster acme-production
```

#### Google Cloud Run
```bash
./deploy/gcp/deploy-cloud-run.sh --project acme-prod --region us-central1
```

#### Azure Container Apps
```bash
./deploy/azure/deploy-container-apps.sh --resource-group acme-rg --location eastus
```

## Going Live

### Pre-Launch Checklist

- [ ] Theme customization complete
- [ ] All widgets tested
- [ ] DAC deployed to staging environment
- [ ] SSL certificates configured
- [ ] Custom domain DNS configured
- [ ] API rate limits reviewed
- [ ] Billing information verified
- [ ] Team trained on platform

### Domain Configuration

Point your custom domain to Industriverse:

```
CNAME security.acme.com → acme-corp.industriverse.ai
```

Or for dedicated deployment:
```
A security.acme.com → your-load-balancer-ip
```

### SSL/TLS Setup

Industriverse provides automatic SSL via Let's Encrypt for hosted deployments.

For self-hosted, configure your own certificates:

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - security.acme.com
    secretName: acme-security-tls
```

### Monitoring

Access your dashboard:

```
https://partner-portal.industriverse.ai/dashboard
```

Monitor:
- Widget impressions
- API call volume
- Error rates
- Revenue tracking
- User engagement

### Support

- **Email**: support@industriverse.ai
- **Slack**: Dedicated partner channel
- **Documentation**: https://docs.industriverse.ai
- **Status**: https://status.industriverse.ai

### Emergency Contact

For production outages:
- **Phone**: +1-555-INDSTRVRS
- **Emergency Email**: emergency@industriverse.ai
- **Response Time**: < 1 hour (Tier 3), < 4 hours (Tier 2), < 24 hours (Tier 1)

## Next Steps

1. **Explore API**: See [API Documentation](./API_REFERENCE.md)
2. **Widget Tutorials**: See [Widget Integration Guide](./WIDGET_INTEGRATION.md)
3. **Examples**: Browse [Example Implementations](./examples/)
4. **Community**: Join our partner Slack channel

## Revenue Tracking

View your earnings in the partner portal:

```
Revenue Share: 30-40% of generated revenue
Payment Terms: Net 30
Payment Methods: Wire transfer, ACH
Minimum Payout: $1,000
```

Revenue sources:
- Partner subscription fees (your customers)
- API overage charges
- Marketplace transactions (if enabled)
- Premium feature upgrades

## Frequently Asked Questions

**Q: Can I white-label the entire platform?**
A: Yes! Tier 3 partners can fully rebrand including domain, logo, colors, and even remove Industriverse branding.

**Q: What happens if I exceed my API limits?**
A: Overage charges apply: $0.001 per API call after your tier limit. You'll receive alerts at 80% and 95% usage.

**Q: Can I migrate between tiers?**
A: Yes, upgrades are instant. Downgrades take effect at next billing cycle.

**Q: Do you offer custom development?**
A: Tier 3 partners receive custom feature development. Contact your account manager.

**Q: What's the SLA?**
A: 99.9% uptime for hosted deployments (Tier 2+), 99.95% for Tier 3 dedicated instances.

---

**Ready to get started?** Contact partners@industriverse.ai or visit https://industriverse.ai/partners
