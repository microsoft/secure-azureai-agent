param location string = resourceGroup().location
param environmentName string
param environment string = 'development'

// Resource token to create unique names
var resourceToken = uniqueString(subscription().id, location, environmentName)
var tags = { 'azd-env-name': environmentName }

// User-assigned managed identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'mi-${environmentName}-${resourceToken}'
  location: location
  tags: tags
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-${environmentName}-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${environmentName}-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${environmentName}-${take(resourceToken, 17)}'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
    enabledForDeployment: false
    enabledForDiskEncryption: false
  }
}

// Key Vault role assignment for managed identity
resource keyVaultSecretsOfficerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentity.id, '9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3') // Key Vault Secrets Officer
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Azure OpenAI Service
resource openAIService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'oai-${environmentName}-${resourceToken}'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'oai-${environmentName}-${resourceToken}'
    publicNetworkAccess: 'Enabled'
  }
}

// App Service Plan for unified app
resource appServicePlan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: 'asp-${environmentName}-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  properties: {
    reserved: true // Required for Linux
  }
  kind: 'linux'
}

// Unified App Service (FastAPI + Chainlit)
resource unifiedAppService 'Microsoft.Web/sites@2024-11-01' = {
  name: 'app-${environmentName}-unified-${resourceToken}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'bash startup.sh'
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      appSettings: [
        {
          name: 'ENVIRONMENT'
          value: environment
        }
        {
          name: 'CHAINLIT_PORT'
          value: '8501'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot/backend/src'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'AZURE_KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAIService.properties.endpoint
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
      ]
    }
  }
}

// Outputs
output AZURE_OPENAI_ENDPOINT string = openAIService.properties.endpoint
output AZURE_KEY_VAULT_URL string = keyVault.properties.vaultUri
output UNIFIED_APP_URI string = 'https://${unifiedAppService.properties.defaultHostName}'
output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsights.properties.ConnectionString
