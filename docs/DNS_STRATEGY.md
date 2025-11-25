# Industriverse DNS & Deployment Strategy

## Overview
This document maps the **Industriverse Architecture** (Portal, BridgeAPI, Sovereign Capsules) to your existing **Cloudflare DNS Records** and the new **thermodynasty.com** domain.

## Domain Strategy

### 1. Primary Domains
- **`industriverse.ai`**: The Core Nexus.
- **`thermodynasty.com`**: The Public Face / Brand Identity (Marketing & Investor Relations).

### 2. Subdomain Mapping (Cloudflare)

Based on your provided records, here is the recommended mapping for the deployed services:

| Subdomain | Target Service | Description |
| :--- | :--- | :--- |
| **`portal.industriverse.ai`** | **Frontend Dashboard** | The main "Industriverse Portal" we just built. Users log in here to view the Energy Atlas and ignite capsules. |
| **`api.industriverse.ai`** | **BridgeAPI (Backend)** | The main entry point for all HTTP traffic (`/v1/capsules`, `/v1/shield`). |
| **`reactor.industriverse.ai`** | **Thermal Sampler** | Dedicated endpoint for high-compute thermodynamic sampling tasks (JAX/TPU workloads). |
| **`capsules.industriverse.ai`** | **Capsule Registry** | A public directory or documentation site for the 27 Sovereign Capsules. |
| **`ws.industriverse.ai`** | **WebSockets** | Real-time telemetry for the "Energy Field" visualization (future upgrade from polling). |
| **`dash.industriverse.ai`** | **Ops/Admin** | Internal monitoring for system health (Prometheus/Grafana). |
| **`foundry.industriverse.ai`** | **CI/CD** | Build server or artifact repository. |

### 3. `thermodynasty.com` Integration
Use this domain as the "glossy" landing page that redirects to the functional portal.
- **`www.thermodynasty.com`** -> **Landing Page** (Marketing, Vision, "The Story").
- **`app.thermodynasty.com`** -> CNAME to **`portal.industriverse.ai`** (Seamless access).

## Deployment Next Steps

1.  **Build Frontend**: Run `npm run build` to generate the static assets for `portal`.
2.  **Deploy Backend**: Containerize `src.bridge_api.server` and deploy to your cloud provider (AWS/GCP/DigitalOcean).
3.  **Update DNS**: Point the `A` records (or `CNAME`) in Cloudflare to your cloud load balancer IPs.

> [!TIP]
> **Security Note**: Ensure `api.industriverse.ai` is proxied via Cloudflare (Orange Cloud) to utilize their WAF and DDoS protection, especially for the `reactor` endpoint.
