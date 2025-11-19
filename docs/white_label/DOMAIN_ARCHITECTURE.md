# Domain Architecture & Infrastructure

**Version**: 2.0.0
**Last Updated**: November 19, 2024

## Overview

Complete specification for domain structure, DNS configuration, CDN setup, and deployment architecture for the Industriverse white-label platform.

---

## Domain Structure

### Primary Domain: industriverse.ai

**DNS Provider**: Cloudflare
**SSL/TLS**: Full (strict) with auto-renewal
**DNSSEC**: Enabled

#### Main Site (industriverse.ai)

**Purpose**: Marketing, platform overview, partner acquisition

**Deployment**:
- **Platform**: Vercel (Next.js)
- **Edge Network**: Cloudflare + Vercel Edge
- **Region**: Global (multi-region)
- **Build**: Automated via GitHub Actions

**DNS Records**:
```
Type    Name    Content                 TTL     Proxy
A       @       76.76.21.21            Auto    Proxied
AAAA    @       2606:4700::6810:1515   Auto    Proxied
```

**Performance**:
- Edge caching for static assets
- Image optimization via Vercel Image API
- Gzip/Brotli compression
- HTTP/3 enabled

**Analytics**:
- Vercel Analytics
- Google Analytics 4
- Plausible (privacy-friendly)

---

### Subdomain: widgets.industriverse.ai

**Purpose**: Widget embed service, preview, SDK delivery

**Deployment**:
- **Platform**: Vercel Edge Functions
- **CDN**: Cloudflare + Vercel
- **Caching**: Aggressive caching for SDK, moderate for widget data

**DNS Records**:
```
Type    Name       Content                   TTL     Proxy
CNAME   widgets    cname.vercel-dns.com     Auto    Proxied
```

**Endpoints**:
```
/embed/{widget-type}        # iframe embeds
/sdk/v2/widget-sdk.js       # JavaScript SDK
/sdk/v2/widget-sdk.min.js   # Minified SDK
/sdk/v2/react-widgets.js    # React components
/preview/{widget-type}      # Interactive previews
/api/widget-data            # Real-time widget data
```

**CORS Configuration**:
```javascript
// Allowed origins based on partner configuration
Access-Control-Allow-Origin: {partner_domain}
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-API-Key
Access-Control-Max-Age: 86400
```

**Rate Limiting**:
- Public embeds: 1000 req/min per IP
- Authenticated API: Based on partner tier
- SDK downloads: Unlimited (cached)

---

### Subdomain: partners.industriverse.ai

**Purpose**: Partner portal, dashboard, configuration

**Deployment**:
- **Platform**: Vercel (Next.js with API routes)
- **Database**: Supabase (PostgreSQL)
- **Auth**: NextAuth.js + Supabase Auth
- **File Storage**: S3 (theme assets, exports)

**DNS Records**:
```
Type    Name       Content                   TTL     Proxy
CNAME   partners   cname.vercel-dns.com     Auto    Proxied
```

**Security**:
- **WAF**: Cloudflare Web Application Firewall
- **DDoS Protection**: Cloudflare
- **Rate Limiting**: Strict (per partner)
- **2FA**: Required for all partners
- **Session**: Secure, httpOnly cookies

**API Routes**:
```
/api/auth/*                 # Authentication
/api/partner/info           # Partner details
/api/partner/dashboard      # Dashboard data
/api/dac/*                  # DAC management
/api/theme/*                # Theme configuration
/api/analytics/*            # Analytics data
/api/billing/*              # Billing info
```

**Real-Time Features**:
- WebSocket server: `wss://partners.industriverse.ai/ws`
- Live metrics updates
- Notification system
- Real-time DAC status

---

### Subdomain: marketplace.industriverse.ai

**Purpose**: UTID marketplace, insight trading (Tier 3 only)

**Deployment**:
- **Platform**: Vercel (Next.js)
- **Database**: Supabase + Weaviate (vector search)
- **Payment**: Stripe Connect
- **Search**: Algolia + custom vector search

**DNS Records**:
```
Type    Name          Content                   TTL     Proxy
CNAME   marketplace   cname.vercel-dns.com     Auto    Proxied
```

**Features**:
- Server-side rendering for SEO
- Incremental static regeneration (ISR) for listings
- Real-time availability updates via WebSocket
- Advanced search with vector similarity

**Search Infrastructure**:
```
Primary: Algolia
  - Instant search
  - Faceted filtering
  - Typo tolerance

Secondary: Weaviate
  - Semantic search
  - 6D embedding similarity
  - Recommendation engine
```

