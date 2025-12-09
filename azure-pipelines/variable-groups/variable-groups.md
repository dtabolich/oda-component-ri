# Azure DevOps Variable Groups Configuration

This document describes all variable groups required for the pipelines.

## How to Create Variable Groups

1. Navigate to **Pipelines → Library** in Azure DevOps
2. Click **+ Variable group**
3. Enter the group name and add variables
4. For secrets, click the lock icon to mark as secret
5. For Key Vault integration, select **Link secrets from an Azure key vault**

---

## Global Variable Groups

### 1. acr-connection
**Description**: Azure Container Registry connection details

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| containerRegistry | your-registry.azurecr.io | No | ACR registry URL |
| acrServiceConnection | acr-connection | No | Service connection name |
| acrUsername | (from ACR) | Yes | ACR username |
| acrPassword | (from ACR) | Yes | ACR password |

**Setup Instructions**:
```bash
# Get ACR credentials
az acr credential show --name your-registry

# Or create service principal for ACR
az ad sp create-for-rbac --name acr-service-principal --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.ContainerRegistry/registries/{registry-name} --role acrpull
```

---

### 2. helm-repo-config
**Description**: Helm repository configuration

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| helmRepoUrl | https://your-helm-repo.com | No | Helm repository URL |
| helmRepoUsername | (if required) | Yes | Helm repo username |
| helmRepoPassword | (if required) | Yes | Helm repo password |

---

## Environment-Specific Variable Groups

### 3. env-dev-config
**Description**: Development environment configuration

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| aksDevConnection | aks-dev | No | AKS dev service connection |
| devNamespace | dev-components | No | Kubernetes namespace |
| devClusterName | aks-dev-cluster | No | AKS cluster name |
| devResourceGroup | rg-dev | No | Azure resource group |
| mongodbConnectionString | (dev MongoDB) | Yes | MongoDB connection string |
| logLevel | debug | No | Application log level |
| replicas | 1 | No | Number of replicas |

---

### 4. env-staging-config
**Description**: Staging environment configuration

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| aksStagingConnection | aks-staging | No | AKS staging service connection |
| stagingNamespace | staging-components | No | Kubernetes namespace |
| stagingClusterName | aks-staging-cluster | No | AKS cluster name |
| stagingResourceGroup | rg-staging | No | Azure resource group |
| mongodbConnectionString | (staging MongoDB) | Yes | MongoDB connection string |
| logLevel | info | No | Application log level |
| replicas | 2 | No | Number of replicas |

---

### 5. env-production-config
**Description**: Production environment configuration

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| aksProdConnection | aks-production | No | AKS prod service connection |
| productionNamespace | production-components | No | Kubernetes namespace |
| productionClusterName | aks-prod-cluster | No | AKS cluster name |
| productionResourceGroup | rg-production | No | Azure resource group |
| logLevel | warn | No | Application log level |
| productionReplicas | 3 | No | Number of replicas |
| productionCpu | 1000m | No | CPU request |
| productionMemory | 2Gi | No | Memory request |

---

### 6. env-secrets-production (Key Vault Backed)
**Description**: Production secrets from Azure Key Vault

| Variable Name | Key Vault Secret | Description |
|--------------|------------------|-------------|
| mongodbConnectionString | mongodb-prod-connection | MongoDB connection string |
| apiKey | api-key-prod | API key for external services |
| jwtSecret | jwt-secret-prod | JWT signing secret |
| encryptionKey | encryption-key-prod | Data encryption key |

**Setup Instructions**:
1. Create Azure Key Vault if not exists:
```bash
az keyvault create --name your-keyvault --resource-group rg-production --location eastus
```

2. Add secrets to Key Vault:
```bash
az keyvault secret set --vault-name your-keyvault --name mongodb-prod-connection --value "mongodb://..."
az keyvault secret set --vault-name your-keyvault --name api-key-prod --value "your-api-key"
az keyvault secret set --vault-name your-keyvault --name jwt-secret-prod --value "your-jwt-secret"
```

3. In Azure DevOps:
   - Go to Library → + Variable group
   - Enable "Link secrets from an Azure key vault as variables"
   - Select your Azure subscription
   - Select your Key Vault
   - Authorize the connection
   - Add the secrets you want to use

