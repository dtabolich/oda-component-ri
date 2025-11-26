# WireMock Helm Chart

This Helm chart deploys WireMock, a flexible HTTP mock server for testing and development.

## Features

- Advanced request matching
- Response templating
- Stateful scenarios
- Admin API for runtime configuration
- Persistent stub mappings via ConfigMaps

## Installation

```bash
# Basic installation
helm install my-wiremock ./WireMock

# With custom mappings
helm install my-wiremock ./WireMock -f custom-values.yaml
```

## Configuration Example

```yaml
mappings:
  - request:
      method: GET
      url: /api/users
    response:
      status: 200
      jsonBody:
        users:
          - id: 1
            name: John Doe
          - id: 2
            name: Jane Smith
  
  - request:
      method: POST
      url: /api/users
    response:
      status: 201
      jsonBody:
        id: 3
        name: New User

files:
  large-response.json: |
    {
      "data": "Large response body here"
    }
```

## Access

```bash
# Port-forward
kubectl port-forward svc/my-wiremock-wiremock 8080:8080

# Test endpoint
curl http://localhost:8080/api/users

# Admin API
curl http://localhost:8080/__admin/mappings
```

## Resources

- [WireMock Documentation](https://wiremock.org/docs/)
- [Request Matching](https://wiremock.org/docs/request-matching/)
- [Response Templating](https://wiremock.org/docs/response-templating/)
