# Prism Mock Server - Comprehensive Deployment Guide

This guide covers various deployment scenarios for Prism Mock Server in Kubernetes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Basic Deployment](#basic-deployment)
3. [Deployment Scenarios](#deployment-scenarios)
4. [Advanced Configuration](#advanced-configuration)
5. [Integration Examples](#integration-examples)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Kubernetes Cluster**: v1.19 or higher
  - Local: Minikube, kind, k3s, Docker Desktop
  - Cloud: GKE, EKS, AKS, or any managed Kubernetes
- **kubectl**: Configured to access your cluster
- **Helm**: Version 3.0 or higher

### Verify Installation

```bash
# Check Kubernetes
kubectl version --short

# Check Helm
helm version --short

# Check cluster access
kubectl cluster-info
```

## Basic Deployment

### 1. Install from Local Chart

```bash
# Navigate to the charts directory
cd /path/to/charts

# Install with default values
helm install my-mock-server ./PrismMockServer

# Install in a specific namespace
helm install my-mock-server ./PrismMockServer -n dev --create-namespace
```

### 2. Verify Installation

```bash
# Check Helm release
helm list -n dev

# Check pods
kubectl get pods -n dev -l app=my-mock-server-prism

# Check services
kubectl get svc -n dev -l app=my-mock-server-prism

# View deployment logs
kubectl logs -n dev -l app=my-mock-server-prism
```

### 3. Access the Mock Server

```bash
# Port-forward to local machine
kubectl port-forward -n dev svc/my-mock-server-prism 8080:80

# Test in another terminal
curl http://localhost:8080/health
```

## Deployment Scenarios

### Scenario 1: Development Environment

**Use Case**: Individual developers need a mock API for local testing.

```bash
helm install dev-mock ./PrismMockServer \
  --namespace dev-${USER} \
  --create-namespace \
  --set prism.replicaCount=1 \
  --set service.type=NodePort \
  --set service.nodePort=30080 \
  --set resources.requests.cpu=50m \
  --set resources.requests.memory=64Mi \
  --set spec.url="https://your-repo.com/api-spec.yaml"
```

### Scenario 2: CI/CD Pipeline

**Use Case**: Mock APIs for automated testing in CI/CD.

```yaml
# ci-values.yaml
prism:
  replicaCount: 1
  options:
    cors: true
    validation: true
    errors: true

spec:
  url: "${API_SPEC_URL}"  # Injected by CI/CD

service:
  type: ClusterIP

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 50m
    memory: 64Mi

# Disable probes if startup is fast
livenessProbe:
  initialDelaySeconds: 5
readinessProbe:
  initialDelaySeconds: 3
```

Deploy in CI/CD:

```bash
# GitLab CI, Jenkins, GitHub Actions, etc.
helm install test-mock ./PrismMockServer \
  -f ci-values.yaml \
  --set spec.url="${CI_PROJECT_URL}/-/raw/${CI_COMMIT_SHA}/api/openapi.yaml" \
  --wait \
  --timeout 2m
```

### Scenario 3: QA/Testing Environment

**Use Case**: Shared mock servers for QA team.

```yaml
# qa-values.yaml
prism:
  replicaCount: 2
  options:
    cors: true
    validation: true
    dynamic: true  # Enable dynamic examples

spec:
  existingConfigMap: "qa-api-specs"
  configMapKey: "openapi.yaml"

service:
  type: ClusterIP

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: qa-mock.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

Deploy:

```bash
# First, create ConfigMap with API spec
kubectl create configmap qa-api-specs \
  --from-file=openapi.yaml=./specs/qa-api-spec.yaml \
  -n qa

# Deploy Prism
helm install qa-mock ./PrismMockServer -f qa-values.yaml -n qa
```

### Scenario 4: Production Mock Service

**Use Case**: High-availability mock server for demos or partner integrations.

```yaml
# production-values.yaml
prism:
  replicaCount: 3
  options:
    cors: true
    validation: true
    errors: false  # Hide detailed errors

spec:
  url: "https://s3.amazonaws.com/your-bucket/api-specs/production-v1.yaml"

service:
  type: ClusterIP

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api-mock.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-mock-tls
      hosts:
        - api-mock.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - prism
          topologyKey: kubernetes.io/hostname
```

### Scenario 5: Multiple API Versions

**Use Case**: Run multiple versions of the same API.

```bash
# Deploy v1
helm install api-v1-mock ./PrismMockServer \
  --set spec.url="https://repo.com/api-v1-spec.yaml" \
  --set service.port=8080

# Deploy v2
helm install api-v2-mock ./PrismMockServer \
  --set spec.url="https://repo.com/api-v2-spec.yaml" \
  --set service.port=8080

# Access v1: http://api-v1-mock-prism.default.svc.cluster.local:8080
# Access v2: http://api-v2-mock-prism.default.svc.cluster.local:8080
```

## Advanced Configuration

### Using External Secrets

For sensitive API specs stored in external secret managers:

```yaml
# Use External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-spec-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: prism-api-spec
    template:
      type: Opaque
      data:
        openapi.yaml: "{{ .apiSpec }}"
  data:
    - secretKey: apiSpec
      remoteRef:
        key: production/api-spec
```

Then reference in Helm values:

```yaml
spec:
  existingConfigMap: "prism-api-spec"
```

### Custom Resource Limits per Environment

```yaml
# Small (dev)
resources:
  requests: { cpu: 50m, memory: 64Mi }
  limits: { cpu: 200m, memory: 256Mi }

# Medium (qa)
resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits: { cpu: 500m, memory: 512Mi }

# Large (prod)
resources:
  requests: { cpu: 200m, memory: 256Mi }
  limits: { cpu: 1000m, memory: 1Gi }
```

### Network Policies

Restrict traffic to mock server:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: prism-network-policy
spec:
  podSelector:
    matchLabels:
      app: my-mock-prism
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: frontend
        - namespaceSelector:
            matchLabels:
              name: backend
      ports:
        - protocol: TCP
          port: 4010
```

## Integration Examples

### With Frontend Applications

```typescript
// React/Vue/Angular frontend
const API_BASE_URL = process.env.REACT_APP_MOCK_API || 
  'http://api-mock.example.com';

fetch(`${API_BASE_URL}/users`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### With Backend Services

```python
# Python backend
import os
import requests

MOCK_API_URL = os.getenv('MOCK_API_URL', 
  'http://my-mock-prism.default.svc.cluster.local')

response = requests.get(f'{MOCK_API_URL}/products')
products = response.json()
```

### In Docker Compose (for local development)

```yaml
version: '3.8'
services:
  prism:
    image: stoplight/prism:5
    command: mock -h 0.0.0.0 /tmp/openapi.yaml
    volumes:
      - ./openapi.yaml:/tmp/openapi.yaml
    ports:
      - "4010:4010"
  
  app:
    build: .
    environment:
      - API_URL=http://prism:4010
    depends_on:
      - prism
```

## Monitoring and Logging

### Prometheus Monitoring

Add ServiceMonitor for Prometheus:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: prism-monitor
spec:
  selector:
    matchLabels:
      app: my-mock-prism
  endpoints:
    - port: http
      interval: 30s
```

### Logging with Fluent Bit

```yaml
# Add to deployment
annotations:
  fluentbit.io/parser: json
```

### Health Checks

```bash
# Check health endpoint
curl http://my-mock-prism.default.svc.cluster.local/

# Watch pod health
kubectl get pods -w -l app=my-mock-prism
```

## Security Best Practices

### 1. Run as Non-Root User

Already configured in `values.yaml`:

```yaml
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
  readOnlyRootFilesystem: true
```

### 2. Use Network Policies

Restrict which pods can access the mock server.

### 3. Enable TLS/HTTPS

Use Ingress with TLS:

```yaml
ingress:
  enabled: true
  tls:
    - secretName: prism-tls
      hosts:
        - mock-api.example.com
```

### 4. Rate Limiting

Configure at Ingress level:

```yaml
ingress:
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
```

### 5. RBAC

Create minimal RBAC for the service account if needed.

## Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod -l app=my-mock-prism

# Check logs
kubectl logs -l app=my-mock-prism

# Common issues:
# - Invalid OpenAPI spec
# - Image pull errors
# - Resource constraints
```

### Invalid OpenAPI Spec

```bash
# Validate your spec
docker run --rm -v $(pwd):/workspace \
  stoplight/spectral lint /workspace/openapi.yaml

# Or use online validator
# https://editor.swagger.io/
```

### Service Not Accessible

```bash
# Check service
kubectl get svc,endpoints -l app=my-mock-prism

# Test from debug pod
kubectl run debug --image=curlimages/curl -it --rm -- \
  curl http://my-mock-prism.default.svc.cluster.local/
```

### Memory Issues

```bash
# Check resource usage
kubectl top pods -l app=my-mock-prism

# Increase memory limits
helm upgrade my-mock ./PrismMockServer \
  --set resources.limits.memory=1Gi \
  --reuse-values
```

### Ingress Not Working

```bash
# Check ingress
kubectl get ingress

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Verify DNS
nslookup mock-api.example.com
```

## Upgrade and Rollback

### Upgrade Release

```bash
# Upgrade with new values
helm upgrade my-mock ./PrismMockServer -f new-values.yaml

# Upgrade with set flags
helm upgrade my-mock ./PrismMockServer \
  --set prism.replicaCount=5 \
  --reuse-values
```

### Rollback Release

```bash
# List revisions
helm history my-mock

# Rollback to previous version
helm rollback my-mock

# Rollback to specific revision
helm rollback my-mock 2
```

## Clean Up

```bash
# Uninstall release
helm uninstall my-mock

# Delete namespace (if dedicated)
kubectl delete namespace dev

# Clean up ConfigMaps (if not managed by Helm)
kubectl delete configmap qa-api-specs
```

## Best Practices Summary

1. ✅ Use dedicated namespaces per environment
2. ✅ Store OpenAPI specs in version control
3. ✅ Set appropriate resource limits
4. ✅ Enable health checks
5. ✅ Use Ingress for external access
6. ✅ Implement network policies
7. ✅ Monitor resource usage
8. ✅ Version your API specifications
9. ✅ Use ConfigMaps or URLs for specs (not inline in production)
10. ✅ Test your Prism deployment in lower environments first

## Additional Resources

- [Prism Documentation](https://docs.stoplight.io/docs/prism)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [OpenAPI Specification](https://swagger.io/specification/)

## Getting Help

- Check the [README.md](README.md) for basic information
- See [QUICKSTART.md](QUICKSTART.md) for quick setup
- Review the [examples/](examples/) directory
- Open an issue in the repository

---

**Happy Mocking!** 🚀
