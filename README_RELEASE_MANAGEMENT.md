# Release Management & Azure DevOps Setup

Complete setup for release management, Azure DevOps pipelines, and backlog organization for the Product Management Platform (ProductCatalog + Plugins).

## 📚 Documentation Overview

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [Release Management Guide](docs/RELEASE_MANAGEMENT_GUIDE.md) | Comprehensive release strategy and processes | All teams |
| [Azure DevOps Setup Guide](docs/AZURE_DEVOPS_SETUP_GUIDE.md) | Step-by-step Azure DevOps configuration | DevOps Engineers |
| [Backlog Management Guide](docs/BACKLOG_MANAGEMENT_GUIDE.md) | Organize backlogs for main product and plugins | Product Owners, Scrum Masters |
| [Deployment Runbook](docs/DEPLOYMENT_RUNBOOK.md) | Operational deployment procedures | Operations Team |
| [Quick Start: Backlog](docs/QUICK_START_BACKLOG.md) | 30-minute backlog setup | All teams |

### Pipeline Files

| File | Purpose |
|------|---------|
| [azure-pipelines/ci-build.yml](azure-pipelines/ci-build.yml) | Main CI pipeline (builds, tests, security scans) |
| [azure-pipelines/release-pipeline.yml](azure-pipelines/release-pipeline.yml) | Multi-stage release pipeline (Dev → Staging → Prod) |
| [azure-pipelines/hotfix-pipeline.yml](azure-pipelines/hotfix-pipeline.yml) | Fast-track pipeline for critical fixes |
| [azure-pipelines/templates/](azure-pipelines/templates/) | Reusable pipeline templates |

### Configuration Files

| File | Purpose |
|------|---------|
| [charts/ProductCatalog/values-*.yaml](charts/ProductCatalog/) | Helm values for each environment |
| [charts/ProductInventory/values-*.yaml](charts/ProductInventory/) | Helm values for each environment |
| [azure-pipelines/variable-groups/](azure-pipelines/variable-groups/) | Variable group documentation |

---

## 🚀 Quick Start

### For Release Management (5 minutes)
1. Read [Release Management Guide](docs/RELEASE_MANAGEMENT_GUIDE.md) - Key sections:
   - Release types and cadence
   - Branching strategy
   - Environment progression

### For Azure DevOps Setup (2-3 hours)
1. Follow [Azure DevOps Setup Guide](docs/AZURE_DEVOPS_SETUP_GUIDE.md) step-by-step:
   - Azure infrastructure setup
   - Service connections
   - Pipeline configuration
   - Environments and approvals

### For Backlog Organization (30 minutes)
1. Use [Quick Start: Backlog](docs/QUICK_START_BACKLOG.md) to set up:
   - Area paths for main product and plugins
   - Teams and iterations
   - Work item templates
   - Essential queries

---

## 🏗️ Architecture Overview

### Component Structure
```
Product Management Platform
├── ProductCatalog (Main Product)
│   ├── Product Catalog API
│   ├── Party Role API
│   ├── Promotion Management API
│   └── Metrics API
│
├── ProductInventory (Plugin)
│   ├── Product Inventory API
│   └── Party Role API
│
└── Shared Infrastructure
    ├── MongoDB
    ├── Monitoring
    └── CI/CD
```

### Environment Progression
```
Developer
    ↓ (git push to feature branch)
    ↓ (PR triggers CI)
CI/Build Pipeline
    ↓ (merge to develop)
Development Environment ←─── Auto Deploy
    ↓ (create release branch)
Staging Environment ←─────── Auto Deploy
    ↓ (merge to main + approval)
Production Environment ←──── Manual Approval
```

### Backlog Organization
```
Azure DevOps Project: Product-Management-Platform
│
├── Area: ProductCatalog
│   ├── Team: ProductCatalog Team
│   ├── Backlog: Main product features
│   └── Sprint: 2-week cadence
│
├── Area: ProductInventory  
│   ├── Team: ProductInventory Team
│   ├── Backlog: Plugin features
│   └── Sprint: 2-week cadence (synchronized)
│
└── Area: Platform
    ├── Team: Platform Team
    ├── Backlog: Infrastructure & shared services
    └── Sprint: 2-week cadence
```

---

## 📋 Release Management Strategy

### Release Types

| Type | Version | Cadence | Approval | Testing |
|------|---------|---------|----------|---------|
| **Major** | X.0.0 | Quarterly | Architecture + Business | Full regression + Performance + Security |
| **Minor** | X.Y.0 | Monthly | Product Owner | Full regression + Integration |
| **Patch** | X.Y.Z | As needed | Team Lead | Targeted + Smoke tests |
| **Hotfix** | X.Y.Z | Immediate | Expedited (1 approver) | Quick validation |

