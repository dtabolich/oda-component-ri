# API Mocking Tools for Kubernetes - Quick Reference Guide

A quick reference for choosing the right API mocking tool for your Kubernetes deployment.

## Quick Decision Tree

```
Need multi-protocol support (gRPC, GraphQL)?
├─ Yes → Microcks or Imposter
└─ No → Continue...

Need complex stateful scenarios?
├─ Yes → WireMock or MockServer
└─ No → Continue...

Need OpenAPI validation?
├─ Yes → Prism or Microcks
└─ No → Continue...

Need simple REST mocking?
├─ Yes → JSON Server or Mockoon
└─ No → Continue...

Need enterprise features (UI, catalog, governance)?
├─ Yes → Microcks
└─ No → Prism or WireMock
```

## One-Line Summaries

| Tool | One-Line Description | When to Use |
|------|---------------------|-------------|
| **Prism** | OpenAPI-first validation and mocking | OpenAPI contracts, frontend dev, CI/CD |
| **WireMock** | Flexible stubbing with advanced matching | Complex test scenarios, stateful mocks |
| **Mockoon** | Developer-friendly with GUI and CLI | Rapid prototyping, easy setup |
| **MockServer** | Comprehensive mocking + verification | Integration testing, proxy mode |
| **Microcks** | Enterprise API management platform | Multi-protocol, API catalog, governance |
| **Hoverfly** | Service virtualization with capture/replay | Performance testing, traffic simulation |
| **Mountebank** | Multi-protocol test doubles | HTTP/TCP/SMTP mocking |
| **Imposter** | Scriptable mock with plugins | Custom logic, dynamic responses |
| **JSON Server** | Zero-config REST API from JSON | Quick demos, hackathons |

## Installation Commands

```bash
# Prism (using our chart)
helm install my-mock ./PrismMockServer

# WireMock (using our chart)
helm install my-mock ./WireMock

# Microcks (official chart)
helm repo add microcks https://microcks.io/helm
helm install microcks microcks/microcks -n microcks --create-namespace

# Mockoon (kubectl)
kubectl create deployment mockoon --image=mockoon/cli:latest

# MockServer (kubectl)
kubectl create deployment mockserver --image=mockserver/mockserver:latest

# JSON Server (kubectl)
kubectl create deployment json-server --image=clue/json-server:latest
```

## Feature Matrix (Visual)

```
Feature               Prism  WireMock  Mockoon  MockServer  Microcks
─────────────────────────────────────────────────────────────────────
OpenAPI Support       ████   ██        ████     ████        ████
State Management      ░░░░   ████      ███      ████        ████
Admin UI              ░░░░   ████      ████     ████        ████
Multi-protocol        ░░░░   ░░░░      ░░░░     ░░░░        ████
Contract Testing      ███    ██        ░░░░     ███         ████
Resource Usage (Low)  ████   ███       ███      ██          ░░░░
Setup Speed           ████   ███       ████     ███         ██
Enterprise Features   ██     ███       ██       ███         ████
```

Legend: ████ Excellent | ███ Good | ██ Fair | ░░░░ None/Poor

## Resource Requirements

```
Tool          Memory    CPU      Startup   Image Size
─────────────────────────────────────────────────────
Prism         ~50MB     Low      <1s       ~20MB
WireMock      ~100MB    Low      2-3s      ~100MB
Mockoon       ~80MB     Low      ~1s       ~150MB
MockServer    ~150MB    Medium   3-5s      ~200MB
Microcks      ~500MB+   Medium   ~30s      ~300MB+
JSON Server   ~30MB     Low      <1s       ~50MB
```

## Use Case Matrix

| Use Case | Best Tool | Alternative |
|----------|-----------|-------------|
| Frontend Development | Prism, Mockoon | JSON Server |
| OpenAPI Contract Testing | Prism, Microcks | Specmatic |
| Complex Integration Tests | WireMock, MockServer | Mountebank |
| Multi-Protocol Mocking | Microcks | Imposter |
| Service Virtualization | Hoverfly, MockServer | WireMock |
| CI/CD Fast Tests | Prism, Mockoon | JSON Server |
| Enterprise API Management | Microcks | - |
| Quick Prototypes | JSON Server, Mockoon | Prism |
| gRPC Mocking | Microcks, Imposter | - |
| GraphQL Mocking | Microcks | MockServer |
| AsyncAPI/Kafka | Microcks | - |

## Cost of Ownership

```
Factor            Prism  WireMock  Mockoon  MockServer  Microcks
──────────────────────────────────────────────────────────────────
Learning Curve    Low    Medium    Low      Medium      High
Maintenance       Low    Low       Low      Medium      Medium
Infrastructure    Low    Low       Low      Medium      High
Documentation     Good   Excellent Good     Excellent   Good
Community         Good   Excellent Good     Good        Growing
```