**Payment Flow**:
```
1. User initiates purchase
2. Stripe payment intent created
3. Payment processed
4. Revenue distribution triggered
5. UTID transferred
6. Confirmation sent
```

---

### Subdomain: docs.industriverse.ai

**Purpose**: Documentation, API reference, guides

**Deployment**:
- **Platform**: Vercel (Next.js + MDX)
- **Search**: Algolia DocSearch
- **Version Control**: Git-based
- **CMS**: Contentlayer (MDX → JSON)

**DNS Records**:
```
Type    Name    Content                   TTL     Proxy
CNAME   docs    cname.vercel-dns.com     Auto    Proxied
```

**Structure**:
```
/                           # Docs home
/getting-started            # Quick start
/api                        # API reference
  /partner                  # Partner API
  /widgets                  # Widget API
  /marketplace              # Marketplace API
/guides                     # Integration guides
  /react                    # React integration
  /vue                      # Vue integration
  /angular                  # Angular integration
/widgets                    # Widget docs
  /ai-shield                # AI Shield docs
  /compliance               # Compliance docs
/examples                   # Code examples
/changelog                  # Platform updates
```

**Features**:
- Versioned documentation
- Interactive code examples
- API playground
- Dark mode
- Mobile-optimized

---

### Subdomain: cdn.industriverse.ai

**Purpose**: Static asset delivery, theme bundles, SDK files

**Deployment**:
- **Platform**: Cloudflare R2 + Workers
- **CDN**: Cloudflare (global)
- **Cache**: Aggressive (1 year for versioned assets)
- **Compression**: Brotli + Gzip

**DNS Records**:
```
Type    Name    Content                   TTL     Proxy
CNAME   cdn     cdn.industriverse.ai     Auto    Proxied
```

**Directory Structure**:
```
/widget-sdk/
  /v2/
    widget-sdk.js           # Latest SDK
    widget-sdk.min.js       # Minified
    widget-sdk.js.map       # Source map
  /v1/                      # Legacy support

/themes/
  /cosmic/
    theme.css
    assets/
  /chrome/
    theme.css
    assets/

/assets/
  /images/
  /fonts/
  /icons/
```

**Caching Strategy**:
```javascript
// Versioned assets (SDK, themes)
Cache-Control: public, max-age=31536000, immutable

// Unversioned assets (logos, images)
Cache-Control: public, max-age=604800
```

**Security Headers**:
```
Content-Security-Policy: default-src 'self' *.industriverse.ai
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
```

---

### Subdomain: api.industriverse.ai

**Purpose**: REST API, WebSocket server, webhooks

**Deployment**:
- **Platform**: AWS ECS (Dockerized FastAPI)
- **Load Balancer**: AWS ALB
- **Database**: AWS RDS (PostgreSQL)
- **Cache**: Redis (AWS ElastiCache)
- **Queue**: AWS SQS

**DNS Records**:
```
Type    Name    Content                          TTL
CNAME   api     api-lb-xxx.us-east-1.elb.aws     300
```

**API Versioning**:
```
/v2/partner/*               # Partner API
/v2/widgets/*               # Widget API
/v2/dac/*                   # DAC API
/v2/marketplace/*           # Marketplace API (Tier 3)
/v2/analytics/*             # Analytics API
```

**WebSocket**:
```
wss://api.industriverse.ai/ws
  /partner/{partner_id}     # Partner updates
  /widget/{widget_id}       # Widget data stream
  /marketplace              # Marketplace events
```

**Rate Limiting** (per tier):
```
Tier 1: 60/min, 1K/hour, 10K/day
Tier 2: 120/min, 5K/hour, 50K/day
Tier 3: 300/min, 15K/hour, 200K/day
```

---

## Secondary Domain: thermodynasty.com

### Main Site (thermodynasty.com)

**Purpose**: I³ Intelligence Platform, research portal

**Deployment**:
- **Platform**: Vercel (Next.js)
- **Database**: Supabase + Neo4j (knowledge graph)
- **Compute**: AWS Lambda (paper processing)

**DNS Records**:
```
Type    Name    Content                   TTL     Proxy
A       @       76.76.21.22              Auto    Proxied
AAAA    @       2606:4700::6810:1516     Auto    Proxied
```

**Features**:
- Research paper browser
- 6D embedding visualizer
- Shadow Twin 3D interface
- MSEP.one simulation portal

---

### Subdomain: labs.thermodynasty.com

**Purpose**: Experimental features, OBMI playground

**Deployment**:
- **Platform**: Vercel (Next.js)
- **Compute**: AWS Lambda + GPU instances (G4dn)
- **Storage**: S3 (experiment results)

