# Kubernetes Deployment Guide for Workflow Automation Layer

## Overview

This guide provides detailed instructions for deploying the Industriverse Workflow Automation Layer on Kubernetes. It covers configuration, deployment strategies, scaling, monitoring, and maintenance procedures.

## Prerequisites

Before deploying the Workflow Automation Layer, ensure you have:

1. A Kubernetes cluster (version 1.19+)
2. `kubectl` configured to communicate with your cluster
3. Helm (version 3.0+) installed
4. Access to container registries containing Workflow Automation Layer images
5. Persistent storage provisioner in your cluster
6. Ingress controller (e.g., NGINX, Traefik) for external access

## Architecture

The Workflow Automation Layer deployment consists of the following components:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                      Kubernetes Cluster                             │
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │             │    │             │    │             │             │
│  │  Workflow   │    │   Agent     │    │    n8n      │             │
│  │  API Server │    │  Services   │    │  Integration│             │
│  │             │    │             │    │             │             │
│  └──────┬──────┘    └──────┬──────┘    └─────────────┘             │
│         │                  │                                       │
│         └──────────┬───────┘                                       │
│                    │                                               │
│          ┌─────────▼──────────┐    ┌─────────────────┐             │
│          │                    │    │                 │             │
│          │  Workflow Engine   │    │   Databases     │             │
│          │                    │    │                 │             │
│          └────────────────────┘    └─────────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Deployment Configuration

### 1. Namespace Setup

Create a dedicated namespace for the Workflow Automation Layer:

```bash
kubectl create namespace workflow-automation
kubectl config set-context --current --namespace=workflow-automation
```

### 2. Configuration

Create a ConfigMap for the Workflow Automation Layer:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: workflow-automation-config
  namespace: workflow-automation
data:
  config.yaml: |
    api:
      port: 8080
      cors:
        enabled: true
        allowed_origins: ["https://industriverse.example.com"]
      rate_limiting:
        enabled: true
        requests_per_minute: 300
    
    workflow_engine:
      execution_modes:
        default_mode: "supervised"
        trust_threshold:
          autonomous: 0.8
          supervised: 0.5
          collaborative: 0.3
      mesh_topology:
        default_topology: "hybrid"
        edge_integration_enabled: true
      telemetry:
        enabled: true
        retention_days: 30
    
    agents:
      auto_scaling:
        enabled: true
        min_replicas: 1
        max_replicas: 10
      health_check:
        enabled: true
        interval_seconds: 30
    
    n8n_integration:
      enabled: true
      n8n_url: "http://n8n-service:5678"
      webhook_base_url: "https://workflow-api.industriverse.example.com/n8n/webhooks"
    
    security:
      authentication:
        oauth2:
          enabled: true
          issuer_url: "https://auth.industriverse.example.com"
        api_key:
          enabled: true
      authorization:
        rbac_enabled: true
    
    databases:
      workflow_db:
        host: "workflow-db-service"
        port: 5432
        database: "workflow_automation"
      telemetry_db:
        host: "telemetry-db-service"
        port: 27017
        database: "workflow_telemetry"
```

### 3. Secrets

Create secrets for database credentials and API keys:

```bash
kubectl create secret generic workflow-db-credentials \
  --from-literal=username=workflow_user \
  --from-literal=password=your-secure-password

kubectl create secret generic telemetry-db-credentials \
  --from-literal=username=telemetry_user \
  --from-literal=password=your-secure-password

kubectl create secret generic n8n-api-key \
  --from-literal=api-key=your-n8n-api-key
```

### 4. Storage

Create persistent volume claims for the databases:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: workflow-db-pvc
  namespace: workflow-automation
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: telemetry-db-pvc
  namespace: workflow-automation
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard
```

## Deployment

### 1. Database Deployments

#### PostgreSQL for Workflow Database

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-db
  namespace: workflow-automation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: workflow-db
  template:
    metadata:
      labels:
        app: workflow-db
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: workflow_automation
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: password
        volumeMounts:
        - name: workflow-db-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: workflow-db-storage
        persistentVolumeClaim:
          claimName: workflow-db-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: workflow-db-service
  namespace: workflow-automation
spec:
  selector:
    app: workflow-db
  ports:
  - port: 5432
    targetPort: 5432
```

#### MongoDB for Telemetry Database

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telemetry-db
  namespace: workflow-automation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: telemetry-db
  template:
    metadata:
      labels:
        app: telemetry-db
    spec:
      containers:
      - name: mongodb
        image: mongo:5
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_DATABASE
          value: workflow_telemetry
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: password
        volumeMounts:
        - name: telemetry-db-storage
          mountPath: /data/db
      volumes:
      - name: telemetry-db-storage
        persistentVolumeClaim:
          claimName: telemetry-db-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: telemetry-db-service
  namespace: workflow-automation
spec:
  selector:
    app: telemetry-db
  ports:
  - port: 27017
    targetPort: 27017
```

