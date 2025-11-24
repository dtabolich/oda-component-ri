# IAM Comparison: Ory Kratos vs WSO2 Identity Server
## For MACH Architecture & TM Forum ODA Digital Ecosystem

**Date**: 2025-11-24  
**Context**: Evaluating IAM solutions for a cloud-native, microservices-based digital ecosystem using TM Forum ODA components

---

## Executive Summary

| Aspect | Ory Kratos | WSO2 Identity Server |
|--------|------------|---------------------|
| **MACH Alignment** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| **Cloud-Native** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Adaptable |
| **Microservices Fit** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐ Moderate |
| **API-First** | ⭐⭐⭐⭐⭐ Pure API | ⭐⭐⭐⭐ Strong |
| **Kubernetes Ready** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Requires work |
| **Learning Curve** | ⭐⭐⭐⭐ Low | ⭐⭐ Steep |
| **Enterprise Features** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Comprehensive |

---

## 1. MACH Architecture Alignment

### **M**icroservices-based

#### Ory Kratos ✅
- **Architecture**: Single-purpose microservice focused solely on identity management
- **Container-first**: Docker images < 20MB (distroless)
- **Stateless**: Can be horizontally scaled without session affinity
- **Database agnostic**: Supports PostgreSQL, MySQL, CockroachDB, SQLite
- **Sidecar pattern**: Works well with service mesh (Istio, Linkerd)
- **Perfect fit**: Designed from ground up for microservices

#### WSO2 Identity Server ⚠️
- **Architecture**: Monolithic Java application (can be componentized)
- **Size**: Heavier footprint (~500MB+ Docker image)
- **Modular**: Can decompose into smaller services with effort
- **State management**: Session clustering required for HA
- **Better for**: Traditional enterprise or hybrid architectures

---

### **A**PI-first

#### Ory Kratos ✅
- **Pure API-first**: No UI included (headless by design)
- **REST APIs**: Complete OpenAPI/Swagger specifications
- **API categories**:
  - Public APIs (registration, login, recovery)
  - Admin APIs (user management, identity schemas)
- **SDK Support**: Official SDKs for Go, TypeScript/JavaScript, PHP, Python, Rust
- **Versioned APIs**: Clear API versioning strategy
- **Integration**: Perfect for SPA, mobile apps, and backend services

#### WSO2 Identity Server ✅
- **Strong API support**: Comprehensive REST APIs
- **SCIM 2.0**: Full user/group management APIs
- **OAuth 2.0/OIDC**: Complete implementation
- **Admin APIs**: Extensive configuration APIs
- **SOAP APIs**: Legacy support (may be overhead)
- **Management console**: Built-in UI (not required, can be disabled)

**Winner**: Ory Kratos (true headless, no UI baggage)

---

### **C**loud-native SaaS

#### Ory Kratos ✅
- **Kubernetes-native**: Helm charts, StatefulSets, operators
- **12-factor app**: Follows all principles
- **Configuration**: Environment variables + config files
- **Observability**: 
  - Prometheus metrics out-of-box
  - Distributed tracing (OpenTelemetry)
  - Structured logging (JSON)
- **Health checks**: Kubernetes-ready liveness/readiness probes
- **Zero-downtime updates**: Rolling updates supported
- **Multi-tenancy**: Achievable via deployment isolation

#### WSO2 Identity Server ⚠️
- **Cloud adaptation**: Can run in containers, requires tuning
- **Kubernetes**: Helm charts available but more complex
- **Configuration**: XML-heavy configuration (less cloud-native)
- **Observability**: Available but requires more setup
- **Startup time**: Slower (JVM-based)
- **Resource usage**: Higher memory footprint
- **Multi-tenancy**: Built-in (better for SaaS providers)

**Winner**: Ory Kratos (born in the cloud)

---

### **H**eadless

#### Ory Kratos ✅
- **Truly headless**: Zero UI components
- **Self-service flows**: API-driven (registration, login, recovery, verification, settings)
- **Frontend freedom**: Build UI in any framework (React, Vue, Angular, mobile)
- **Customization**: Complete control over UX/UI
- **Consistency**: Your brand, your design system
- **Perfect for**: Modern SPAs and mobile apps

