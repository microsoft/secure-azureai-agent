targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of the naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Resource group name')
param resourceGroupName string = 'rg-${environmentName}'

@description('Environment type (development, staging, production)')
param environment string = 'development'

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
  }
}

// Deploy unified app resources
module resources 'unified-resources.bicep' = {
  name: 'unified-resources'
  scope: rg
  params: {
    location: location
    environmentName: environmentName
    environment: environment
  }
}

// Outputs
output RESOURCE_GROUP_ID string = rg.id
output AZURE_OPENAI_ENDPOINT string = resources.outputs.AZURE_OPENAI_ENDPOINT
output AZURE_KEY_VAULT_URL string = resources.outputs.AZURE_KEY_VAULT_URL
output UNIFIED_APP_URI string = resources.outputs.UNIFIED_APP_URI