### 2. Workflow API Server Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-api-server
  namespace: workflow-automation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-api-server
  template:
    metadata:
      labels:
        app: workflow-api-server
    spec:
      containers:
      - name: api-server
        image: industriverse/workflow-api-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: CONFIG_PATH
          value: "/etc/workflow-automation/config.yaml"
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: password
        - name: TELEMETRY_DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: username
        - name: TELEMETRY_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: password
        - name: N8N_API_KEY
          valueFrom:
            secretKeyRef:
              name: n8n-api-key
              key: api-key
        volumeMounts:
        - name: config-volume
          mountPath: /etc/workflow-automation
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: workflow-automation-config

---
apiVersion: v1
kind: Service
metadata:
  name: workflow-api-service
  namespace: workflow-automation
spec:
  selector:
    app: workflow-api-server
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### 3. Workflow Engine Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-engine
  namespace: workflow-automation
spec:
  replicas: 2
  selector:
    matchLabels:
      app: workflow-engine
  template:
    metadata:
      labels:
        app: workflow-engine
    spec:
      containers:
      - name: engine
        image: industriverse/workflow-engine:latest
        env:
        - name: CONFIG_PATH
          value: "/etc/workflow-automation/config.yaml"
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: password
        - name: TELEMETRY_DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: username
        - name: TELEMETRY_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: telemetry-db-credentials
              key: password
        volumeMounts:
        - name: config-volume
          mountPath: /etc/workflow-automation
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: workflow-automation-config
```

### 4. Agent Services Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-agents
  namespace: workflow-automation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-agents
  template:
    metadata:
      labels:
        app: workflow-agents
    spec:
      containers:
      - name: agents
        image: industriverse/workflow-agents:latest
        env:
        - name: CONFIG_PATH
          value: "/etc/workflow-automation/config.yaml"
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: password
        volumeMounts:
        - name: config-volume
          mountPath: /etc/workflow-automation
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8082
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: workflow-automation-config
```

### 5. n8n Integration Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n-integration
  namespace: workflow-automation
spec:
  replicas: 2
  selector:
    matchLabels:
      app: n8n-integration
  template:
    metadata:
      labels:
        app: n8n-integration
    spec:
      containers:
      - name: n8n-integration
        image: industriverse/n8n-integration:latest
        env:
        - name: CONFIG_PATH
          value: "/etc/workflow-automation/config.yaml"
        - name: N8N_API_KEY
          valueFrom:
            secretKeyRef:
              name: n8n-api-key
              key: api-key
        volumeMounts:
        - name: config-volume
          mountPath: /etc/workflow-automation
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8083
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: workflow-automation-config

---
apiVersion: v1
kind: Service
metadata:
  name: n8n-integration-service
  namespace: workflow-automation
spec:
  selector:
    app: n8n-integration
  ports:
  - port: 80
    targetPort: 8083
  type: ClusterIP
```

### 6. Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: workflow-automation-ingress
  namespace: workflow-automation
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - workflow-api.industriverse.example.com
    secretName: workflow-api-tls
  rules:
  - host: workflow-api.industriverse.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: workflow-api-service
            port:
              number: 80
```

## Horizontal Pod Autoscaling

Configure horizontal pod autoscaling for the API server and workflow engine:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: workflow-api-hpa
  namespace: workflow-automation
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: workflow-api-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: workflow-engine-hpa
  namespace: workflow-automation
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: workflow-engine
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring and Logging

### 1. Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: workflow-automation-monitor
  namespace: workflow-automation
spec:
  selector:
    matchLabels:
      app: workflow-api-server
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
```

### 2. Logging Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: workflow-automation-logging
  namespace: workflow-automation
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        1
        Log_Level    info
        Daemon       off
        Parsers_File parsers.conf

    [INPUT]
        Name             tail
        Path             /var/log/containers/workflow-*.log
        Parser           docker
        Tag              kube.*
        Refresh_Interval 5
        Mem_Buf_Limit    5MB
        Skip_Long_Lines  On

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Merge_Log           On
        K8S-Logging.Parser  On
        K8S-Logging.Exclude Off

    [OUTPUT]
        Name            es
        Match           *
        Host            elasticsearch-master
        Port            9200
        Logstash_Format On
        Logstash_Prefix workflow-automation
        Replace_Dots    On
        Retry_Limit     False
```

## Deployment Strategies

### 1. Rolling Updates

The default deployment strategy is Rolling Updates, which ensures zero downtime during updates:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
```

### 2. Blue-Green Deployment

For critical updates, consider using a Blue-Green deployment strategy:

1. Deploy a new version of the application with a different label:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-api-server-green
  namespace: workflow-automation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-api-server
      version: green
  template:
    metadata:
      labels:
        app: workflow-api-server
        version: green
    # ... rest of the template
```

2. Test the new deployment internally.

3. Switch traffic by updating the service selector:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: workflow-api-service
  namespace: workflow-automation
spec:
  selector:
    app: workflow-api-server
    version: green  # Changed from 'blue' to 'green'
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

4. Once confirmed working, remove the old deployment.

## Backup and Disaster Recovery

### 1. Database Backups

