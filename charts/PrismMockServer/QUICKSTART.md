# Prism Mock Server - Quick Start Guide

Get your Prism mock server up and running in 5 minutes!

## Prerequisites

- Kubernetes cluster (local or cloud)
- kubectl configured
- Helm 3 installed

## 1. Install with Default Configuration

The quickest way to get started:

```bash
# Install in the default namespace
helm install my-mock ./PrismMockServer

# Or install in a specific namespace
helm install my-mock ./PrismMockServer -n testing --create-namespace
```

This will deploy Prism with a sample OpenAPI specification.

## 2. Test Your Mock Server

```bash
# Port-forward to access locally
kubectl port-forward svc/my-mock-prism 8080:80

# In another terminal, test the mock server
curl http://localhost:8080/health

# Expected response: {"status":"ok"}
```

## 3. Use Your Own API Specification

### Option A: From a URL

```bash
helm install my-mock ./PrismMockServer \
  --set spec.url="https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml" \
  --set spec.inline=""
```

### Option B: Using a values file

Create `my-api.yaml`:

```yaml
spec:
  inline: |
    openapi: 3.0.0
    info:
      title: My API
      version: 1.0.0
    paths:
      /hello:
        get:
          responses:
            '200':
              description: Success
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
                        example: "Hello, World!"
```

Install:

```bash
helm install my-mock ./PrismMockServer -f my-api.yaml
```

## 4. Access from Other Pods

Your mock server is accessible at:

```
http://my-mock-prism.<namespace>.svc.cluster.local
```

Example from another pod:

```bash
kubectl run test-pod --image=curlimages/curl -it --rm -- \
  curl http://my-mock-prism.default.svc.cluster.local/hello
```

## 5. Enable External Access

### Using NodePort:

```bash
helm install my-mock ./PrismMockServer \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

Access via: `http://<node-ip>:30080`

### Using Ingress:

```bash
helm install my-mock ./PrismMockServer \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mock.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

## 6. Using Pre-built Examples

We provide several example configurations:

```bash
# Petstore API
helm install petstore-mock ./PrismMockServer -f examples/petstore-values.yaml

# Custom E-Commerce API
helm install ecommerce-mock ./PrismMockServer -f examples/custom-api-values.yaml

# Production configuration
helm install prod-mock ./PrismMockServer -f examples/production-values.yaml

# NodePort configuration
helm install external-mock ./PrismMockServer -f examples/nodeport-values.yaml
```

## 7. Common Commands

```bash
# Check deployment status
helm status my-mock

# View pod logs
kubectl logs -l app=my-mock-prism -f

# Get service details
kubectl get svc my-mock-prism

# Upgrade deployment
helm upgrade my-mock ./PrismMockServer -f my-values.yaml

# Uninstall
helm uninstall my-mock
```

## 8. Troubleshooting

### Pod not starting?

```bash
# Check pod status and events
kubectl describe pod -l app=my-mock-prism

# View logs
kubectl logs -l app=my-mock-prism
```

### Can't access the service?

```bash
# Verify service and endpoints
kubectl get svc,endpoints -l app=my-mock-prism

# Test from within cluster
kubectl run test --image=curlimages/curl -it --rm -- \
  curl http://my-mock-prism.default.svc.cluster.local/
```

### Invalid OpenAPI spec?

Validate your OpenAPI specification at:
- https://editor.swagger.io/
- https://apitools.dev/swagger-parser/online/

## Next Steps

- Read the full [README.md](README.md) for advanced configuration
- Explore the [examples/](examples/) directory for more use cases
- Check out [Prism documentation](https://docs.stoplight.io/docs/prism)

## Quick Tips

1. **Dynamic Responses**: Set `prism.options.dynamic=true` for random data
2. **CORS**: Enabled by default, disable with `prism.options.cors=false`
3. **Validation**: Request/response validation is enabled by default
4. **Multiple Mocks**: Deploy multiple instances with different release names
5. **CI/CD**: Use `spec.url` to point to specs in your repo

## Example: Complete Development Setup

```bash
# Create namespace
kubectl create namespace dev-team

# Deploy mock server
helm install backend-mock ./PrismMockServer \
  --namespace dev-team \
  --set spec.url="https://github.com/myteam/api-specs/blob/main/backend-api.yaml" \
  --set service.type=NodePort \
  --set service.nodePort=30100 \
  --set prism.options.cors=true \
  --set prism.options.validation=true

# Get connection info
echo "Mock server available at: http://$(minikube ip):30100"
```

Happy Mocking! 🎉