### Branching Strategy (GitFlow)

```
main (production)
  │
  ├── release/1.2.x (release branches)
  │     │
  │     └── (merged from develop)
  │
  └── develop (integration)
        │
        ├── feature/TICKET-123-feature-name
        ├── bugfix/TICKET-456-bug-name
        └── hotfix/TICKET-789-critical-fix (from main)
```

### Versioning

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, architectural updates
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes, security patches

**Git Tags**:
- Component: `productcatalog-v1.2.1`
- Platform: `platform-v2.0.0`
- Hotfix: `hotfix-v1.2.2`

---

## 🔄 Pipeline Overview

### CI/Build Pipeline
**Trigger**: All branches (PRs and commits)

```
┌─────────────────────────────────────────────────┐
│ Stage 1: Build and Unit Test                   │
│  - Build Node.js microservices                 │
│  - Run unit tests                              │
│  - Code coverage                               │
├─────────────────────────────────────────────────┤
│ Stage 2: Code Quality & Security               │
│  - Linting                                     │
│  - Security scanning (SAST)                    │
│  - Dependency vulnerabilities                  │
├─────────────────────────────────────────────────┤
│ Stage 3: Build Docker Images                   │
│  - Build images for all microservices         │
│  - Push to Azure Container Registry           │
│  - Tag with version and commit SHA            │
├─────────────────────────────────────────────────┤
│ Stage 4: Integration Tests                     │
│  - Deploy to ephemeral environment            │
│  - Run integration tests                      │
│  - API contract tests                         │
├─────────────────────────────────────────────────┤
│ Stage 5: Package Helm Charts                   │
│  - Lint Helm charts                           │
│  - Package charts                             │
│  - Publish artifacts                          │
└─────────────────────────────────────────────────┘
```

### Release Pipeline
**Trigger**: Release branches and main

```
┌─────────────────────────────────────────────────┐
│ Stage 1: Build Release Artifacts               │
│  - Production Docker images                    │
│  - Helm charts                                 │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓ (automatic)
┌─────────────────────────────────────────────────┐
│ Stage 2: Development Environment                │
│  - Deploy to dev cluster                       │
│  - Smoke tests                                 │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓ (automatic)
┌─────────────────────────────────────────────────┐
│ Stage 3: Staging Environment                    │
│  - Deploy to staging cluster                   │
│  - Integration tests                           │
│  - Performance tests                           │
│  - QA validation                               │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓ (manual approval - 2 approvers)
┌─────────────────────────────────────────────────┐
│ Stage 4: Production Environment                 │
│  - Backup current state                        │
│  - Blue-Green deployment                       │
│  - Health checks                               │
│  - Extended monitoring (30 min)                │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Backlog Organization

### Structure

**Area-Based Organization** (Recommended):

```
Product-Management-Platform
│
├── ProductCatalog (Main Product)
│   ├── Core-API
│   ├── Party-Role-API
│   ├── Promotion-API
│   └── Infrastructure
│
├── ProductInventory (Plugin)
│   ├── Inventory-API
│   └── Integration
│
├── Shared-Services
│   ├── Authentication
│   ├── Monitoring
│   └── DevOps
│
└── Platform
    ├── Infrastructure
    └── Security
```

### Work Item Hierarchy

```
Epic (Strategic Initiative)
  │
  ├── Feature (Deliverable Capability)
  │     │
  │     ├── User Story (User-Facing)
  │     │     │
  │     │     ├── Task (Dev Work)
  │     │     ├── Bug (Defects)
  │     │     └── Test Case
  │     │
  │     └── User Story
  │
  └── Feature
