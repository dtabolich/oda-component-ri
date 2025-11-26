# Microcks Deployment Guide for Kubernetes

Microcks is a comprehensive, cloud-native API mocking and testing platform. This guide covers deploying Microcks on Kubernetes.

## Overview

Microcks provides:
- Multi-protocol support (REST, GraphQL, gRPC, AsyncAPI, SOAP)
- API catalog and governance
- Contract testing
- Kubernetes Operator
- Web UI dashboard
- Git integration for specs

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- 2GB+ available memory
- Storage class for persistent volumes

## Installation Methods

### Method 1: Helm Chart (Recommended)

```bash
# Add Microcks Helm repository
helm repo add microcks https://microcks.io/helm
helm repo update

# Install with default configuration
helm install microcks microcks/microcks \
  --namespace microcks \
  --create-namespace

# Install with custom values
helm install microcks microcks/microcks \
  --namespace microcks \
  --create-namespace \
  -f microcks-values.yaml
```

### Method 2: Kubernetes Operator

```bash
# Install Microcks Operator
kubectl create namespace microcks

# Apply operator manifests
kubectl apply -f https://raw.githubusercontent.com/microcks/microcks-operator/main/deploy/operator.yaml -n microcks

# Create Microcks instance
kubectl apply -f - <<EOF
apiVersion: microcks.github.io/v1alpha1
kind: Microcks
metadata:
  name: microcks
  namespace: microcks
spec:
  version: "1.8.0"
  microcks:
    replicas: 1
    url: microcks.example.com
  postman:
    replicas: 1
  keycloak:
    install: true
    persistent: true
  mongodb:
    install: true
    persistent: true
    volumeSize: 2Gi
  features:
    async:
      enabled: true
EOF
```

### Method 3: Quick Development Setup (Minimal)

```yaml
# microcks-minimal.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: microcks
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microcks
  namespace: microcks
spec:
  replicas: 1
  selector:
    matchLabels:
      app: microcks
  template:
    metadata:
      labels:
        app: microcks
    spec:
      containers:
      - name: microcks
        image: quay.io/microcks/microcks:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_DATA_MONGODB_URI
          value: mongodb://mongodb:27017
        - name: KEYCLOAK_URL
          value: http://keycloak:8080/auth
      - name: postman-runtime
        image: quay.io/microcks/microcks-postman-runtime:latest
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: microcks
  namespace: microcks
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  selector:
    app: microcks
---
# MongoDB for storage
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: microcks
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:4.4
        ports:
        - containerPort: 27017
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: microcks
spec:
  ports:
  - port: 27017
  selector:
    app: mongodb
```

## Custom Values Configuration

```yaml
# microcks-values.yaml

# Microcks application
microcks:
  replicas: 2
  url: microcks.example.com
  
  # Resource limits
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

# Postman runtime for tests
postman:
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"

# MongoDB configuration
mongodb:
  install: true
  persistent: true
  volumeSize: 5Gi
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"

# Keycloak for authentication
keycloak:
  install: true
  persistent: true
  volumeSize: 1Gi
  
# Features
features:
  async:
    enabled: true
    defaultBinding: KAFKA
    kafka:
      url: kafka-bootstrap:9092

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: microcks.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: microcks-tls
      hosts:
        - microcks.example.com
```

## Post-Installation Setup

### 1. Get Access Credentials

```bash
# Get Keycloak admin password
kubectl get secret microcks-keycloak-admin \
  -n microcks \
  -o jsonpath='{.data.password}' | base64 -d

# Get service URL
kubectl get svc microcks -n microcks
```

### 2. Access the UI

```bash
# Port-forward to access locally
kubectl port-forward svc/microcks 8080:8080 -n microcks

# Open browser
open http://localhost:8080
```

### 3. Import API Specifications

**Via UI**:
1. Navigate to http://localhost:8080
2. Click "Importers"
3. Add importer (Git, URL, or Upload)

**Via API**:
```bash
# Import OpenAPI spec
curl -X POST http://localhost:8080/api/artifact/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@openapi.yaml"
```

**Via Git Integration**:
```yaml
# Create importer via kubectl
apiVersion: v1
kind: Secret
metadata:
  name: microcks-github-secret
  namespace: microcks
type: Opaque
stringData:
  username: your-github-username
  token: your-github-token
---
# Then configure in Microcks UI or via API
```

## Working with Microcks

### Import OpenAPI Specification

```bash
# Example OpenAPI spec: users-api.yaml
cat > users-api.yaml <<EOF
openapi: 3.0.0
info:
  title: Users API
  version: 1.0.0
  x-microcks:
    examples:
      - name: "John Doe"
        summary: "User John"
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
              examples:
                users_list:
                  value:
                    - id: 1
                      name: John Doe
                    - id: 2
                      name: Jane Smith
  /users/{id}:
    get:
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
              examples:
                user_john:
                  value:
                    id: 1
                    name: John Doe
EOF

# Import to Microcks
curl -X POST http://localhost:8080/api/artifact/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@users-api.yaml"
```

### Access Mock Endpoints

```bash
# Mocks are available at:
# http://microcks:8080/rest/Users API/1.0.0/users

# From within cluster:
curl http://microcks.microcks.svc.cluster.local:8080/rest/Users%20API/1.0.0/users

# From local (with port-forward):
curl http://localhost:8080/rest/Users%20API/1.0.0/users
```