**DNS Records**:
```
Type    Name    Content                   TTL     Proxy
CNAME   labs    cname.vercel-dns.com     Auto    Proxied
```

**Experimental Features**:
- RDR engine interface
- OBMI operator playground
- 6D embedding explorer
- Custom simulation builder

---

## SSL/TLS Configuration

### Certificate Management

**Provider**: Let's Encrypt via Cloudflare
**Type**: Universal SSL (wildcard + specific subdomains)
**Renewal**: Automatic (90-day certificates)

**Certificates Needed**:
```
*.industriverse.ai          # Wildcard for all subdomains
industriverse.ai            # Root domain
thermodynasty.com           # Root domain
*.thermodynasty.com         # Wildcard
```

### TLS Settings

```
Minimum TLS Version: 1.2
Cipher Suites: Modern (prefer ChaCha20-Poly1305, AES-GCM)
HSTS: Enabled (max-age=31536000; includeSubDomains; preload)
Certificate Transparency: Enabled
OCSP Stapling: Enabled
```

---

## CDN Configuration

### Cloudflare Settings

**Caching**:
```
Cache Level: Standard
Browser Cache TTL: Respect Existing Headers
Always Online: Enabled
Crawler Hints: Enabled
```

**Optimization**:
```
Auto Minify: JS, CSS, HTML
Brotli: Enabled
Early Hints: Enabled
HTTP/3 (QUIC): Enabled
0-RTT Connection Resumption: Enabled
```

**Security**:
```
WAF: Enabled (OWASP ruleset)
DDoS Protection: Automatic
Bot Fight Mode: Enabled
Email Obfuscation: Enabled
Hotlink Protection: Enabled
```

**Page Rules**:
```
1. cdn.industriverse.ai/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 year
   - Browser Cache TTL: 1 year

2. api.industriverse.ai/*
   - Cache Level: Bypass
   - Security Level: High

3. *.industriverse.ai/api/*
   - Cache Level: Bypass
   - Rate Limit: Custom rules
```

---

## Monitoring & Observability

### Uptime Monitoring

**Provider**: UptimeRobot + Pingdom
**Endpoints**:
```
https://industriverse.ai
https://partners.industriverse.ai
https://marketplace.industriverse.ai
https://docs.industriverse.ai
https://api.industriverse.ai/health
https://thermodynasty.com
```