Schedule regular backups of the PostgreSQL and MongoDB databases:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: workflow-db-backup
  namespace: workflow-automation
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h workflow-db-service -U $DB_USERNAME -d workflow_automation | gzip > /backups/workflow-db-$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: workflow-db-credentials
                  key: password
            - name: DB_USERNAME
              valueFrom:
                secretKeyRef:
                  name: workflow-db-credentials
                  key: username
            volumeMounts:
            - name: backup-volume
              mountPath: /backups
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: workflow-backups-pvc
          restartPolicy: OnFailure
```

### 2. Configuration Backups

Regularly export and backup Kubernetes resources:

```bash
kubectl get configmap,secret,deployment,service,ingress -n workflow-automation -o yaml > workflow-automation-backup-$(date +%Y%m%d).yaml
```

## Scaling Considerations

### 1. Vertical Scaling

Adjust resource requests and limits based on observed usage patterns:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### 2. Horizontal Scaling

Adjust HPA settings based on load patterns and performance requirements:

```yaml
spec:
  minReplicas: 5  # Increased from 3
  maxReplicas: 15  # Increased from 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Decreased from 70 for earlier scaling
```

### 3. Database Scaling

For high-volume deployments, consider implementing database replication:

```yaml
# PostgreSQL with replication
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: workflow-db
  namespace: workflow-automation
spec:
  serviceName: "workflow-db"
  replicas: 3
  selector:
    matchLabels:
      app: workflow-db
  template:
    # ... template configuration
```

## Multi-Environment Deployment

### 1. Environment-Specific Configuration

Use Kustomize to manage environment-specific configurations:

```
workflow-automation/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── development/
│   │   ├── configmap.yaml
│   │   └── kustomization.yaml
│   ├── staging/
│   │   ├── configmap.yaml
│   │   └── kustomization.yaml
│   └── production/
│       ├── configmap.yaml
│       ├── hpa.yaml
│       └── kustomization.yaml
```

### 2. Deployment to Different Environments

```bash
# Development
kubectl apply -k workflow-automation/overlays/development

# Staging
kubectl apply -k workflow-automation/overlays/staging

# Production
kubectl apply -k workflow-automation/overlays/production
```

## Troubleshooting

### 1. Pod Status Issues

Check pod status and logs:

```bash
kubectl get pods -n workflow-automation
kubectl describe pod <pod-name> -n workflow-automation
kubectl logs <pod-name> -n workflow-automation
```

### 2. Database Connection Issues

Check database connectivity:

```bash
kubectl exec -it <workflow-api-pod> -n workflow-automation -- curl workflow-db-service:5432
kubectl exec -it <workflow-api-pod> -n workflow-automation -- curl telemetry-db-service:27017
```

### 3. Service Discovery Issues

Check DNS resolution:

```bash
kubectl exec -it <workflow-api-pod> -n workflow-automation -- nslookup workflow-db-service
kubectl exec -it <workflow-api-pod> -n workflow-automation -- nslookup telemetry-db-service
```

### 4. Resource Constraints

Check resource usage:

```bash
kubectl top pods -n workflow-automation
kubectl top nodes
```

## Maintenance Procedures

### 1. Rolling Updates

Apply updates with zero downtime:

```bash
kubectl set image deployment/workflow-api-server api-server=industriverse/workflow-api-server:new-version -n workflow-automation
```

### 2. Configuration Updates

Update ConfigMaps and restart affected deployments:

```bash
kubectl apply -f updated-configmap.yaml -n workflow-automation
kubectl rollout restart deployment workflow-api-server -n workflow-automation
```

### 3. Database Migrations

Run database migrations as a Kubernetes Job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: workflow-db-migration
  namespace: workflow-automation
spec:
  template:
    spec:
      containers:
      - name: migration
        image: industriverse/workflow-migration:latest
        env:
        - name: DB_HOST
          value: "workflow-db-service"
        - name: DB_NAME
          value: "workflow_automation"
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: workflow-db-credentials
              key: password
      restartPolicy: Never
  backoffLimit: 4
```

## Security Considerations

### 1. Network Policies

Restrict network traffic between components:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: workflow-api-policy
  namespace: workflow-automation
spec:
  podSelector:
    matchLabels:
      app: workflow-api-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: workflow-db
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: telemetry-db
    ports:
    - protocol: TCP
      port: 27017
```

### 2. Pod Security Context

Configure security contexts for pods:

```yaml
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: api-server
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
```

### 3. Secret Management

Consider using a dedicated secret management solution like HashiCorp Vault:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: workflow-vault-auth
  namespace: workflow-automation

---
# Vault Agent configuration
```

## Conclusion

This guide provides a comprehensive approach to deploying the Industriverse Workflow Automation Layer on Kubernetes. By following these instructions, you can set up a scalable, resilient, and secure deployment that meets your production requirements.

## Additional Resources

- [Workflow Automation Layer Documentation](workflow_automation_layer_documentation.md)
- [API Reference](api_reference.md)
- [Security and Compliance Guide](security_compliance_guide.md)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

## Version History

- **1.0.0** (2025-05-22): Initial deployment guide