## Deployment Patterns

### Pattern 1: Simple Dev Environment
```yaml
# Use: Prism or Mockoon
Resources: Minimal (50-100MB)
Setup: 5 minutes
Best for: 1-5 developers
```

### Pattern 2: CI/CD Testing
```yaml
# Use: Prism or WireMock
Resources: Medium (100-200MB)
Setup: 10 minutes
Best for: Automated pipelines
```

### Pattern 3: QA Environment
```yaml
# Use: WireMock or MockServer
Resources: Medium (200-400MB)
Setup: 15 minutes
Best for: QA team testing
```

### Pattern 4: Enterprise Platform
```yaml
# Use: Microcks
Resources: High (500MB-1GB)
Setup: 30 minutes
Best for: Multiple teams, API catalog
```

## Side-by-Side Deployment

You can run multiple tools together:

```yaml
# Prism for OpenAPI validation
- Service: prism-mock:80
  Use: Contract validation

# WireMock for complex scenarios  
- Service: wiremock-mock:8080
  Use: Stateful testing

# JSON Server for quick prototypes
- Service: json-server:80
  Use: Rapid prototyping
```

## Kubernetes Deployment Comparison

| Aspect | Prism | WireMock | Microcks |
|--------|-------|----------|----------|
| Pod Count | 1 | 1 | 3-5 |
| Dependencies | None | None | MongoDB, Keycloak |
| ConfigMap Usage | 1 (spec) | 1-2 (mappings) | Multiple |
| PV Required | No | No | Yes (prod) |
| Ingress | Optional | Optional | Recommended |
| Service Mesh | Compatible | Compatible | Compatible |

## Migration Paths

### From Prism to WireMock
**Reason**: Need state management
**Effort**: Medium (rewrite specs to mappings)

### From WireMock to Microcks
**Reason**: Need multi-protocol + UI
**Effort**: High (infrastructure + data migration)

### From JSON Server to Prism
**Reason**: Need OpenAPI validation
**Effort**: Low (create OpenAPI from JSON)

### From Any to Microcks
**Reason**: Enterprise requirements
**Effort**: High (full platform setup)

## Community and Support

| Tool | GitHub Stars | Last Update | Releases/Year | Enterprise Support |
|------|--------------|-------------|---------------|-------------------|
| Prism | 4k+ | Active | 12+ | Stoplight |
| WireMock | 6k+ | Very Active | 6+ | Yes |
| Mockoon | 5k+ | Active | 12+ | No |
| MockServer | 4k+ | Active | 6+ | Yes |
| Microcks | 1k+ | Active | 4+ | Limited |

## Final Recommendations

### For Startups/Small Teams
**Choose**: Prism or Mockoon
- Fast setup
- Low resources
- Easy to learn

### For Medium Companies
**Choose**: WireMock or MockServer
- Balance of features
- Good scalability
- Community support

### For Enterprises
**Choose**: Microcks
- Full API lifecycle
- Multi-protocol
- Governance features

### For Specific Protocols
- **REST only**: Any tool
- **REST + gRPC**: Microcks or Imposter
- **REST + GraphQL**: Microcks or MockServer
- **REST + AsyncAPI**: Microcks
- **Multi-protocol**: Microcks

## Quick Start Commands

```bash
# Try Prism (fastest)
kubectl run prism --image=stoplight/prism:5 \
  --port=4010 \
  -- mock -h 0.0.0.0 https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml

kubectl port-forward prism 4010:4010

# Try WireMock
kubectl run wiremock --image=wiremock/wiremock:3.3.1 --port=8080
kubectl port-forward wiremock 8080:8080

# Try Microcks (requires more setup)
helm repo add microcks https://microcks.io/helm
helm install microcks microcks/microcks -n microcks --create-namespace
```

## Performance Benchmarks (Approximate)

```
Tool          Requests/sec  Latency (p95)  Memory Usage
──────────────────────────────────────────────────────
Prism         2000+         <10ms          50MB
WireMock      5000+         <5ms           100MB
MockServer    4000+         <8ms           150MB
Microcks      3000+         <15ms          500MB
JSON Server   3000+         <5ms           30MB
```

## Summary Table

| Priority | Simple Projects | Medium Projects | Enterprise |
|----------|----------------|-----------------|------------|
| 🥇 | Prism | WireMock | Microcks |
| 🥈 | Mockoon | MockServer | - |
| 🥉 | JSON Server | Prism | WireMock |

---

**Last Updated**: November 2025
**Available Charts**: `/workspace/charts/PrismMockServer`, `/workspace/charts/WireMock`
**Full Comparison**: See `/workspace/API_MOCKING_TOOLS_COMPARISON.md`