**Check Frequency**: 1 minute
**Alert Channels**:
- Slack (#infrastructure-alerts)
- PagerDuty (critical only)
- Email (team@industriverse.ai)

### Performance Monitoring

**Real User Monitoring (RUM)**:
- Vercel Analytics (all Vercel deployments)
- Google Analytics 4 (Core Web Vitals)

**Synthetic Monitoring**:
- Lighthouse CI (automated performance tests)
- WebPageTest (monthly deep dives)

**Metrics Tracked**:
```
- FCP (First Contentful Paint)
- LCP (Largest Contentful Paint)
- FID (First Input Delay)
- CLS (Cumulative Layout Shift)
- TTFB (Time to First Byte)
- Load Time
- Bundle Size
```

### Logging & Tracing

**Log Aggregation**:
- Vercel: Native logging
- AWS: CloudWatch Logs
- Application: Structured JSON logs

**Log Retention**:
```
Info/Debug: 7 days
Warning: 30 days
Error: 90 days
Critical: 1 year
```

**Distributed Tracing**:
- OpenTelemetry
- Jaeger (self-hosted)
- Trace sampling: 10% of requests

---

## Disaster Recovery

### Backup Strategy

**Database Backups**:
```
Frequency: Daily (automated)
Retention: 30 days
Storage: AWS S3 (cross-region)
Encryption: AES-256
Test Restoration: Monthly
```

**Configuration Backups**:
```
DNS: Daily export via Cloudflare API
Vercel: Git-based (no backup needed)
AWS: Terraform state in S3 + versioning
```

### Failover Plan

**DNS Failover**:
- Cloudflare Load Balancing
- Health checks every 60s
- Automatic failover to backup region
- TTL: 300s (5 minutes)

**Database Failover**:
- Multi-AZ deployment (AWS RDS)
- Read replicas in 3 regions
- Automatic failover < 2 minutes
- Point-in-time recovery enabled

**Service Recovery Targets**:
```
RTO (Recovery Time Objective): 4 hours
RPO (Recovery Point Objective): 1 hour
SLA Uptime: 99.9% (Tier 1-2), 99.95% (Tier 3)
```

---

## Cost Optimization

### Infrastructure Costs (Monthly Estimates)

**Vercel**:
```
Pro Plan: $20/month
Bandwidth: ~$50/month (1TB)
Edge Functions: ~$30/month
Total: ~$100/month
```

**AWS**:
```
ECS (API): $150/month (2 tasks, always on)
RDS: $200/month (db.t3.large, Multi-AZ)
ElastiCache: $50/month (cache.t3.small)
S3: $30/month (storage + bandwidth)
CloudWatch: $20/month
Total: ~$450/month
```

**Cloudflare**:
```
Pro Plan: $20/month/domain × 2 = $40/month
R2 Storage: $15/month (100GB)
Total: ~$55/month
```

**Third-Party Services**:
```
Supabase: $25/month (Pro plan)
Algolia: $99/month (Search tier)
Stripe: % of transactions (no fixed cost)
Total: ~$124/month
```

**Grand Total**: ~$729/month (baseline, scales with usage)

### Optimization Strategies

1. **Edge Caching**: Reduce origin requests by 80%
2. **Image Optimization**: WebP/AVIF, lazy loading
3. **Code Splitting**: Reduce bundle size 40%
4. **Serverless**: Pay-per-execution vs always-on
5. **Reserved Instances**: 30% savings on predictable workloads

---

## Security Hardening

### DDoS Protection

**Layer 3/4** (Network/Transport):
- Cloudflare automatic mitigation
- AWS Shield Standard
- Rate limiting at edge

**Layer 7** (Application):
- Cloudflare WAF
- Custom rate limits per endpoint
- Challenge pages for suspicious traffic

### Bot Protection

**Cloudflare Bot Management**:
- Bot score for all requests
- Challenge suspicious bots
- Allow verified bots (search engines)

**Custom Rules**:
```
- Block requests with missing User-Agent
- Challenge high-frequency IPs
- Allow known good bots (Googlebot, etc.)
```

### API Security

**Authentication**:
- API key in header (X-API-Key)
- JWT for user sessions
- OAuth 2.0 for partner integrations

**Authorization**:
- Role-based access control (RBAC)
- Partner tier enforcement
- Resource-level permissions

**Input Validation**:
- Schema validation (JSON Schema)
- SQL injection prevention (parameterized queries)
- XSS protection (sanitization)

---

## Deployment Pipeline

### CI/CD Workflow

**GitHub Actions** (All repos):
```yaml
name: Deploy

on:
  push:
    branches: [main, production]

jobs:
  test:
    - Lint (ESLint, Prettier)
    - Type check (TypeScript)
    - Unit tests (Vitest)
    - E2E tests (Playwright)

  build:
    - Build production bundle
    - Optimize images
    - Generate sitemap

  deploy:
    - Deploy to Vercel (preview for PRs)
    - Deploy to production (main branch)
    - Invalidate CDN cache
    - Send Slack notification
```

### Deployment Environments

**Development**:
```
URL: dev.industriverse.ai
Branch: develop
Database: Development instance
Deploy: Automatic on push
```

**Staging**:
```
URL: staging.industriverse.ai
Branch: staging
Database: Staging instance
Deploy: Automatic on push
Testing: Manual QA
```

**Production**:
```
URL: industriverse.ai (all subdomains)
Branch: main
Database: Production instance
Deploy: Automatic after staging approval
Monitoring: Enhanced
```

---

## Compliance & Data Residency

### GDPR Compliance

**Data Residency**: EU customers → EU data centers
**Data Minimization**: Collect only necessary data
**Right to Access**: API endpoint for data export
**Right to Deletion**: 30-day grace period
**Cookie Consent**: Required for analytics

### SOC 2 Type II

**Controls**:
- Access logging (all actions)
- Regular security audits
- Penetration testing (annual)
- Employee background checks
- Encryption at rest and in transit

---

## Future Enhancements

### Short Term (Q1 2025)

- [ ] Edge compute for widget rendering
- [ ] Multi-region database replication
- [ ] Advanced DDoS protection
- [ ] GraphQL API (in addition to REST)
- [ ] WebAssembly for computation-heavy tasks

### Long Term (2025-2026)

- [ ] Self-hosted option for enterprise (Tier 3)
- [ ] On-premise deployment support
- [ ] Air-gapped installations
- [ ] Custom domain support for partners
- [ ] White-labeled mobile apps (iOS, Android)

---

## Contact & Support

**Infrastructure Team**: infra@industriverse.ai
**Security Issues**: security@industriverse.ai
**Emergency**: +1-555-INDSTRVRS (Tier 3 only)

**Documentation**: https://docs.industriverse.ai/infrastructure
**Status Page**: https://status.industriverse.ai
