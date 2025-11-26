# Prism Mock Server Helm Chart

This Helm chart deploys [Stoplight Prism](https://stoplight.io/open-source/prism), a powerful HTTP mock server that can simulate APIs based on OpenAPI v2/v3 specifications.

## Features

- 🚀 Easy deployment of Prism mock server in Kubernetes
- 📝 Flexible OpenAPI specification management (inline, URL, or ConfigMap)
- 🔒 Security-hardened with non-root containers and read-only filesystem
- 📊 Built-in health checks and monitoring
- 🌐 Optional Ingress support
- ⚙️ Highly configurable via values.yaml

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+

## Installation

### Quick Start

Install the chart with default values (includes a sample OpenAPI spec):

```bash
helm install my-mock-server ./PrismMockServer -n default
```

### Custom Installation Examples

#### 1. Using an Inline OpenAPI Specification

Create a `custom-values.yaml`:

```yaml
spec:
  inline: |
    openapi: 3.0.0
    info:
      title: My API
      version: 1.0.0
    servers:
      - url: https://api.example.com
    paths:
      /users:
        get:
          summary: Get all users
          responses:
            '200':
              description: Successful response
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
                        email:
                          type: string
      /users/{id}:
        get:
          summary: Get user by ID
          parameters:
            - name: id
              in: path
              required: true
              schema:
                type: integer
          responses:
            '200':
              description: Successful response
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      email:
                        type: string
```

Install:

```bash
helm install my-api-mock ./PrismMockServer -f custom-values.yaml -n default
```

#### 2. Using an OpenAPI Spec from a URL

```yaml
spec:
  url: "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml"
```

Install:

```bash
helm install petstore-mock ./PrismMockServer -f custom-values.yaml -n default
```

#### 3. Using an Existing ConfigMap

First, create a ConfigMap with your OpenAPI spec:

```bash
kubectl create configmap my-openapi-spec \
  --from-file=openapi.yaml=./path/to/your/openapi.yaml \
  -n default
```

Then install with:

```yaml
spec:
  existingConfigMap: "my-openapi-spec"
  configMapKey: "openapi.yaml"
```

#### 4. With Ingress Enabled

```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: mock-api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mock-api-tls
      hosts:
        - mock-api.example.com

service:
  type: ClusterIP
```

#### 5. With NodePort Service

```yaml
service:
  type: NodePort
  port: 80
  nodePort: 30080
```

#### 6. Production-Ready Configuration

```yaml
prism:
  replicaCount: 3
  options:
    cors: true
    validation: true
    errors: true

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

## Configuration

### Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `prism.image` | Prism Docker image | `stoplight/prism:5` |
| `prism.replicaCount` | Number of replicas | `1` |
| `prism.port` | Port where Prism listens | `4010` |
| `prism.options.cors` | Enable CORS | `true` |
| `prism.options.dynamic` | Enable dynamic response generation | `false` |
| `prism.options.validation` | Enable request/response validation | `true` |
| `spec.url` | URL to OpenAPI spec | `""` |
| `spec.inline` | Inline OpenAPI spec | Sample spec |
| `spec.existingConfigMap` | Use existing ConfigMap | `""` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `ingress.enabled` | Enable ingress | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

For a complete list of configuration options, see [values.yaml](values.yaml).

## Accessing the Mock Server

### From within the cluster:

```bash
# Get the service name
kubectl get svc -l app=<release-name>-prism

# Access via service DNS
curl http://<release-name>-prism.<namespace>.svc.cluster.local/your-endpoint
```

### Using port-forward:

```bash
kubectl port-forward svc/<release-name>-prism 8080:80 -n default

# Then access locally
curl http://localhost:8080/your-endpoint
```

### Using NodePort:

```bash
# Get the node port
kubectl get svc <release-name>-prism -n default

# Access via node IP and port
curl http://<node-ip>:<node-port>/your-endpoint
```

### Using Ingress:

Access via the configured hostname (e.g., `http://mock-api.example.com/your-endpoint`)

## Testing Your Mock Server

Once deployed, you can test it:

```bash
# Port-forward to local machine
kubectl port-forward svc/<release-name>-prism 8080:80 -n default

# Test the health endpoint (from the default spec)
curl http://localhost:8080/health

# Response:
# {"status":"ok"}
```

## Prism Command Line Options

This chart supports the following Prism options via `values.yaml`:

- `cors`: Enable CORS headers
- `dynamic`: Generate random dynamic response data
- `validation`: Validate requests/responses against the spec
- `errors`: Show detailed error messages
- `host`: Host to bind to (default: 0.0.0.0)

For more details on Prism CLI options, see the [official documentation](https://docs.stoplight.io/docs/prism/674b27b261c3c-prism-cli).

## Upgrading

To upgrade an existing release:

```bash
helm upgrade my-mock-server ./PrismMockServer -f custom-values.yaml -n default
```

## Uninstalling

To uninstall/delete the deployment:

```bash
helm uninstall my-mock-server -n default
```

This will remove all Kubernetes resources associated with the chart.

## Advanced Use Cases

### Multiple Mock Servers

You can deploy multiple instances of Prism with different OpenAPI specs:

```bash
# Deploy first mock server
helm install api-v1-mock ./PrismMockServer -f api-v1-spec.yaml -n default

# Deploy second mock server
helm install api-v2-mock ./PrismMockServer -f api-v2-spec.yaml -n default
```

### Integration Testing

Use Prism mock servers in your CI/CD pipeline for integration testing:

```yaml
# ci-values.yaml
prism:
  replicaCount: 1
resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

### Development Environment

Deploy mock servers for each developer:

```bash
helm install dev-${USER}-mock ./PrismMockServer \
  --set spec.url=https://github.com/myorg/api-specs/blob/main/openapi.yaml \
  -n dev-${USER}
```

## Troubleshooting

### Check pod status:

```bash
kubectl get pods -l app=<release-name>-prism -n default
```

### View pod logs:

```bash
kubectl logs -l app=<release-name>-prism -n default
```

### Describe pod for events:

```bash
kubectl describe pod <pod-name> -n default
```

### Common Issues:

1. **Pod not starting**: Check if the OpenAPI spec is valid
   ```bash
   kubectl logs <pod-name> -n default
   ```

2. **Service not accessible**: Verify service and endpoints
   ```bash
   kubectl get svc,endpoints -l app=<release-name>-prism -n default
   ```

3. **Invalid OpenAPI spec**: Validate your spec at https://editor.swagger.io/

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This Helm chart is provided as-is under the MIT License.

## Resources

- [Prism Documentation](https://docs.stoplight.io/docs/prism)
- [Prism GitHub Repository](https://github.com/stoplightio/prism)
- [OpenAPI Specification](https://www.openapis.org/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Helm Documentation](https://helm.sh/docs/)
