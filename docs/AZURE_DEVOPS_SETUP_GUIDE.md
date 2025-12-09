# Azure DevOps Setup Guide

Complete step-by-step guide to set up Azure DevOps for your Product Management platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Infrastructure Setup](#azure-infrastructure-setup)
3. [Azure DevOps Project Setup](#azure-devops-project-setup)
4. [Service Connections](#service-connections)
5. [Variable Groups](#variable-groups)
6. [Pipeline Setup](#pipeline-setup)
7. [Branch Policies](#branch-policies)
8. [Environments and Approvals](#environments-and-approvals)
9. [Validation and Testing](#validation-and-testing)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- Azure CLI (`az`) - [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- kubectl - [Install](https://kubernetes.io/docs/tasks/tools/)
- Helm 3.x - [Install](https://helm.sh/docs/intro/install/)
- Git
- Azure DevOps account with organization admin access

### Required Azure Resources
- Azure subscription with contributor access
- Azure DevOps organization
- GitHub or Azure Repos repository

### Skills Required
- Basic Kubernetes knowledge
- Docker basics
- Helm charts basics
- Azure DevOps pipelines

---

## Azure Infrastructure Setup

### Step 1: Login to Azure

```bash
az login
az account set --subscription "Your-Subscription-Name"

# Verify subscription
az account show
```

### Step 2: Create Resource Groups

```bash
# Set variables
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
LOCATION="eastus"

# Create resource groups for each environment
az group create --name rg-dev --location $LOCATION
az group create --name rg-staging --location $LOCATION
az group create --name rg-production --location $LOCATION

# Create shared resources group
az group create --name rg-shared --location $LOCATION
```

### Step 3: Create Azure Container Registry

```bash
ACR_NAME="yourcompanyregistry"  # Must be globally unique

az acr create \
  --resource-group rg-shared \
  --name $ACR_NAME \
  --sku Standard \
  --admin-enabled true

# Get ACR credentials
az acr credential show --name $ACR_NAME

# Save these credentials - you'll need them later
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo "ACR Username: $ACR_USERNAME"
echo "ACR Password: $ACR_PASSWORD"
```

### Step 4: Create AKS Clusters

```bash
# Create AKS cluster for Development
az aks create \
  --resource-group rg-dev \
  --name aks-dev-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME

# Create AKS cluster for Staging
az aks create \
  --resource-group rg-staging \
  --name aks-staging-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME

# Create AKS cluster for Production
az aks create \
  --resource-group rg-production \
  --name aks-prod-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10

# Get AKS credentials
az aks get-credentials --resource-group rg-dev --name aks-dev-cluster --admin
az aks get-credentials --resource-group rg-staging --name aks-staging-cluster --admin
az aks get-credentials --resource-group rg-production --name aks-prod-cluster --admin

# Verify access
kubectl config get-contexts
```

### Step 5: Create Azure Key Vault

```bash
KEYVAULT_NAME="yourcompanykeyvault"  # Must be globally unique

az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group rg-shared \
  --location $LOCATION

# Add secrets to Key Vault
az keyvault secret set --vault-name $KEYVAULT_NAME --name mongodb-prod-connection --value "mongodb://your-connection-string"
az keyvault secret set --vault-name $KEYVAULT_NAME --name api-key-prod --value "your-api-key-here"
az keyvault secret set --vault-name $KEYVAULT_NAME --name jwt-secret-prod --value "$(openssl rand -base64 32)"
az keyvault secret set --vault-name $KEYVAULT_NAME --name encryption-key-prod --value "$(openssl rand -base64 32)"

# List secrets to verify
az keyvault secret list --vault-name $KEYVAULT_NAME --query '[].name' -o table
```

### Step 6: Create Service Principal for Azure DevOps

```bash
SP_NAME="azure-devops-sp"

# Create service principal with contributor role
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name $SP_NAME \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID)

# Extract credentials
APP_ID=$(echo $SP_OUTPUT | jq -r '.appId')
PASSWORD=$(echo $SP_OUTPUT | jq -r '.password')
TENANT_ID=$(echo $SP_OUTPUT | jq -r '.tenant')

echo "==================================="
echo "Service Principal Created"
echo "==================================="
echo "Application (client) ID: $APP_ID"
echo "Client Secret: $PASSWORD"
echo "Tenant ID: $TENANT_ID"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo ""
echo "SAVE THESE CREDENTIALS SECURELY!"
echo "==================================="

# Grant Key Vault access to Service Principal
az keyvault set-policy \
  --name $KEYVAULT_NAME \
  --spn $APP_ID \
  --secret-permissions get list

# Grant ACR pull permissions
az role assignment create \
  --assignee $APP_ID \
  --role AcrPull \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-shared/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME
```

### Step 7: Install NGINX Ingress Controller (for each cluster)

```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install on Dev cluster
kubectl config use-context aks-dev-cluster-admin
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.replicaCount=1

# Install on Staging cluster
kubectl config use-context aks-staging-cluster-admin
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.replicaCount=2

# Install on Production cluster
kubectl config use-context aks-prod-cluster-admin
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.replicaCount=3
```

### Step 8: Create Kubernetes Namespaces

```bash
# Development
kubectl config use-context aks-dev-cluster-admin
kubectl create namespace dev-components

# Staging
kubectl config use-context aks-staging-cluster-admin
kubectl create namespace staging-components

# Production
kubectl config use-context aks-prod-cluster-admin
kubectl create namespace production-components
```

---

## Azure DevOps Project Setup

### Step 1: Create Azure DevOps Organization
1. Go to https://dev.azure.com
2. Click "New organization"
3. Choose a name for your organization
4. Create organization

### Step 2: Create Project
1. Click "New project"
2. Enter project name: "Product-Management-Platform"
3. Visibility: Private
4. Version control: Git
5. Work item process: Agile
6. Click "Create"

### Step 3: Import Repository
1. Go to Repos
2. Click "Import repository"
3. Enter your GitHub URL or:
   - Push your code to Azure Repos:
   ```bash
   git remote add azure https://dev.azure.com/yourorg/Product-Management-Platform/_git/Product-Management-Platform
   git push azure main
   ```

---

## Service Connections

### Step 1: Create Azure Resource Manager Connection

1. Navigate to **Project Settings** → **Service connections**
2. Click **New service connection**
3. Select **Azure Resource Manager**
4. Choose **Service principal (manual)**
5. Enter details:
   - **Connection name**: `azure-resource-manager`
   - **Subscription ID**: (from earlier)
   - **Subscription Name**: Your subscription name
   - **Service Principal ID**: (App ID from earlier)
   - **Service Principal Key**: (Password from earlier)
   - **Tenant ID**: (from earlier)
6. Click **Verify** then **Save**

### Step 2: Create Docker Registry Connection

1. Click **New service connection**
2. Select **Docker Registry**
3. Choose **Azure Container Registry**
4. Select your subscription
5. Select your ACR
6. Enter details:
   - **Connection name**: `acr-connection`
   - **Azure Container Registry**: Select your ACR
7. Click **Save**

### Step 3: Create Kubernetes Service Connections

Create three separate connections for each environment:

**Development AKS:**
1. Click **New service connection**
2. Select **Kubernetes**
3. Choose **Azure Subscription**
4. Select your subscription
5. Select **aks-dev-cluster**
6. Namespace: `dev-components`
7. Connection name: `aks-dev`
8. Click **Save**

**Staging AKS:**
- Repeat with `aks-staging-cluster`, namespace `staging-components`, name `aks-staging`

**Production AKS:**
- Repeat with `aks-prod-cluster`, namespace `production-components`, name `aks-production`

### Step 4: Verify Service Connections

All connections should show green checkmark:
- ✅ azure-resource-manager
- ✅ acr-connection
- ✅ aks-dev
- ✅ aks-staging
- ✅ aks-production

---

## Variable Groups

### Step 1: Create Global Variable Groups

Navigate to **Pipelines** → **Library**

#### Create: acr-connection
1. Click **+ Variable group**
2. Name: `acr-connection`
3. Add variables:
   - `containerRegistry`: `yourregistry.azurecr.io`
   - `acrServiceConnection`: `acr-connection`
   - `acrUsername`: (from ACR) - **Mark as secret**
   - `acrPassword`: (from ACR) - **Mark as secret**
4. Click **Save**

#### Create: helm-repo-config
1. Name: `helm-repo-config`
2. Add variables:
   - `helmRepoUrl`: Your Helm repo URL (or leave blank if using ACR)
3. Click **Save**

### Step 2: Create Environment Variable Groups

#### Create: env-dev-config
1. Name: `env-dev-config`
2. Add variables:
   ```
   aksDevConnection: aks-dev
   devNamespace: dev-components
   devClusterName: aks-dev-cluster
   devResourceGroup: rg-dev
   logLevel: debug
   replicas: 1
   ```

#### Create: env-staging-config
1. Name: `env-staging-config`
2. Add variables:
   ```
   aksStagingConnection: aks-staging
   stagingNamespace: staging-components
   stagingClusterName: aks-staging-cluster
   stagingResourceGroup: rg-staging
   logLevel: info
   replicas: 2
   ```

#### Create: env-production-config
1. Name: `env-production-config`
2. Add variables:
   ```
   aksProdConnection: aks-production
   productionNamespace: production-components
   productionClusterName: aks-prod-cluster
   productionResourceGroup: rg-production
   logLevel: warn
   productionReplicas: 3
   productionCpu: 1000m
   productionMemory: 2Gi
   ```

### Step 3: Create Key Vault Variable Group

1. Click **+ Variable group**
2. Name: `env-secrets-production`
3. Enable **Link secrets from an Azure key vault as variables**
4. Select service connection: `azure-resource-manager`
5. Select Key Vault: `yourcompanykeyvault`
6. Click **Authorize**
7. Click **+ Add** and select secrets:
   - mongodb-prod-connection
   - api-key-prod
   - jwt-secret-prod
   - encryption-key-prod
8. Click **Save**

---

## Pipeline Setup

### Step 1: Create CI Build Pipeline

1. Navigate to **Pipelines** → **Pipelines**
2. Click **New pipeline**
3. Select **Azure Repos Git**
4. Select your repository
5. Choose **Existing Azure Pipelines YAML file**
6. Path: `/azure-pipelines/ci-build.yml`
7. Click **Continue**
8. Click **Save** (don't run yet)
9. Click the three dots → **Rename/move**
10. Rename to: `CI-Build`

### Step 2: Create Release Pipeline

1. Click **New pipeline**
2. Select **Azure Repos Git**
3. Select your repository
4. Choose **Existing Azure Pipelines YAML file**
5. Path: `/azure-pipelines/release-pipeline.yml`
6. Click **Continue**
7. Click **Save**
8. Rename to: `Release-Pipeline`

### Step 3: Create Hotfix Pipeline

1. Click **New pipeline**
2. Select **Azure Repos Git**
3. Choose **Existing Azure Pipelines YAML file**
4. Path: `/azure-pipelines/hotfix-pipeline.yml`
5. Click **Continue**
6. Click **Save**
7. Rename to: `Hotfix-Pipeline`

### Step 4: Grant Pipeline Permissions

For each pipeline:
1. Click on the pipeline
2. Click **Edit**
3. Click the three dots → **Settings**
4. Under **Processing of new run requests**: Select **Immediately**
5. Under **Variable groups**:
   - Add all variable groups the pipeline needs
   - Grant access

---

## Branch Policies

### Step 1: Configure Main Branch Policy

1. Navigate to **Repos** → **Branches**
2. Find `main` branch
3. Click the three dots → **Branch policies**
4. Configure:

**Require a minimum number of reviewers**
- ✅ Enable
- Minimum number of reviewers: **2**
- ✅ Requestors can approve their own changes: **No**
- ✅ Prohibit the most recent pusher from approving: **Yes**
- ✅ Require completion of associated work items: **Yes**

**Check for linked work items**
- ✅ Enable
- Mode: **Required**

**Check for comment resolution**
- ✅ Enable
- Mode: **Required**

**Build validation**
- Click **+ Add build policy**
- Select **CI-Build** pipeline
- Display name: `CI Build Validation`
- Trigger: **Automatic**
- Policy requirement: **Required**
- Build expiration: **Immediately**

**Status checks**
- Add any external status checks if needed

5. Click **Save**

### Step 2: Configure Develop Branch Policy

1. Find `develop` branch (create if doesn't exist)
2. Click the three dots → **Branch policies**
3. Configure:

**Require a minimum number of reviewers**
- ✅ Enable
- Minimum number of reviewers: **1**

**Build validation**
- Add **CI-Build** pipeline

4. Click **Save**

---

## Environments and Approvals

### Step 1: Create Development Environment

1. Navigate to **Pipelines** → **Environments**
2. Click **New environment**
3. Name: `Development`
4. Resource: **None**
5. Click **Create**
6. No approvals needed (automatic deployment)

### Step 2: Create Staging Environment

1. Click **New environment**
2. Name: `Staging`
3. Click **Create**
4. Click the three dots → **Approvals and checks**
5. Click **Approvals**
6. Add approvers: (Add QA team members)
7. Instructions: "Please validate in staging environment"
8. Timeout: 24 hours
9. Click **Create**

### Step 3: Create Production Environment

1. Click **New environment**
2. Name: `Production`
3. Click **Create**
4. Click the three dots → **Approvals and checks**
5. Click **Approvals**
6. Add approvers: (Add 2+ production approvers)
7. Instructions: "Production deployment approval required"
8. Timeout: 48 hours
9. ✅ Require approval from all users
10. Click **Create**

**Add Business Hours Check:**
1. Click **Approvals and checks** again
2. Click **Business hours**
3. Configure business hours (e.g., Mon-Fri, 9 AM - 5 PM)
4. Time zone: Your timezone
5. Click **Save**

### Step 4: Create Production-Hotfix Environment

1. Click **New environment**
2. Name: `Production-Hotfix`
3. Add approvals with expedited process (1 approver, shorter timeout)

---

## Validation and Testing

### Step 1: Test CI Pipeline

1. Create a feature branch:
   ```bash
   git checkout -b feature/test-pipeline
   ```

2. Make a small change and commit:
   ```bash
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test CI pipeline"
   git push origin feature/test-pipeline
   ```

3. Create Pull Request to `develop`
4. Verify CI-Build pipeline triggers
5. Check that all stages complete successfully

### Step 2: Test Development Deployment

1. Merge PR to `develop`
2. Verify Release-Pipeline triggers
3. Check deployment to Development environment
4. Verify pods are running:
   ```bash
   kubectl config use-context aks-dev-cluster-admin
   kubectl get pods -n dev-components
   ```

### Step 3: Test Staging Deployment

1. Create release branch:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/1.0.0
   git push origin release/1.0.0
   ```

2. Verify deployment to Staging
3. Approve if required
4. Check pods in staging

### Step 4: Test Production Deployment

1. Merge release branch to `main`
2. Verify Production approval request
3. Approve deployment
4. Monitor production deployment
5. Verify:
   ```bash
   kubectl config use-context aks-prod-cluster-admin
   kubectl get pods -n production-components
   kubectl get services -n production-components
   ```

---

## Troubleshooting

### Issue: Pipeline fails with "Permission denied"

**Solution:**
- Check service connection permissions
- Verify service principal has correct roles
- Re-authorize service connections

### Issue: Cannot push Docker images to ACR

**Solution:**
```bash
# Verify ACR access
az acr login --name yourregistry

# Check ACR credentials
az acr credential show --name yourregistry

# Update service connection with new credentials
```

### Issue: Helm deployment fails

**Solution:**
```bash
# Check AKS connectivity
kubectl get nodes

# Verify namespace exists
kubectl get namespaces

# Check Helm release status
helm list -n your-namespace

# View pod logs
kubectl logs -n your-namespace pod-name
```

### Issue: Key Vault secrets not accessible

**Solution:**
```bash
# Grant service principal access to Key Vault
az keyvault set-policy \
  --name yourkeyvault \
  --spn <service-principal-id> \
  --secret-permissions get list

# Verify secrets exist
az keyvault secret list --vault-name yourkeyvault
```

### Issue: Environment approval not triggering

**Solution:**
- Check environment configuration
- Verify approvers have correct permissions
- Check approval timeout settings
- Review pipeline YAML for correct environment name

---

## Next Steps

After completing this setup:

1. ✅ Validate all pipelines work correctly
2. ✅ Set up monitoring and alerts
3. ✅ Configure backup strategies
4. ✅ Document runbooks for operations team
5. ✅ Train team on deployment process
6. ✅ Schedule release planning meeting
7. ✅ Set up status page for stakeholders
8. ✅ Configure Slack/Teams notifications

---

## Additional Resources

- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)
- [Azure Kubernetes Service](https://docs.microsoft.com/en-us/azure/aks/)
- [Helm Documentation](https://helm.sh/docs/)
- [YAML Pipeline Schema](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema)

---

## Support and Contacts

- **DevOps Team**: devops@yourcompany.com
- **Platform Team**: platform@yourcompany.com
- **On-Call**: Check PagerDuty/OpsGenie

---

*Last Updated: December 2025*
