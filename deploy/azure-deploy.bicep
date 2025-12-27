@description('Container name')
param containerName string = 'insecure-banking'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Container image to deploy')
param containerImage string

@description('DNS name label for the container')
param dnsNameLabel string

@description('Number of CPU cores')
param cpuCores int = 1

@description('Memory in GB')
param memoryInGb int = 1

@description('Django secret key')
@secure()
param secretKey string

@description('Debug mode')
param debug string = 'False'

@description('Allowed hosts (comma-separated)')
param allowedHosts string

resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerName
  location: location
  properties: {
    containers: [
      {
        name: containerName
        properties: {
          image: containerImage
          ports: [
            {
              port: 8000
              protocol: 'TCP'
            }
          ]
          environmentVariables: [
            {
              name: 'SECRET_KEY'
              secureValue: secretKey
            }
            {
              name: 'DEBUG'
              value: debug
            }
            {
              name: 'ALLOWED_HOSTS'
              value: allowedHosts
            }
          ]
          resources: {
            requests: {
              cpu: cpuCores
              memoryInGB: memoryInGb
            }
          }
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'Always'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 8000
          protocol: 'TCP'
        }
      ]
      dnsNameLabel: dnsNameLabel
    }
  }
}

output containerIPv4Address string = containerGroup.properties.ipAddress.ip
output containerFQDN string = containerGroup.properties.ipAddress.fqdn