```

### Tags Strategy

**Component Tags**: `main-product`, `plugin`, `productcatalog`, `productinventory`
**Type Tags**: `api`, `backend`, `frontend`, `infrastructure`
**Priority Tags**: `critical`, `customer-facing`, `technical-debt`
**Release Tags**: `v1.2.0`, `v1.3.0`, `hotfix`
**Integration Tags**: `cross-component`, `breaking-change`

---

## 🔐 Security & Compliance

### Security Gates

**Pre-Deployment Checks**:
- ✅ No critical vulnerabilities in images
- ✅ No exposed secrets in code
- ✅ All dependencies up to date
- ✅ Security scan passed
- ✅ Compliance check passed

### Secrets Management

**Never commit**:
- Database connection strings
- API keys
- Certificates
- Passwords

**Always use**:
- Azure Key Vault for production secrets
- Variable groups (marked as secret) for non-production
- Service principals for authentication
- Managed identities when possible

---

## 📊 Monitoring & Metrics

### Key Metrics

**Release Metrics**:
- **Lead Time**: Commit to production
- **Deploy Frequency**: How often deploying
- **MTTR**: Mean time to recovery
- **Change Failure Rate**: % of deployments causing incidents

**Team Metrics**:
- Sprint velocity
- Work item throughput
- Cycle time
- Bug resolution time

**Application Metrics**:
- Service uptime (99.9% SLA)
- Error rate (< 0.1%)
- Response time (p95 < 500ms)
- Request throughput

---

## 🚨 Troubleshooting

### Common Issues

**Pipeline Fails**:
1. Check service connections
2. Verify variable groups
3. Review pipeline logs
4. Check Azure resources

**Deployment Fails**:
1. Check AKS cluster health
2. Verify namespace exists
3. Check Helm release status
4. Review pod logs

**Work Items Not Visible**:
1. Check area path filters
2. Verify team membership
3. Check query filters

### Get Help

- **Documentation**: Check relevant guide in `docs/` folder
- **Runbook**: See [Deployment Runbook](docs/DEPLOYMENT_RUNBOOK.md)
- **Support**: Contact DevOps team

---

## ✅ Implementation Checklist

### Phase 1: Azure Infrastructure (Week 1)
- [ ] Create Azure resource groups
- [ ] Set up Azure Container Registry
- [ ] Create AKS clusters (dev, staging, prod)
- [ ] Set up Azure Key Vault
- [ ] Create service principals
- [ ] Install ingress controllers

### Phase 2: Azure DevOps Setup (Week 1-2)
- [ ] Create Azure DevOps project
- [ ] Configure service connections
- [ ] Set up variable groups
- [ ] Import pipeline YAML files
- [ ] Configure branch policies
- [ ] Create environments with approvals

### Phase 3: Backlog Organization (Week 2)
- [ ] Create area paths
- [ ] Set up teams
- [ ] Configure iterations
- [ ] Create work item templates
- [ ] Set up queries and dashboards
- [ ] Import existing work items

### Phase 4: Testing & Validation (Week 2-3)
- [ ] Test CI pipeline
- [ ] Test dev deployment
- [ ] Test staging deployment
- [ ] Test production deployment (non-prod data)
- [ ] Validate rollback procedures
- [ ] Train teams

### Phase 5: Go Live (Week 3)
- [ ] Final validation
- [ ] Team training completed
- [ ] Documentation reviewed
- [ ] First production deployment
- [ ] Monitor and iterate

---

## 📚 Additional Resources

### Documentation
- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)
- [Azure Kubernetes Service](https://docs.microsoft.com/en-us/azure/aks/)
- [Helm Documentation](https://helm.sh/docs/)
- [Semantic Versioning](https://semver.org/)

### Tools
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/)
- [Git](https://git-scm.com/)

### Internal
- DevOps Team: devops@yourcompany.com
- Platform Team: platform@yourcompany.com
- Training Resources: [Internal Wiki]

---

## 🎓 Training & Support

### Recommended Training Path

**For Developers**:
1. Read: Release Management Guide (focus on branching strategy)
2. Read: Deployment Runbook (focus on your component)
3. Practice: Create feature branch → PR → deploy to dev

**For DevOps Engineers**:
1. Complete: Azure DevOps Setup Guide (hands-on)
2. Review: All pipeline YAML files
3. Practice: Deploy to all environments

**For Product Owners / Scrum Masters**:
1. Complete: Quick Start Backlog (hands-on)
2. Read: Backlog Management Guide (focus on your product)
3. Practice: Create Epics → Features → Stories

**For Operations Team**:
1. Read: Deployment Runbook (comprehensive)
2. Review: Monitoring and health checks
3. Practice: Deployment and rollback procedures

---

## 📞 Support Contacts

| Team | Email | Slack Channel |
|------|-------|---------------|
| DevOps | devops@yourcompany.com | #devops |
| Platform | platform@yourcompany.com | #platform |
| ProductCatalog | catalog-team@yourcompany.com | #product-catalog |
| ProductInventory | inventory-team@yourcompany.com | #product-inventory |

---

## 📝 License & Contributions

This documentation is maintained by the Platform Team. For updates or corrections, please:
1. Create an issue or
2. Submit a pull request

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Maintainer**: Platform Team