#### WSO2 Identity Server ❌
- **Traditional approach**: Built-in UIs and management console
- **Customization**: JSP-based UI customization (dated)
- **Theming**: Possible but limited
- **Not truly headless**: Can expose APIs but designed with UI-first approach
- **Better for**: Organizations wanting out-of-box UI

**Winner**: Ory Kratos (pure headless philosophy)

---

## 2. Authentication & Authorization Features

### Authentication Methods

| Feature | Ory Kratos | WSO2 IS |
|---------|------------|---------|
| **Password-based** | ✅ Yes | ✅ Yes |
| **Passwordless** | ✅ Yes (WebAuthn, Magic Links) | ✅ Yes |
| **Social Login** | ✅ Via OIDC | ✅ Yes (20+ providers) |
| **Multi-factor Auth (MFA)** | ⚠️ Limited (TOTP via Ory Hydra) | ✅ Comprehensive (TOTP, SMS, Email, FIDO2) |
| **Biometric** | ✅ WebAuthn/FIDO2 | ✅ Yes |
| **Risk-based Auth** | ❌ No | ✅ Yes (Adaptive auth) |
| **Device Trust** | ⚠️ Basic | ✅ Advanced |

### Identity Management

| Feature | Ory Kratos | WSO2 IS |
|---------|------------|---------|
| **User Registration** | ✅ Flexible schemas | ✅ Yes |
| **Self-service flows** | ✅ Excellent | ✅ Good |
| **Email/Phone verification** | ✅ Yes | ✅ Yes |
| **Account recovery** | ✅ Yes | ✅ Yes |
| **Profile management** | ✅ Yes | ✅ Yes |
| **Identity schema flexibility** | ✅ JSON Schema | ⚠️ Fixed + extensions |
| **Custom attributes** | ✅ Unlimited | ✅ Limited |

### Session Management

| Feature | Ory Kratos | WSO2 IS |
|---------|------------|---------|
| **Session handling** | ✅ Cookie-based | ✅ Multiple options |
| **JWT support** | ⚠️ Via Ory Hydra | ✅ Native |
| **Session lifetime** | ✅ Configurable | ✅ Configurable |
| **Revocation** | ✅ Yes | ✅ Yes |
| **Single Sign-On (SSO)** | ⚠️ Limited (needs Ory Hydra) | ✅ Comprehensive |

### Standards Compliance

| Standard | Ory Kratos | WSO2 IS |
|----------|------------|---------|
| **OAuth 2.0** | ❌ (Use Ory Hydra) | ✅ Full |
| **OpenID Connect** | ❌ (Use Ory Hydra) | ✅ Certified |
| **SAML 2.0** | ❌ | ✅ Yes |
| **WS-Federation** | ❌ | ✅ Yes |
| **SCIM 2.0** | ❌ | ✅ Yes |
| **WebAuthn/FIDO2** | ✅ Yes | ✅ Yes |

---

## 3. Authorization & Access Control

### Ory Kratos ⚠️
- **Focus**: Authentication only
- **Authorization**: Not included (use Ory Keto separately)
- **RBAC**: Not built-in
- **ABAC**: Not built-in
- **Permissions**: External solution required
- **Architecture**: Separation of concerns (auth vs authz)

### WSO2 Identity Server ✅
- **Focus**: Complete IAM (authn + authz)
- **Authorization**: Built-in
- **RBAC**: Yes (Role-Based Access Control)
- **ABAC**: Yes (Attribute-Based Access Control)
- **XACML**: Full XACML 3.0 engine
- **Fine-grained**: Policy-based access control
- **Scopes**: OAuth 2.0 scope management

**Winner**: WSO2 IS (if you need integrated authz)

---

## 4. Integration & Extensibility

### Ory Kratos

**Pros:**
- **Webhooks**: Pre/post hooks for all flows
- **Identity schemas**: JSON Schema-based, fully customizable
- **Courier**: Template-based email/SMS notifications
- **Admin API**: Programmatic control over everything
- **Database**: Direct access for custom queries
- **SDKs**: High-quality, auto-generated
- **Open source**: Modify anything if needed