---

## Optional Variable Groups

### 7. notification-config
**Description**: Notification settings for pipeline events

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| slackWebhook | https://hooks.slack.com/... | Yes | Slack webhook URL |
| teamsWebhook | https://outlook.office.com/... | Yes | Teams webhook URL |
| emailRecipients | team@example.com | No | Email recipients |

---

### 8. feature-flags
**Description**: Feature flags for enabling/disabling features

| Variable Name | Value | Secret | Description |
|--------------|-------|--------|-------------|
| enableCanaryDeployment | false | No | Enable canary deployments |
| enableBlueGreen | true | No | Enable blue-green deployments |
| enableAutoRollback | true | No | Enable automatic rollback |
| enableSecurityScanning | true | No | Enable security scanning |

---

## Variable Naming Conventions

Follow these conventions when adding variables:

### Naming Pattern
- Use camelCase for variable names
- Use descriptive names
- Prefix with environment for env-specific variables

### Examples
```
✅ Good:
- mongodbConnectionString
- aksDevConnection
- productionReplicas

❌ Bad:
- mongodb
- connection
- replicas
```

---

## Security Best Practices

1. **Never Store Secrets in Plain Text**
   - Always mark sensitive values as secret
   - Use Key Vault for production secrets

2. **Rotate Secrets Regularly**
   - Set up a rotation schedule
   - Update Key Vault secrets, not variable groups directly

3. **Use Managed Identities**
   - Prefer managed identities over service principals when possible
   - Reduces secret management overhead

4. **Limit Access**
   - Grant variable group access only to required pipelines
   - Use Azure DevOps permissions to restrict access

5. **Audit Access**
   - Regularly review who has access to variable groups
   - Monitor Key Vault access logs

---

## Complete Setup Script

Here's a complete script to set up all Azure resources and variable groups:

```bash
#!/bin/bash

# Configuration
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="rg-devops"
LOCATION="eastus"
ACR_NAME="yourregistry"
KEYVAULT_NAME="yourkeyvault"

# Login to Azure
az login
az account set --subscription $SUBSCRIPTION_ID

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Standard

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

echo "ACR Username: $ACR_USERNAME"
echo "ACR Password: $ACR_PASSWORD"

# Create Azure Key Vault
az keyvault create --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION

# Set Key Vault secrets
az keyvault secret set --vault-name $KEYVAULT_NAME --name mongodb-prod-connection --value "mongodb://your-connection-string"
az keyvault secret set --vault-name $KEYVAULT_NAME --name api-key-prod --value "your-api-key"
az keyvault secret set --vault-name $KEYVAULT_NAME --name jwt-secret-prod --value "$(openssl rand -base64 32)"

# Create Service Principal for Azure DevOps
SP_NAME="azure-devops-sp"
SP_CREDENTIALS=$(az ad sp create-for-rbac --name $SP_NAME --role contributor --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP)

echo "Service Principal created:"
echo $SP_CREDENTIALS

# Grant Key Vault access to Service Principal
SP_OBJECT_ID=$(echo $SP_CREDENTIALS | jq -r '.appId' | xargs az ad sp show --id | jq -r '.id')
az keyvault set-policy --name $KEYVAULT_NAME --object-id $SP_OBJECT_ID --secret-permissions get list

echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Create service connections in Azure DevOps using the credentials above"
echo "2. Create variable groups in Azure DevOps Library"
echo "3. Link Key Vault secrets to env-secrets-production variable group"
```

---

## Troubleshooting

### Issue: Variable not found in pipeline
**Solution**: 
- Verify variable group is linked to pipeline
- Check variable name spelling (case-sensitive)
- Ensure pipeline has access to the variable group

### Issue: Cannot access Key Vault secrets
**Solution**:
- Verify service connection has Key Vault access
- Check Key Vault access policies
- Ensure secrets exist in Key Vault

### Issue: Secret values visible in logs
**Solution**:
- Mark variable as secret in variable group
- Never use `echo` or `print` with secret variables
- Use Azure DevOps logging commands to mask secrets

---

## References

- [Azure DevOps Variable Groups](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups)
- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
