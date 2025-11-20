# EIL Platform - Grafana Dashboards

Production monitoring dashboards for the Energy Intelligence Layer platform.

## Overview

This directory contains 4 comprehensive Grafana dashboards for monitoring all aspects of the EIL platform:

1. **API Performance** - HTTP metrics, response times, throughput
2. **Energy & Diffusion Metrics** - Physics-specific metrics, energy conservation, regime detection
3. **System Health** - Infrastructure monitoring, resource usage, Kubernetes metrics
4. **Security Monitoring** - Authentication, authorization, rate limiting, security events

## Dashboards

### 1. API Performance Dashboard

**File**: `dashboards/api-performance.json`

**Metrics Tracked**:
- Request rate (RPS) by endpoint
- Total requests counter
- Error rate percentage
- Response time percentiles (P50, P95, P99)
- Status code distribution
- Endpoint performance table
- Active connections
- Request size distribution

**Alerts**:
- ⚠️ High response time (P95 > 1s)
- ⚠️ High error rate (>5%)

**Use Cases**:
- Monitor API health and performance
- Identify slow endpoints
- Track error patterns
- Capacity planning

---

### 2. Energy & Diffusion Metrics Dashboard

**File**: `dashboards/energy-metrics.json`

**Metrics Tracked**:
- **Energy Fidelity Gauge** - Conservation accuracy (target: >95%)
- **Regime Confidence Gauge** - Detection confidence (target: >85%)
- **Diffusion Steps/sec** - Sampling throughput
- Energy conservation over time
- Regime distribution (equilibrium/transition/critical)
- Diffusion sampling duration
- Proof validation rate (valid vs invalid)
- Energy metrics by domain
- Thermodynamic constraint violations
- Boltzmann weighting distribution

**Alerts**:
- 🚨 Low energy fidelity (<95%)
- 🚨 Thermodynamic violations detected

**Use Cases**:
- Validate physics constraints
- Monitor diffusion model health
- Track energy conservation accuracy
- Identify regime transitions
- Debug thermodynamic issues

**Physics-Specific Panels**:
- **Energy Fidelity**: Measures how well energy is conserved (ΔE < tolerance)
- **Regime Detection**: Tracks equilibrium/transition/critical regime classification
- **Boltzmann Weighting**: Distribution of exp(-E/kT) weights in sampling

---

### 3. System Health Dashboard

**File**: `dashboards/system-health.json`

**Metrics Tracked**:
- Pod status and replica count
- CPU usage by pod (percentage and cores)
- Memory usage by pod (percentage and bytes)
- Network I/O (receive/transmit)
- Disk I/O (read/write)
- Pod restart count
- HPA status (current/desired/min/max replicas)
- Resource usage table
- Container filesystem usage
- Goroutines/threads count

**Alerts**:
- ⚠️ Pod restart count exceeded
- ⚠️ High CPU usage (>85%)
- ⚠️ High memory usage (>90%)

**Use Cases**:
- Monitor Kubernetes cluster health
- Track resource utilization
- Identify performance bottlenecks
- Validate autoscaling behavior
- Capacity planning

---

### 4. Security Monitoring Dashboard

**File**: `dashboards/security-monitoring.json`

**Metrics Tracked**:
- Authentication success rate
- Failed login attempts/min
- Rate limit hits/min
- Authentication attempts timeline
- Rate limits by endpoint
- API key usage (valid/invalid/revoked)
- Permission denials by permission type
- Security events table with severity
- Suspicious activity detections
- Token operations (created/refreshed/revoked)
- Top failed login IPs
- Rate limited users
- Audit log events by severity

**Alerts**:
- 🚨 High failed login rate (>10/min) - Possible brute force
- 🚨 Suspicious activity detected
- ⚠️ High rate limit hits

**Use Cases**:
- Detect security threats
- Monitor authentication patterns
- Identify brute force attacks
- Track API key usage
- Audit security events
- Investigate suspicious activity

---

## Installation

### Option 1: Automatic (Helm Chart)

The dashboards are automatically provisioned when deploying via Helm with Grafana enabled:

```bash
helm install eil-platform ./helm/eil-platform \
  --set grafana.enabled=true \
  --namespace eil-platform
```

### Option 2: Manual Import