**Cons:**
- Smaller ecosystem compared to WSO2
- Fewer pre-built integrations
- More DIY for complex scenarios

### WSO2 Identity Server

**Pros:**
- **Extensions**: Rich extension framework (Java-based)
- **Connectors**: 20+ identity providers pre-configured
- **Provisioning**: SCIM, SPML, Just-In-Time provisioning
- **User stores**: LDAP, AD, JDBC, custom
- **Event handlers**: Extensive lifecycle hooks
- **Workflow engine**: BPEL-based approval workflows
- **Large ecosystem**: Many pre-built integrations

**Cons:**
- Java/OSGi expertise required for extensions
- Heavier customization process
- Longer development cycles

---

## 5. Developer Experience

### Ory Kratos ✅

**Pros:**
- **Documentation**: Excellent, modern docs
- **Examples**: Rich example repository
- **CLI**: Powerful CLI tool (`kratos`)
- **Local development**: Quick Docker Compose setup
- **API design**: Intuitive, RESTful
- **Error handling**: Clear, actionable error messages
- **Community**: Active, responsive community
- **Learning curve**: Gentle for modern developers

**Cons:**
- Requires understanding of multiple Ory services
- Less enterprise support resources

### WSO2 Identity Server ⚠️

**Pros:**
- **Documentation**: Comprehensive but dense
- **Enterprise support**: Commercial support available
- **Tutorials**: Many available
- **Community**: Large, established

**Cons:**
- **Complexity**: Steeper learning curve
- **Setup**: More complex initial setup
- **Documentation**: Can be overwhelming
- **Modern tools**: Less aligned with cloud-native DX
- **XML configuration**: Less developer-friendly

---

## 6. Performance & Scalability

### Ory Kratos ✅

- **Throughput**: 10,000+ req/s (single instance)
- **Latency**: <10ms (typical)
- **Memory**: ~50-100MB per instance
- **Horizontal scaling**: Linear, stateless
- **Database**: Main bottleneck (use read replicas)
- **Connection pooling**: Efficient
- **Caching**: Minimal state, fast

### WSO2 Identity Server ⚠️

- **Throughput**: 1,000-5,000 req/s (needs tuning)
- **Latency**: ~50-100ms (JVM overhead)
- **Memory**: ~1-2GB per instance (JVM heap)
- **Horizontal scaling**: Requires session clustering
- **Startup time**: 20-60 seconds
- **JVM tuning**: Requires expertise
- **Better for**: Large enterprises with ops teams

---

## 7. Operational Considerations

### Deployment

| Aspect | Ory Kratos | WSO2 IS |
|--------|------------|---------|
| **Container size** | 15-20MB | 500MB+ |
| **Startup time** | <1 second | 20-60 seconds |
| **Configuration** | ENV vars + YAML | XML files + ENV vars |
| **Secrets management** | K8s secrets, Vault | Multiple options |
| **HA setup** | Simple (stateless) | Complex (clustering) |
| **Rolling updates** | Easy | Requires care |

### Monitoring & Observability

| Aspect | Ory Kratos | WSO2 IS |
|--------|------------|---------|
| **Metrics** | Prometheus (native) | JMX, Prometheus (plugin) |
| **Tracing** | OpenTelemetry | OpenTelemetry (setup needed) |
| **Logging** | JSON structured | Log4j2 |
| **Health checks** | Built-in | Available |
| **Dashboards** | Grafana templates | Pre-built options |

### Backup & Disaster Recovery

| Aspect | Ory Kratos | WSO2 IS |
|--------|------------|---------|
| **State storage** | Database only | Database + filesystem |
| **Backup** | Standard DB backup | DB + config files |
| **Recovery** | Straightforward | More complex |
| **Data migration** | SQL scripts | WSO2 tooling |

---

## 8. Security Features

### Ory Kratos ✅