### Run Contract Tests

```bash
# Via Microcks API
curl -X POST http://localhost:8080/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "serviceId": "Users API:1.0.0",
    "testEndpoint": "http://your-api.example.com/users",
    "runnerType": "POSTMAN"
  }'
```

## Integration Examples

### With CI/CD (GitHub Actions)

```yaml
# .github/workflows/api-test.yml
name: API Contract Test
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Import API to Microcks
        run: |
          curl -X POST ${{ secrets.MICROCKS_URL }}/api/artifact/upload \
            -H "Content-Type: multipart/form-data" \
            -F "file=@api/openapi.yaml"
      
      - name: Run Contract Test
        run: |
          curl -X POST ${{ secrets.MICROCKS_URL }}/api/tests \
            -H "Content-Type: application/json" \
            -d '{
              "serviceId": "My API:1.0.0",
              "testEndpoint": "${{ secrets.TEST_ENDPOINT }}",
              "runnerType": "POSTMAN"
            }'
```

### With ArgoCD (GitOps)

```yaml
# applications/microcks-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: microcks
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://microcks.io/helm
    chart: microcks
    targetRevision: 1.8.0
    helm:
      values: |
        microcks:
          url: microcks.example.com
        ingress:
          enabled: true
  destination:
    server: https://kubernetes.default.svc
    namespace: microcks
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### With Kafka (AsyncAPI)

```yaml
# Enable Kafka integration
features:
  async:
    enabled: true
    defaultBinding: KAFKA
    kafka:
      url: kafka-bootstrap.kafka:9092
```

Then import AsyncAPI specs:

```yaml
asyncapi: 2.5.0
info:
  title: User Events
  version: 1.0.0
channels:
  user/created:
    publish:
      message:
        payload:
          type: object
          properties:
            userId:
              type: string
            name:
              type: string
```

## Monitoring and Observability

### Prometheus Metrics

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: microcks
  namespace: microcks
spec:
  selector:
    matchLabels:
      app: microcks
  endpoints:
  - port: http
    path: /actuator/prometheus
```

### Logging

```bash
# View Microcks logs
kubectl logs -n microcks -l app=microcks -f

# View specific component
kubectl logs -n microcks deployment/microcks -c microcks -f
```

## Backup and Restore

### Backup MongoDB Data

```bash
# Backup
kubectl exec -n microcks deployment/microcks-mongodb -- \
  mongodump --out=/tmp/backup

kubectl cp microcks/microcks-mongodb-xxx:/tmp/backup ./backup

# Restore
kubectl cp ./backup microcks/microcks-mongodb-xxx:/tmp/backup

kubectl exec -n microcks deployment/microcks-mongodb -- \
  mongorestore /tmp/backup
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n microcks
kubectl describe pod <pod-name> -n microcks
```

### Common Issues

**MongoDB Connection Failed**:
```bash
# Check MongoDB is running
kubectl get pods -n microcks -l app=mongodb

# Check connection string
kubectl get configmap microcks-config -n microcks -o yaml
```

**Keycloak Authentication Issues**:
```bash
# Restart Keycloak
kubectl rollout restart deployment/microcks-keycloak -n microcks

# Reset admin password
kubectl get secret microcks-keycloak-admin -n microcks
```

## Uninstallation

```bash
# Via Helm
helm uninstall microcks -n microcks

# Clean up namespace
kubectl delete namespace microcks
```

## Production Recommendations

1. **Enable Persistence**: Use PersistentVolumes for MongoDB and Keycloak
2. **High Availability**: Run multiple replicas of Microcks and Postman runtime
3. **Resource Limits**: Set appropriate CPU/memory limits
4. **TLS**: Enable TLS via Ingress with cert-manager
5. **Backup**: Regular MongoDB backups
6. **Monitoring**: Integrate with Prometheus/Grafana
7. **Authentication**: Configure Keycloak with your IdP (LDAP, SAML, OIDC)

## Comparison: Microcks vs Prism

| Feature | Microcks | Prism |
|---------|----------|-------|
| OpenAPI Support | ✅ Full | ✅ Full |
| GraphQL | ✅ | ❌ |
| gRPC | ✅ | ❌ |
| AsyncAPI | ✅ | ❌ |
| Web UI | ✅ | ❌ |
| Contract Testing | ✅ | ⚠️ Limited |
| State Management | ✅ | ❌ |
| Complexity | High | Low |
| Resource Usage | High (~500MB+) | Low (~50MB) |
| Setup Time | ~5-10 min | ~1 min |
| Best For | Enterprise | Simple mocking |

## Resources

- [Microcks Documentation](https://microcks.io/documentation/)
- [Microcks GitHub](https://github.com/microcks/microcks)
- [Helm Chart Repository](https://github.com/microcks/microcks-helm-chart)
- [Kubernetes Operator](https://github.com/microcks/microcks-operator)
- [Community](https://microcks.io/community/)

---

**When to Use Microcks**:
- ✅ Multiple protocols (REST, gRPC, GraphQL, AsyncAPI)
- ✅ Enterprise API management
- ✅ Contract testing at scale
- ✅ API catalog and governance
- ✅ Team collaboration on API specs

**When to Use Prism Instead**:
- ✅ Simple OpenAPI mocking
- ✅ Fast startup needed
- ✅ Minimal resource usage
- ✅ Quick prototyping
- ✅ CI/CD with tight time constraints