1. **Access Grafana**:
   ```bash
   kubectl port-forward svc/grafana 3000:80 -n eil-platform
   open http://localhost:3000
   ```

2. **Login**:
   - Username: `admin`
   - Password: Check Helm values or secret

3. **Import Dashboards**:
   - Go to Dashboards → Import
   - Upload each JSON file from `dashboards/`
   - Select Prometheus datasource
   - Click Import

### Option 3: Provisioning via ConfigMap

```bash
# Create ConfigMap with dashboards
kubectl create configmap grafana-dashboards \
  --from-file=dashboards/ \
  --namespace eil-platform

# Mount in Grafana deployment
# (Already configured in Helm chart)
```

---

## Configuration

### Data Sources

The dashboards require these data sources:

1. **Prometheus** (primary)
   - URL: `http://prometheus-server:80`
   - Type: Prometheus
   - Default: Yes

2. **InfluxDB** (optional)
   - URL: `http://influxdb:8086`
   - Type: InfluxDB (Flux)
   - Organization: `eil-platform`
   - Bucket: `energy_metrics`

3. **Neo4j** (optional, requires plugin)
   - URL: `bolt://neo4j:7687`
   - Type: Neo4j
   - Database: `neo4j`

Configure in `provisioning/datasources.yaml` or via Grafana UI.

### Variables

Each dashboard supports template variables for filtering:

- `$datasource` - Select Prometheus instance
- `$namespace` - Kubernetes namespace filter
- `$domain` - Energy domain filter (Energy dashboard)
- `$time_range` - Time range selector

---

## Alerts

### Configured Alerts

| Alert | Condition | Severity | Dashboard |
|-------|-----------|----------|-----------|
| High Response Time | P95 > 1s for 5m | Warning | API Performance |
| High Error Rate | >5% for 5m | Critical | API Performance |
| Low Energy Fidelity | <95% for 10m | Warning | Energy Metrics |
| Thermodynamic Violations | >0.01/s | Critical | Energy Metrics |
| Pod Restarts | >3 in 1h | Warning | System Health |
| High Failed Login Rate | >10/min for 5m | Critical | Security |
| Suspicious Activity | >0.1/s | Critical | Security |

### Alert Channels

Configure alert notification channels in Grafana:

```yaml
# Slack notification
- name: slack-alerts
  type: slack
  uid: slack1
  settings:
    url: <webhook-url>
    recipient: '#eil-alerts'

# PagerDuty
- name: pagerduty
  type: pagerduty
  settings:
    integrationKey: <key>
    severity: critical

# Email
- name: email-ops
  type: email
  settings:
    addresses: ops@eil-platform.io
```

---

## Metrics Reference

### Custom EIL Metrics

These metrics are exposed by the EIL API (`/metrics` endpoint):

#### API Metrics
- `http_requests_total` - Total HTTP requests (counter)
- `http_request_duration_seconds` - Request latency (histogram)
- `http_request_size_bytes` - Request size (histogram)
- `active_connections` - Active HTTP connections (gauge)

#### Energy Metrics
- `energy_fidelity` - Energy conservation fidelity 0-1 (gauge)
- `regime_confidence` - Regime detection confidence 0-1 (gauge)
- `regime_detection_total` - Regime detections by type (counter)
- `energy_conservation_violations_total` - ΔE violations (counter)
- `entropy_monotonicity_violations_total` - ΔS violations (counter)

#### Diffusion Metrics
- `diffusion_steps_total` - Total diffusion steps (counter)
- `diffusion_sample_duration_seconds` - Sampling duration (histogram)
- `boltzmann_weight` - Boltzmann weights (histogram)

#### Proof Metrics
- `proof_validation_total` - Proof validations (counter)

#### Security Metrics
- `auth_attempts_total` - Authentication attempts (counter)
- `api_key_requests_total` - API key requests (counter)
- `rate_limit_exceeded_total` - Rate limit hits (counter)
- `permission_denied_total` - Permission denials (counter)
- `security_event_total` - Security events (counter)
- `audit_events_total` - Audit log events (counter)

### Kubernetes Metrics

From `kube-state-metrics`:

