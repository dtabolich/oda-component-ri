# Prism Mock Server Kubernetes Deployment - Complete Overview

This document provides a comprehensive overview of the Prism Mock Server Helm chart for Kubernetes deployment.

## 📋 What is Prism?

[Stoplight Prism](https://stoplight.io/open-source/prism) is an open-source HTTP mock server that can simulate APIs based on OpenAPI v2/v3 (formerly Swagger) specifications. It's perfect for:

- **Frontend Development**: Develop UIs before the backend is ready
- **API Testing**: Test your applications against a predictable API
- **CI/CD Pipelines**: Run integration tests without external dependencies
- **API Validation**: Validate requests and responses against your OpenAPI spec
- **Demos & Presentations**: Demonstrate your API without a full backend

## 🎯 What This Helm Chart Provides

A complete, production-ready Helm chart for deploying Prism in Kubernetes with:

✅ **Flexible OpenAPI Spec Management**
- Inline YAML in values.yaml
- External URL (Git, S3, HTTP)
- Existing ConfigMap

✅ **Security Hardening**
- Non-root container
- Read-only filesystem
- Security contexts
- Network policies support

✅ **High Availability**
- Multiple replicas
- Pod anti-affinity
- Health checks
- Resource management

✅ **Easy Access**
- ClusterIP, NodePort, LoadBalancer services
- Ingress support with TLS
- Internal DNS resolution

✅ **Developer Experience**
- Comprehensive examples
- Quick start guide
- Deployment test script
- Detailed documentation

## 📁 Chart Structure

```
PrismMockServer/
├── Chart.yaml                      # Chart metadata
├── values.yaml                     # Default configuration values
├── README.md                       # Main documentation
├── QUICKSTART.md                   # 5-minute setup guide
├── DEPLOYMENT_GUIDE.md            # Comprehensive deployment guide
├── test-deployment.sh             # Automated test script
├── .helmignore                     # Files to exclude from chart
├── .gitignore                      # Git ignore rules
│
├── templates/                      # Kubernetes manifests
│   ├── deployment.yaml            # Prism deployment
│   ├── service.yaml               # Kubernetes service
│   ├── configmap.yaml             # OpenAPI spec storage
│   ├── ingress.yaml               # Ingress configuration
│   ├── _helpers.tpl               # Helm template helpers
│   └── NOTES.txt                  # Post-install instructions
│
└── examples/                       # Ready-to-use examples
    ├── petstore-values.yaml       # OpenAPI Petstore example
    ├── custom-api-values.yaml     # Custom API example
    ├── production-values.yaml     # Production configuration
    └── nodeport-values.yaml       # NodePort service example
```

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to charts directory
cd /workspace/charts

# 2. Install with default values
helm install my-mock PrismMockServer

# 3. Access the mock server
kubectl port-forward svc/my-mock-prism 8080:80

# 4. Test it
curl http://localhost:8080/health
```

## 📚 Documentation Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](charts/PrismMockServer/README.md) | Main documentation, features, configuration | All users |
| [QUICKSTART.md](charts/PrismMockServer/QUICKSTART.md) | 5-minute setup guide | New users |
| [DEPLOYMENT_GUIDE.md](charts/PrismMockServer/DEPLOYMENT_GUIDE.md) | Comprehensive deployment scenarios | DevOps, Platform Engineers |
| [values.yaml](charts/PrismMockServer/values.yaml) | All configuration options | Advanced users |
| [examples/](charts/PrismMockServer/examples/) | Ready-to-use configurations | All users |

## 🎨 Deployment Scenarios

### 1. Development Environment
```bash
helm install dev-mock PrismMockServer \
  --set service.type=NodePort \
  --set spec.url="https://your-repo.com/api-spec.yaml"
```

### 2. CI/CD Testing
```bash
helm install test-mock PrismMockServer \
  -f examples/custom-api-values.yaml \
  --wait --timeout 2m
```

### 3. QA Environment
```bash
kubectl create configmap qa-specs --from-file=openapi.yaml
helm install qa-mock PrismMockServer \
  --set spec.existingConfigMap=qa-specs
```

### 4. Production Mock Service
```bash
helm install prod-mock PrismMockServer \
  -f examples/production-values.yaml
```

## ⚙️ Key Configuration Options

### OpenAPI Specification Source

**Option 1: Inline (in values.yaml)**
```yaml
spec:
  inline: |
    openapi: 3.0.0
    info:
      title: My API
    paths:
      /users:
        get:
          responses:
            '200':
              description: Success
```

**Option 2: URL**
```yaml
spec:
  url: "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml"
```

**Option 3: ConfigMap**
```yaml
spec:
  existingConfigMap: "my-api-spec"
  configMapKey: "openapi.yaml"
```

### Service Types

**ClusterIP (default)** - Internal cluster access only
```yaml
service:
  type: ClusterIP
  port: 80
```

**NodePort** - Access via Node IP
```yaml
service:
  type: NodePort
  port: 80
  nodePort: 30080
```

**LoadBalancer** - Cloud provider load balancer
```yaml
service:
  type: LoadBalancer
  port: 80
```

**Ingress** - HTTP/HTTPS routing
```yaml
ingress:
  enabled: true
  hosts:
    - host: mock-api.example.com
      paths:
        - path: /
          pathType: Prefix
```

### Prism Options

```yaml
prism:
  options:
    cors: true          # Enable CORS
    validation: true    # Validate requests/responses
    dynamic: false      # Generate random data
    errors: true        # Show detailed errors
```

## 🔧 Installation Methods

### Method 1: Helm Install (Recommended)
```bash
helm install my-mock ./PrismMockServer
```

### Method 2: With Custom Values
```bash
helm install my-mock ./PrismMockServer -f custom-values.yaml
```

### Method 3: With Set Flags
```bash
helm install my-mock ./PrismMockServer \
  --set prism.replicaCount=3 \
  --set service.type=LoadBalancer
```

### Method 4: From Git Repository
```bash
git clone <repo-url>
cd reference-example-components/charts
helm install my-mock ./PrismMockServer
```

## 🧪 Testing Your Deployment

### Automated Test Script
```bash
# Run comprehensive tests
./PrismMockServer/test-deployment.sh my-mock default
```

### Manual Testing
```bash
# Check deployment status
kubectl get pods,svc,ingress -l app=my-mock-prism

# View logs
kubectl logs -l app=my-mock-prism -f

# Test HTTP endpoint
kubectl port-forward svc/my-mock-prism 8080:80
curl http://localhost:8080/
```

## 🌐 Access Patterns

### From Within Kubernetes Cluster
```bash
# Service DNS name
http://my-mock-prism.default.svc.cluster.local

# From any pod in the cluster
curl http://my-mock-prism.default.svc.cluster.local/api/users
```

### From Local Machine (Development)
```bash
# Port-forward
kubectl port-forward svc/my-mock-prism 8080:80

# Access
curl http://localhost:8080/api/users
```

### From External Network (Production)
```bash
# Via Ingress
https://mock-api.example.com/api/users

# Via NodePort
http://<node-ip>:30080/api/users

# Via LoadBalancer
http://<loadbalancer-ip>/api/users
```

## 🎯 Use Cases & Examples

### Use Case 1: Frontend Development
Deploy a mock backend API so frontend developers can work independently:

```bash
helm install backend-mock PrismMockServer \
  --set spec.url="https://github.com/myteam/api-specs/blob/main/backend-v2.yaml" \
  --set service.type=NodePort
```

### Use Case 2: Integration Testing
Mock external APIs in your test environment:

```bash
helm install payment-api-mock PrismMockServer \
  -f payment-api-spec.yaml \
  --namespace testing
```

### Use Case 3: API Validation
Validate that your requests/responses match your OpenAPI spec:

```bash
helm install validation-mock PrismMockServer \
  --set prism.options.validation=true \
  --set prism.options.errors=true
```

### Use Case 4: Demo Environment
Create a reliable demo environment for presentations:

```bash
helm install demo-mock PrismMockServer \
  -f examples/production-values.yaml \
  --set ingress.hosts[0].host=demo-api.company.com
```

## 🔒 Security Features

- ✅ Non-root container (UID 1000)
- ✅ Read-only root filesystem
- ✅ Dropped all capabilities
- ✅ No privilege escalation
- ✅ Security context configured
- ✅ Network policies support
- ✅ TLS/HTTPS via Ingress

## 📊 Production Readiness

### High Availability
- Multiple replicas with pod anti-affinity
- Rolling updates with zero downtime
- Health checks (liveness & readiness probes)

### Resource Management
- CPU and memory limits configured
- Horizontal Pod Autoscaling ready
- Resource requests for scheduling

### Monitoring & Logging
- Structured JSON logging
- Prometheus metrics ready
- Health check endpoints

## 🛠️ Maintenance

### Upgrade Deployment
```bash
helm upgrade my-mock ./PrismMockServer -f new-values.yaml
```

### Update OpenAPI Spec
```bash
# If using ConfigMap
kubectl create configmap my-spec --from-file=openapi.yaml --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/my-mock-prism
```

### Scale Replicas
```bash
helm upgrade my-mock ./PrismMockServer --set prism.replicaCount=5 --reuse-values
```

### Rollback
```bash
helm rollback my-mock
```

### Uninstall
```bash
helm uninstall my-mock
```

## 📈 Monitoring

### View Resource Usage
```bash
kubectl top pods -l app=my-mock-prism
```

### Check Logs
```bash
kubectl logs -l app=my-mock-prism --tail=100 -f
```

### View Events
```bash
kubectl get events --sort-by='.lastTimestamp' | grep prism
```

## 🐛 Troubleshooting

### Pod Not Starting
```bash
kubectl describe pod -l app=my-mock-prism
kubectl logs -l app=my-mock-prism
```

### Service Not Accessible
```bash
kubectl get svc,endpoints -l app=my-mock-prism
```

### Invalid OpenAPI Spec
Validate at: https://editor.swagger.io/

## 💡 Tips & Best Practices

1. **Use URL or ConfigMap in production**, not inline specs
2. **Enable validation** to catch API contract issues
3. **Set appropriate resource limits** based on your load
4. **Use Ingress with TLS** for external access
5. **Deploy in dedicated namespaces** per environment
6. **Version your OpenAPI specs** in Git
7. **Monitor resource usage** and adjust limits
8. **Use network policies** to restrict access
9. **Enable CORS** if needed for web apps
10. **Test in lower environments** before production

## 🔗 Resources

### Official Documentation
- [Prism CLI Documentation](https://docs.stoplight.io/docs/prism/674b27b261c3c-prism-cli)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)

### Tools
- [OpenAPI Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Stoplight Studio](https://stoplight.io/studio)

### Related Projects
- [Prism GitHub](https://github.com/stoplightio/prism)
- [OpenAPI Tools](https://openapi.tools/)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional examples
- Enhanced monitoring integration
- Support for Prism proxy mode
- Additional security policies
- Performance optimizations

## 📝 License

This Helm chart is provided under the MIT License.

## ✨ Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| OpenAPI v2/v3 Support | ✅ | Full support |
| Multiple Spec Sources | ✅ | URL, ConfigMap, Inline |
| High Availability | ✅ | Multi-replica, anti-affinity |
| Security Hardening | ✅ | Non-root, read-only FS |
| Health Checks | ✅ | Liveness & readiness |
| Ingress Support | ✅ | With TLS |
| Resource Limits | ✅ | Configurable |
| CORS Support | ✅ | Enabled by default |
| Request Validation | ✅ | Optional |
| Dynamic Responses | ✅ | Optional |
| Multiple Service Types | ✅ | ClusterIP, NodePort, LB |
| Comprehensive Docs | ✅ | Multiple guides |
| Example Configs | ✅ | 4+ examples |
| Test Script | ✅ | Automated validation |

## 🎉 Conclusion

This Helm chart provides a complete, production-ready solution for deploying Prism Mock Server in Kubernetes. Whether you're developing APIs, testing applications, or providing demo environments, this chart has you covered.

**Quick Start**: See [QUICKSTART.md](charts/PrismMockServer/QUICKSTART.md)

**Need Help?** Check the [README.md](charts/PrismMockServer/README.md) or [DEPLOYMENT_GUIDE.md](charts/PrismMockServer/DEPLOYMENT_GUIDE.md)

---

**Created for**: Kubernetes API mocking and testing
**Maintained by**: DevOps Team
**Last Updated**: November 2025
**Chart Version**: 1.0.0
**Prism Version**: 5.10.0

🚀 **Happy Mocking!**