- **Password policies**: Configurable (breach detection)
- **Breach detection**: HaveIBeenPwned integration
- **Rate limiting**: Built-in
- **CSRF protection**: Yes
- **Account enumeration**: Protected
- **Secure defaults**: Yes
- **Encryption**: At rest (DB), in transit (TLS)
- **Secrets management**: External (Vault recommended)
- **Security audits**: Regular (open source)

### WSO2 Identity Server ✅

- **All above features**: Yes
- **Advanced threat detection**: Yes
- **Anomaly detection**: Yes
- **Bot detection**: Yes
- **Account locking**: Advanced policies
- **Password policies**: Highly configurable
- **Compliance**: PCI-DSS, SOC2, ISO27001
- **Security certifications**: Multiple

---

## 9. Cost Considerations

### Ory Kratos

**Open Source (Apache 2.0)**
- Free to use, modify, distribute
- No licensing fees
- Infrastructure costs only

**Ory Network (Managed)**
- Pay-as-you-go pricing
- ~$0.50 per 1000 monthly active users
- Includes Kratos + Hydra + Keto
- Free tier available

**Hidden Costs:**
- Development time (building UI)
- Operations (self-hosting)
- Learning curve

### WSO2 Identity Server

**Open Source (Apache 2.0)**
- Free to use
- Community support only
- Infrastructure costs

**WSO2 Identity Server (Commercial)**
- Subscription-based
- ~$3-10 per user/year (volume pricing)
- Enterprise support included
- Updates and patches
- Typically $25K-$100K+ annually

**Hidden Costs:**
- Higher infrastructure costs
- DevOps complexity
- Java/WSO2 expertise

---

## 10. Compliance & Governance

### Ory Kratos ⚠️

- **GDPR**: Data portability, right to erasure (implement yourself)
- **CCPA**: Similar to GDPR
- **Audit logs**: Basic (enhance with external tools)
- **Data residency**: Control via deployment
- **Consent management**: Custom implementation
- **Privacy**: Built with privacy-first principles

### WSO2 Identity Server ✅

- **GDPR**: Built-in compliance toolkit
- **CCPA**: Supported
- **Audit logs**: Comprehensive
- **Consent management**: Built-in framework
- **Data residency**: Configurable
- **Compliance reports**: Available
- **Privacy by design**: Yes

---

## 11. Ecosystem & Stack Integration

### Your Current Stack (TM Forum ODA)

**Current Architecture:**
- ✅ Kubernetes/Helm
- ✅ Microservices (Node.js)
- ✅ MongoDB
- ✅ TMF Open APIs
- ✅ JWT bearer tokens
- ✅ Event-driven

### Integration with Ory Kratos ✅

**Perfect Fit:**
- **Kubernetes**: Native support, Helm charts
- **Microservices**: Sidecar or standalone service
- **Node.js**: Official TypeScript SDK
- **JWT**: Via Ory Hydra (OAuth2/OIDC)
- **TMF APIs**: Protect with JWT middleware
- **Events**: Webhooks for identity events
- **MongoDB**: Not directly (Kratos uses SQL) - use Postgres

**Architecture:**
```
[Frontend] → [API Gateway] → [TMF APIs]
               ↓                   ↓
          [Ory Kratos]      [JWT Validation]
          [Ory Hydra]
               ↓
          [PostgreSQL]
```

### Integration with WSO2 IS ⚠️

**Requires Adaptation:**
- **Kubernetes**: Possible but heavier
- **Microservices**: Acts as monolith
- **Node.js**: REST APIs (no official SDK)
- **JWT**: Native support
- **TMF APIs**: Standard OAuth2 integration
- **Events**: Event handlers available
- **MongoDB**: Separate identity DB (SQL required)

**Architecture:**
```
[Frontend] → [API Gateway] → [TMF APIs]
               ↓                   ↓
          [WSO2 IS]        [JWT Validation]
          (Monolith)
               ↓
          [MySQL/PostgreSQL]
```

---

## 12. Use Case Suitability

### Choose Ory Kratos if:

✅ **MUST HAVE:**
- MACH architecture is non-negotiable
- Cloud-native, Kubernetes-first deployment
- Microservices architecture
- Modern tech stack (Go, Node.js, React)
- Headless/API-first requirement
- Small to medium user base (<1M users)
- Developer-friendly experience priority

