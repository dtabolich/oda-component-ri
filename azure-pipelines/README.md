# Azure DevOps Pipelines

This directory contains Azure DevOps pipeline definitions for the Product Management platform.

## Pipeline Structure

```
azure-pipelines/
├── ci-build.yml                    # Main CI pipeline (runs on PRs and commits)
├── release-pipeline.yml            # Multi-stage release pipeline
├── docker-build.yml                # Docker image build pipeline
├── helm-release.yml                # Helm chart packaging and publishing
├── hotfix-pipeline.yml             # Fast-track pipeline for hotfixes
├── templates/                      # Reusable pipeline templates
│   ├── build-microservice.yml      # Template for building Node.js services
│   ├── docker-build-push.yml       # Template for Docker operations
│   ├── helm-package.yml            # Template for Helm operations
│   ├── deploy-to-aks.yml          # Template for AKS deployments
│   └── security-scan.yml           # Template for security scanning
└── variable-groups/                # Documentation for variable groups
    └── variable-groups.md
```

## Quick Start

### Prerequisites
1. Azure DevOps project created
2. Service connections configured:
   - Azure Container Registry
   - Azure Kubernetes Service (for each environment)
   - Azure Key Vault
3. Variable groups created (see variable-groups/variable-groups.md)
4. Branch policies configured on main and develop branches

### Setting Up Pipelines

1. **Create CI Pipeline**
   - New Pipeline → Azure Repos Git → Select repository
   - Existing Azure Pipelines YAML file
   - Path: `/azure-pipelines/ci-build.yml`
   - Name: `CI-Build`

2. **Create Release Pipeline**
   - New Pipeline → Azure Repos Git → Select repository
   - Existing Azure Pipelines YAML file
   - Path: `/azure-pipelines/release-pipeline.yml`
   - Name: `Release-Pipeline`

3. **Create Helm Release Pipeline**
   - New Pipeline → Azure Repos Git → Select repository
   - Existing Azure Pipelines YAML file
   - Path: `/azure-pipelines/helm-release.yml`
   - Name: `Helm-Release`

### Pipeline Triggers

- **ci-build.yml**: Triggers on all branches (PRs and commits)
- **release-pipeline.yml**: Triggers on release/* branches and main
- **helm-release.yml**: Manual trigger or on Git tags
- **hotfix-pipeline.yml**: Triggers on hotfix/* branches

## Variable Groups

Create these variable groups in Azure DevOps Library:

### Global Variables
- `acr-connection`: Azure Container Registry connection details
- `helm-repo-config`: Helm repository configuration

### Environment-Specific
- `env-dev-config`: Development environment configuration
- `env-staging-config`: Staging environment configuration
- `env-production-config`: Production environment configuration
- `env-secrets-production`: Production secrets (Key Vault backed)

See [variable-groups.md](./variable-groups/variable-groups.md) for detailed configuration.

## Service Connections

Required service connections in Azure DevOps:

1. **Azure Container Registry**
   - Type: Docker Registry
   - Name: `acr-connection`

2. **Azure Kubernetes Service - Dev**
   - Type: Kubernetes
   - Name: `aks-dev`

3. **Azure Kubernetes Service - Staging**
   - Type: Kubernetes
   - Name: `aks-staging`

4. **Azure Kubernetes Service - Production**
   - Type: Kubernetes
   - Name: `aks-production`

5. **Azure Key Vault**
   - Type: Azure Resource Manager
   - Name: `keyvault-connection`

## Branch Policies

Configure these policies on protected branches:

### Main Branch
- Require pull request reviews: 2 approvers
- Required pipelines: CI-Build
- Check for linked work items
- Check for comment resolution

### Develop Branch
- Require pull request reviews: 1 approver
- Required pipelines: CI-Build

## Environments

Create these environments in Azure DevOps:

1. **Development**
   - No approvals required
   - Automatic deployment

2. **Staging**
   - Optional: Require 1 approval
   - Automatic deployment after dev

3. **Production**
   - Require 2 approvals
   - Manual deployment trigger
   - Scheduled deployment window (optional)

## Deployment Strategies

### Development
- Direct deployment on every merge to develop
- Latest version always deployed

### Staging
- Deployed when release branch is created
- Used for QA and UAT

### Production
- Blue-Green deployment (recommended)
- Canary deployment (for high-risk changes)
- Rolling update (default)

## Monitoring and Alerts

Configure these alerts in Azure DevOps:

1. Pipeline failure notifications
2. Deployment failure notifications
3. Security scan failures
4. Long-running pipeline alerts

## Troubleshooting

### Common Issues

**Pipeline fails at Docker build**
- Check ACR service connection
- Verify Dockerfile paths
- Check Docker authentication

**Helm deployment fails**
- Verify AKS service connection
- Check namespace exists
- Verify RBAC permissions

**Tests fail in pipeline but pass locally**
- Check environment variables
- Verify dependencies are installed
- Check for environment-specific issues

## Best Practices

1. **Use Templates**: Reuse common pipeline logic via templates
2. **Parameterize**: Use variables for environment-specific values
3. **Cache Dependencies**: Cache npm/node_modules to speed up builds
4. **Parallel Jobs**: Run independent jobs in parallel
5. **Fail Fast**: Run quick tests first
6. **Security Scans**: Always run security scans before deployment
7. **Approval Gates**: Use manual approvals for production
8. **Rollback Plan**: Always have a rollback mechanism

## Maintenance

### Regular Tasks
- Review and update pipeline templates monthly
- Update Docker base images
- Review security scan results
- Archive old pipeline runs
- Update documentation

### Pipeline Performance
- Monitor pipeline duration trends
- Optimize slow stages
- Review cache effectiveness
- Consider using self-hosted agents for faster builds
