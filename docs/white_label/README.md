# Industriverse White-Label Platform Documentation

Complete documentation for embedding Industriverse capabilities into your own products.

## 📚 Documentation Index

### Getting Started
- **[Partner Onboarding Guide](./PARTNER_ONBOARDING.md)** - Complete guide to getting started as a partner
- **[Quick Start: React](./examples/quickstart-react.md)** - React integration example (15 minutes)

### API Reference
- **[API Reference](./API_REFERENCE.md)** - Complete REST API documentation
- **[OpenAPI Spec](https://api.industriverse.ai/v2/openapi.json)** - Machine-readable API specification

### Implementation Guides
- **[Widget Integration](./WIDGET_INTEGRATION.md)** - Detailed widget integration guide
- **[Theme Customization](./THEME_CUSTOMIZATION.md)** - Design token system and branding
- **[DAC Deployment](./DAC_DEPLOYMENT.md)** - Deploy Anywhere Capsule deployment

### Advanced Topics
- **[I³ Intelligence Layer](./I3_INTEGRATION.md)** - Research and knowledge discovery (Tier 3)
- **[Credit Protocol Economy](./CREDIT_PROTOCOL.md)** - Marketplace and tokenomics (Tier 3)
- **[Analytics & Monitoring](./ANALYTICS.md)** - Usage tracking and revenue monitoring

## 🚀 Quick Start

### 1. Get Partner Credentials

Contact: **partners@industriverse.ai**

Receive:
```json
{
  "partner_id": "your-company",
  "api_key": "iv_xxxxxxxxxxxxxx",
  "tier": "domain-intelligence"
}
```

### 2. Choose Integration Method

| Method | Best For | Time to Integrate |
|--------|----------|-------------------|
| iframe embed | Quick proof of concept | 5 minutes |
| JavaScript SDK | Web applications | 30 minutes |
| React components | React applications | 15 minutes |
| DAC deployment | Full platform | 1-2 hours |

### 3. Basic Widget Embed

```html
<!-- Easiest: iframe -->
<iframe
  src="https://widgets.industriverse.ai/ai-shield-dashboard?partner=your-company&token=xxx"
  width="100%"
  height="600px"
></iframe>

<!-- Better: JavaScript SDK -->
<script src="https://cdn.industriverse.ai/widget-sdk/v2.js"></script>
<div id="widget"></div>
<script>
  IndustriverseWidgets.init({
    partnerId: 'your-company',
    apiKey: 'your_api_key'
  });

  IndustriverseWidgets.mount('ai-shield-dashboard', {
    container: '#widget',
    theme: 'cosmic'
  });
</script>

<!-- Best: React -->
<AIShieldDashboard
  partnerId="your-company"
  apiKey="your_api_key"
  theme="cosmic"
/>
```

## 🎨 Three Tiers, Tailored Value

### Tier 1: Security Essentials
**$5K-$15K/mo** | **4 widgets** | **Docker deployment**

Perfect for SMB security monitoring and compliance dashboards.

**Includes**: AI Shield, Compliance Score, Security Orb, Threat Heatmap

[View Tier 1 Details →](./tiers/TIER1_SECURITY_ESSENTIALS.md)

---

### Tier 2: Domain Intelligence
**$25K-$50K/mo** | **6 widgets** | **Kubernetes deployment**

Advanced analytics, predictive capabilities, full theme customization.

**Includes**: All Tier 1 + Energy Flow, Predictive Maintenance

[View Tier 2 Details →](./tiers/TIER2_DOMAIN_INTELLIGENCE.md)

---

### Tier 3: Full Discovery Platform
**$100K-$500K/mo** | **8 widgets** | **I³ Intelligence Layer**

Complete research platform with RDR engine, Shadow Twin 3D, marketplace.

**Includes**: All Tier 1 & 2 + Shadow Twin 3D, Research Explorer, MSEP.one, OBMI Operators

[View Tier 3 Details →](./tiers/TIER3_FULL_DISCOVERY.md)

## 📦 Available Widgets

| Widget | Description | Tier Required |
|--------|-------------|---------------|
| **AI Shield Dashboard** | Real-time threat monitoring with thermodynamic security | Tier 1+ |
| **Compliance Score** | NIST, ISO27001, GDPR, SOC 2 tracking | Tier 1+ |
| **Security Orb** | Ambient threat level indicator | Tier 1+ |
| **Threat Heatmap** | Thermodynamic topology visualization | Tier 1+ |
| **Energy Flow Graph** | Operational thermodynamics and efficiency | Tier 2+ |
| **Predictive Maintenance** | AI-powered failure forecasting | Tier 2+ |
| **Shadow Twin 3D** | Interactive 3D system visualization | Tier 3 |
| **Research Explorer** | I³ knowledge graph and research browser | Tier 3 |

[View Widget Catalog →](./WIDGET_CATALOG.md)

## 🏗️ Platform Architecture

```
┌─────────────────────────────────────────────────────┐
│             Partner Application (You)               │
│                 Fully Rebranded                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │        Embeddable Widgets (8 total)         │  │
│  │  AI Shield | Compliance | Threat | Energy   │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │   DAC (Deploy Anywhere Capsule)             │  │
│  │   Kubernetes | Docker | AWS | GCP | Azure   │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │   I³ Intelligence Layer (Tier 3)            │  │
│  │   RDR Engine | Shadow Twin | MSEP.one       │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │   Credit Protocol Economy (Tier 3)          │  │
│  │   Marketplace | Tokens | Revenue Share      │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 💰 Revenue Model

### Partner Revenue Share: 30-40%

**You earn from**:
- Customer subscription fees
- API usage overage
- Marketplace transactions (Tier 3)
- Premium feature upgrades

**Example** (Tier 2 partner with 50 customers):
```
Your monthly revenue:
  Customer subscriptions: $75,000
  API overages: $5,000
  Total gross: $80,000

Your 35% share: $28,000/month
Annual recurring: $336,000
```

**Payment Terms**: Net 30, wire transfer or ACH

[View Pricing Calculator →](./PRICING_CALCULATOR.md)

## 🔑 Key Features

### Design Token System
Customize colors, logo, domain while preserving thermodynamic aesthetic.

```json
{
  "theme_base": "cosmic",
  "custom_colors": {
    "primary": "#1E40AF",
    "accent": "#F59E0B"
  },
  "logo_url": "https://your-company.com/logo.svg",
  "custom_domain": "security.your-company.com"
}
```

### Deploy Anywhere Capsules (DACs)
Single manifest, multiple deployment targets.

```yaml
name: your-security-platform
tier: domain-intelligence
target_environments:
  - kubernetes
  - docker
  - aws
```

Generates:
- Kubernetes manifests (YAML)
- Docker Compose files
- AWS ECS task definitions
- GCP Cloud Run configs
- Azure Container Apps specs

### Real-Time Updates
WebSocket connections for live threat monitoring.

```javascript
widget.on('threatDetected', (threat) => {
  // Real-time threat alert
  sendNotification(threat);
});
```

### I³ Intelligence Layer (Tier 3)
Complete research platform:

- **RDR Engine**: 6D thermodynamic embeddings for papers
- **Shadow Twin**: 3D force-directed knowledge graph
- **MSEP.one**: Nano-simulation validation
- **OBMI Operators**: Thermodynamic knowledge operations

### Credit Protocol Economy (Tier 3)
Monetize validated research insights:

- **Proof-of-Insight Ledger**: Blockchain-inspired immutable record
- **UTID Marketplace**: Trade validated insights
- **Token Economics**: Dynamic pricing, staking, rewards
- **Revenue Distribution**: 65% creator, 12% validators, 10% platform

## 📖 Example Implementations

### React Application
```bash
# Install
npm install @industriverse/react-widgets

# Use
import { AIShieldDashboard } from '@industriverse/react-widgets';

<AIShieldDashboard partnerId="your-company" />
```

[Full React Example →](./examples/quickstart-react.md)

### Vue Application
```bash
npm install @industriverse/vue-widgets
```

[Full Vue Example →](./examples/quickstart-vue.md)

### Angular Application
```bash
npm install @industriverse/angular-widgets
```

[Full Angular Example →](./examples/quickstart-angular.md)

### Vanilla JavaScript
```html
<script src="https://cdn.industriverse.ai/widget-sdk/v2.js"></script>
```

[Full Vanilla JS Example →](./examples/quickstart-vanilla.md)

## 🛠️ Development Tools

### CLI Tool
```bash
npm install -g @industriverse/cli

# Preview theme
iv-theme preview --config theme.json

# Validate DAC manifest
iv-dac validate manifest.yaml

# Deploy DAC
iv-dac deploy --environment production
```

### Browser DevTools Extension
Chrome/Firefox extension for debugging widgets.

```bash
# Install from Chrome Web Store
https://chrome.google.com/webstore/.../industriverse-devtools
```

**Features**:
- Widget performance profiling
- WebSocket message inspector
- Theme customization preview
- API call logging

## 📊 Analytics & Monitoring

### Partner Portal Dashboard

View real-time metrics:
- Widget impressions
- API call volume
- Active deployments
- Revenue tracking
- Error rates
- User engagement

**Access**: https://partner-portal.industriverse.ai

### Programmatic Analytics

```python
from industriverse import Client

client = Client(api_key="your_api_key")

analytics = client.analytics.get(
    start_date="2024-11-01",
    end_date="2024-11-30",
    granularity="day"
)

print(f"Total API calls: {analytics.total_api_calls}")
print(f"Widget impressions: {analytics.total_impressions}")
print(f"Revenue: ${analytics.total_revenue}")
```

[View Analytics Guide →](./ANALYTICS.md)

## 🔐 Security & Compliance

### Security Features
- **API key rotation**: Automatic every 90 days
- **IP whitelisting**: Restrict API access by IP
- **CORS configuration**: Control allowed origins
- **Webhook signatures**: HMAC validation
- **TLS 1.3**: All traffic encrypted
- **SOC 2 Type II**: Certified secure operations

### Compliance Support
Built-in compliance frameworks:
- NIST Cybersecurity Framework
- ISO 27001
- GDPR
- SOC 2
- HIPAA (Tier 3 with BAA)

[View Security Documentation →](./SECURITY.md)

## 🚨 Support & SLA

### Support Tiers

| Tier | Response Time | Channels | Availability |
|------|---------------|----------|--------------|
| Tier 1 | < 24 hours | Email | 9am-5pm ET |
| Tier 2 | < 4 hours | Email, Slack | 24/5 |
| Tier 3 | < 1 hour | Email, Slack, Phone | 24/7 |

### Support Channels
- **Email**: support@industriverse.ai
- **Slack**: Dedicated partner channel
- **Phone**: +1-555-INDSTRVRS (Tier 3 only)
- **Emergency**: emergency@industriverse.ai

### SLA
- **Uptime**: 99.9% (hosted), 99.95% (Tier 3 dedicated)
- **API Latency**: < 200ms p95
- **Widget Load Time**: < 1s

[View Status Page →](https://status.industriverse.ai)

## 🌐 Community & Resources

### Developer Community
- **Discord**: https://discord.gg/industriverse
- **GitHub**: https://github.com/industriverse
- **Stack Overflow**: Tag `industriverse`
- **Twitter**: @industriverse

### Learning Resources
- **Video Tutorials**: https://youtube.com/industriverse
- **Webinars**: Monthly partner webinars
- **Blog**: https://blog.industriverse.ai
- **Changelog**: https://changelog.industriverse.ai

### Example Projects
- **React Dashboard**: https://github.com/industriverse/examples/react
- **Vue Security App**: https://github.com/industriverse/examples/vue
- **Angular Platform**: https://github.com/industriverse/examples/angular
- **Full Stack**: https://github.com/industriverse/examples/fullstack

## 📝 Legal & Compliance

### Agreements
- **Partner Agreement**: Signed during onboarding
- **SLA**: Service Level Agreement
- **DPA**: Data Processing Agreement
- **BAA**: Business Associate Agreement (HIPAA, Tier 3)

### Data Privacy
- **GDPR compliant**: EU data residency available
- **CCPA compliant**: California privacy rights supported
- **Data retention**: Customer data retained 90 days post-termination
- **Data export**: Full data export available via API

[View Privacy Policy →](./PRIVACY.md)

## 🎯 Next Steps

1. **[Request Partner Account](https://industriverse.ai/partners/apply)** - Get API credentials
2. **[Try Quick Start](./examples/quickstart-react.md)** - 15-minute React integration
3. **[Explore API](./API_REFERENCE.md)** - Complete API documentation
4. **[Join Community](https://discord.gg/industriverse)** - Connect with other partners
5. **[Schedule Demo](https://industriverse.ai/partners/demo)** - Live walkthrough with team

## 📧 Contact

**General Inquiries**: partners@industriverse.ai

**Sales**: sales@industriverse.ai

**Support**: support@industriverse.ai

**Emergency**: emergency@industriverse.ai

**Phone**: +1-555-INDSTRVRS (Tier 3 only)

---

**Last Updated**: November 19, 2024

**Documentation Version**: 2.0.0

**Platform Version**: 2.0.0