✅ **NICE TO HAVE:**
- Full control over UI/UX
- Lightweight footprint
- Fast deployment cycles
- Modern DevOps practices
- Open source flexibility
- Cost optimization

❌ **DEAL BREAKERS:**
- Need comprehensive authorization (add Ory Keto)
- Need federation (SAML, WS-Fed) (add Ory Hydra with extensions)
- Need enterprise workflow engine
- Legacy integration requirements
- Large enterprise with existing WSO2 investments

### Choose WSO2 Identity Server if:

✅ **MUST HAVE:**
- Comprehensive IAM features out-of-box
- Enterprise federation (SAML, WS-Fed, Kerberos)
- Complex authorization requirements (XACML)
- Extensive compliance requirements
- Large enterprise (1M+ users)
- Existing Java/WSO2 ecosystem
- Built-in UI acceptable
- Need commercial support

✅ **NICE TO HAVE:**
- Workflow engine for approvals
- Many pre-built connectors
- Risk-based authentication
- User store federation (LDAP/AD)
- Mature product (10+ years)

❌ **DEAL BREAKERS:**
- MACH architecture is priority
- Kubernetes-native is critical
- Microservices-first approach
- Need lightweight services
- Limited ops resources
- Avoid JVM stack

---

## 13. Migration & Integration Path

### If You Choose Ory Kratos

**Phase 1: Foundation (Weeks 1-2)**
1. Deploy Ory Kratos + PostgreSQL
2. Deploy Ory Hydra (OAuth2/OIDC)
3. Configure identity schemas
4. Set up basic authentication flows

**Phase 2: Integration (Weeks 3-4)**
1. Build authentication UI (login, register, recovery)
2. Integrate with TMF APIs
3. Implement JWT validation middleware
4. Add Party Role API integration

**Phase 3: Enhancement (Weeks 5-6)**
1. Add MFA (TOTP via Hydra)
2. Implement social login
3. Set up email/SMS notifications
4. Add monitoring and observability

**Phase 4: Authorization (Weeks 7-8)**
1. Deploy Ory Keto (if needed)
2. Implement permission model
3. Integrate with business logic
4. Testing and hardening

**Total Timeline**: 8-10 weeks

### If You Choose WSO2 Identity Server

**Phase 1: Foundation (Weeks 1-3)**
1. Deploy WSO2 IS cluster
2. Configure database (HA)
3. Set up basic authentication
4. Configure OAuth2/OIDC

**Phase 2: Integration (Weeks 4-6)**
1. Integrate with TMF APIs
2. Configure JWT issuance
3. Set up user stores
4. Configure service providers

**Phase 3: Customization (Weeks 7-9)**
1. Customize UI/themes
2. Configure advanced authentication
3. Set up authorization policies
4. Add MFA and adaptive auth

**Phase 4: Operations (Weeks 10-12)**
1. Monitoring setup
2. Backup/DR configuration
3. Performance tuning
4. Security hardening

**Total Timeline**: 12-16 weeks

---

## 14. Final Recommendation

### **For Your MACH Architecture: Ory Kratos + Ory Hydra**

**Rationale:**

1. **MACH Alignment (Critical)**: Ory Kratos is purpose-built for MACH
   - True microservice architecture
   - Cloud-native from day one
   - API-first/headless by design
   - Kubernetes-native

2. **Fits Your Stack**: 
   - Aligns with your existing Kubernetes/Helm deployment
   - Complements your Node.js microservices
   - Works with your TMF Open API architecture
   - Supports your event-driven patterns

3. **Developer Experience**:
   - Modern, well-documented APIs
   - TypeScript SDK for Node.js integration
   - Quick learning curve
   - Active community

4. **Operational Efficiency**:
   - Lightweight containers
   - Easy to scale
   - Simple to operate
   - Lower infrastructure costs

5. **Flexibility**:
   - Full control over UI/UX
   - Extensible via webhooks
   - Open source - no vendor lock-in
   - Can add features via Ory Network

**What You'll Need to Add:**