- `kube_pod_status_phase` - Pod phase
- `kube_pod_container_status_restarts_total` - Container restarts
- `kube_deployment_status_replicas_available` - Available replicas
- `kube_horizontalpodautoscaler_*` - HPA metrics
- `container_cpu_usage_seconds_total` - CPU usage
- `container_memory_working_set_bytes` - Memory usage
- `container_network_*` - Network I/O
- `container_fs_*` - Filesystem metrics

---

## Customization

### Adding Panels

1. **Via Grafana UI**:
   - Edit dashboard
   - Add panel
   - Configure query and visualization
   - Save dashboard
   - Export JSON

2. **Via JSON**:
   - Edit dashboard JSON file
   - Add panel to `panels` array
   - Update `gridPos` for layout
   - Increment `id` for new panel

### Creating New Dashboards

Template structure:

```json
{
  "dashboard": {
    "title": "My Dashboard",
    "tags": ["eil", "custom"],
    "panels": [
      {
        "id": 1,
        "title": "My Panel",
        "type": "graph",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "my_metric{job=\"eil-api\"}",
            "legendFormat": "{{label}}",
            "refId": "A"
          }
        ]
      }
    ]
  }
}
```

### Panel Types

Available visualization types:

- **graph** - Time series line/area chart
- **stat** - Single stat with sparkline
- **gauge** - Gauge/meter visualization
- **table** - Tabular data
- **piechart** - Pie/donut chart
- **heatmap** - Heat map
- **bargauge** - Horizontal/vertical bar gauge

---

## Troubleshooting

### No Data Showing

**Check**:
1. Prometheus is scraping metrics:
   ```bash
   # Check targets
   kubectl port-forward svc/prometheus-server 9090:80 -n eil-platform
   open http://localhost:9090/targets
   ```

2. EIL API is exposing metrics:
   ```bash
   kubectl port-forward svc/eil-api 8000:80 -n eil-platform
   curl http://localhost:8000/metrics
   ```

3. Data source is configured:
   - Go to Configuration → Data Sources
   - Test connection to Prometheus

### Missing Metrics

Some metrics may not appear until certain operations occur:

- **Diffusion metrics**: Only after `/v1/diffuse` requests
- **Proof metrics**: Only after `/v1/proof` requests
- **Security metrics**: Only after authentication attempts

### Performance Issues

If dashboards are slow:

1. **Reduce time range**: Use shorter windows (1h instead of 24h)
2. **Increase refresh interval**: Change from 10s to 30s or 1m
3. **Optimize queries**: Use `rate()` with larger windows
4. **Enable query caching**: Configure in Prometheus

### Alert Not Firing

**Debug**:
1. Check alert condition in panel settings
2. Verify metric data exists
3. Check alert evaluation interval
4. Review alert history in Grafana

---

## Best Practices

### Dashboard Usage

1. **Regular Review**: Check dashboards daily for anomalies
2. **Baseline Establishment**: Learn normal patterns first
3. **Alert Tuning**: Adjust thresholds to reduce false positives
4. **Context Correlation**: Use multiple dashboards together for investigation

### Metric Collection

1. **High-Cardinality Labels**: Avoid labels with many unique values
2. **Consistent Naming**: Follow Prometheus naming conventions
3. **Appropriate Types**: Use counters for cumulative, gauges for snapshots
4. **Documentation**: Document custom metrics

### Performance

1. **Query Optimization**: Use `rate()` for counters, `avg_over_time()` for smoothing
2. **Recording Rules**: Pre-compute expensive queries in Prometheus
3. **Data Retention**: Balance history vs storage cost
4. **Dashboard Complexity**: Keep <20 panels per dashboard

---

## Support

- **Documentation**: https://docs.eil-platform.io/monitoring
- **Grafana Docs**: https://grafana.com/docs/
- **Prometheus Docs**: https://prometheus.io/docs/
- **GitHub**: https://github.com/industriverse/eil-platform/issues
- **Email**: support@eil-platform.io

---

## Dashboard Versions

| Dashboard | Version | Last Updated | Author |
|-----------|---------|--------------|--------|
| API Performance | 1.0 | 2025-01 | EIL Team |
| Energy Metrics | 1.0 | 2025-01 | EIL Team |
| System Health | 1.0 | 2025-01 | EIL Team |
| Security Monitoring | 1.0 | 2025-01 | EIL Team |

---

## License

Apache License 2.0 - See LICENSE file for details.