- **Ory Hydra**: For OAuth2/OIDC and JWT issuance
- **Ory Keto** (optional): For fine-grained authorization
- **Custom UI**: Build your authentication flows
- **PostgreSQL**: For Kratos and Hydra (separate from MongoDB)

**Recommended Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                  API Gateway / Ingress              │
└─────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
    │   Auth   │    │   TMF    │    │   TMF    │
    │    UI    │    │ Product  │    │ Inventory│
    └────┬─────┘    │ Catalog  │    │   API    │
         │          └────┬─────┘    └────┬─────┘
    ┌────▼─────┐        │                │
    │   Ory    │        └────────┬───────┘
    │  Kratos  │                 │
    │(Identity)│            JWT Validation
    └────┬─────┘                 │
         │                  ┌────▼─────┐
    ┌────▼─────┐            │  Party   │
    │   Ory    │            │   Role   │
    │  Hydra   │◄───────────│   API    │
    │(OAuth2)  │            └──────────┘
    └────┬─────┘
         │
    ┌────▼─────┐
    │PostgreSQL│
    │  (IAM)   │
    └──────────┘
```

### When to Reconsider WSO2 IS:

- Enterprise federation (SAML, WS-Fed) is critical
- Complex XACML policies required
- Existing WSO2 infrastructure
- Need out-of-box enterprise features
- Have Java/WSO2 expertise in-house
- Can afford longer implementation timeline

---

## 15. Getting Started with Ory Kratos

### Quick Start Commands

```bash
# 1. Add Ory Helm repository
helm repo add ory https://k8s.ory.sh/helm/charts
helm repo update

# 2. Install PostgreSQL (if not already present)
helm install postgres bitnami/postgresql \
  --set auth.database=kratos \
  --namespace iam --create-namespace

# 3. Install Ory Kratos
helm install kratos ory/kratos \
  --set kratos.config.dsn="postgres://postgres:password@postgres-postgresql:5432/kratos" \
  --namespace iam

# 4. Install Ory Hydra (OAuth2/OIDC)
helm install hydra ory/hydra \
  --set hydra.config.dsn="postgres://postgres:password@postgres-postgresql:5432/hydra" \
  --namespace iam

# 5. Verify deployment
kubectl get pods -n iam
```

### Next Steps

1. **Review documentation**: https://www.ory.sh/docs/kratos
2. **Try quickstart**: https://www.ory.sh/docs/kratos/quickstart
3. **Explore examples**: https://github.com/ory/kratos-selfservice-ui-node
4. **Join community**: https://slack.ory.sh/

---

## 16. References & Resources

### Ory Kratos
- **Documentation**: https://www.ory.sh/docs/kratos
- **GitHub**: https://github.com/ory/kratos
- **Community**: https://github.com/ory/kratos/discussions
- **Examples**: https://github.com/ory/kratos-selfservice-ui-node

### WSO2 Identity Server
- **Documentation**: https://is.docs.wso2.com/
- **GitHub**: https://github.com/wso2/product-is
- **Community**: https://stackoverflow.com/questions/tagged/wso2is

### MACH Alliance
- **Website**: https://machalliance.org/
- **Architecture Guide**: https://machalliance.org/mach-architecture

### TM Forum ODA
- **Documentation**: https://www.tmforum.org/oda/
- **Component Specifications**: https://github.com/tmforum-oda

---

## Conclusion

For your **MACH architecture** and **TM Forum ODA digital ecosystem**, **Ory Kratos + Ory Hydra** is the recommended choice. It aligns perfectly with your cloud-native, microservices-based, API-first architecture and will integrate seamlessly with your existing Kubernetes and Node.js stack.

While WSO2 Identity Server offers more out-of-box enterprise features, it comes with complexity and architectural compromises that conflict with MACH principles. The additional development effort required for Ory Kratos (building UI, integrating multiple Ory services) is offset by better long-term alignment, operational efficiency, and developer experience.

**Start with**: Ory Kratos + Ory Hydra  
**Evaluate later**: Ory Keto (if complex authorization needed)  
**Consider WSO2**: Only if enterprise features become mandatory

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-24
