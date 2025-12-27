# Azure Deployment Guide

This guide will help you deploy the Insecure Banking application to Azure Container Instances with optional Cloudflare domain integration.

## Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- [Docker](https://docs.docker.com/get-docker/) installed (for local builds)
- Azure subscription
- (Optional) Cloudflare account with API token

## Quick Start

### 1. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```bash
# Required for production
SECRET_KEY=your-very-secure-secret-key-here

# Azure Configuration
AZURE_RESOURCE_GROUP=insecure-banking-rg
AZURE_LOCATION=eastus
AZURE_CONTAINER_NAME=insecure-banking
AZURE_DNS_NAME_LABEL=insecure-banking-unique

# Optional: Cloudflare Configuration
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_DOMAIN=yourdomain.com
CLOUDFLARE_SUBDOMAIN=bank
```

### 2. Deploy to Azure

Run the deployment script:

```bash
cd deploy
chmod +x deploy-azure.sh
./deploy-azure.sh
```

The script will:
1. Log you into Azure (if not already logged in)
2. Create or verify the resource group
3. Build and push your Docker image
4. Deploy the container to Azure Container Instances
5. Display the access URLs

### 3. (Optional) Configure Cloudflare DNS

If you have a Cloudflare domain:

```bash
chmod +x setup-cloudflare.sh
./setup-cloudflare.sh
```

This will automatically configure your Cloudflare DNS to point to your Azure container.

## Deployment Methods

The deployment script offers three methods:

### Method 1: Local Docker Build
- Builds the image locally
- Creates an Azure Container Registry
- Pushes the image to ACR
- Best for: Development and testing

### Method 2: Azure Container Registry (Recommended)
- Builds the image directly in Azure
- Uses Azure Container Registry
- No local Docker build required
- Best for: Production deployments

### Method 3: Docker Hub
- Uses a pre-existing image from Docker Hub
- No build required
- Best for: Using pre-built public images

## Azure Resources Created

The deployment creates the following resources:

- **Resource Group**: Container for all resources
- **Container Instance**: Runs your Docker container
- **Azure Container Registry** (optional): Stores your Docker images
- **Public IP**: Automatically assigned
- **DNS Name**: `<dns-label>.<location>.azurecontainer.io`

## Configuration Options

### Environment Variables

Set these in your `.env` file or pass them during deployment:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (required for production) | Auto-generated |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Auto-configured |
| `AZURE_RESOURCE_GROUP` | Azure resource group name | `insecure-banking-rg` |
| `AZURE_LOCATION` | Azure region | `eastus` |
| `AZURE_CONTAINER_NAME` | Container instance name | `insecure-banking` |
| `AZURE_DNS_NAME_LABEL` | DNS label (must be unique) | `insecure-banking-<timestamp>` |

### Resource Sizing

Modify in `deploy-azure.sh`:
- CPU: 1 core (can be increased)
- Memory: 1 GB (can be increased)

## Cloudflare Integration

### Getting Cloudflare Credentials

1. Log into your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your domain
3. Get your **Zone ID** from the right sidebar
4. Create an **API Token**:
   - Go to "My Profile" > "API Tokens"
   - Click "Create Token"
   - Use "Edit zone DNS" template
   - Select your specific zone
   - Create and copy the token

### DNS Configuration

The Cloudflare setup script will:
1. Create an A record pointing to your Azure container IP
2. Enable Cloudflare proxy (orange cloud) by default
3. Update your `.env` file with the new allowed hosts

### HTTPS with Cloudflare

For HTTPS access, you have several options:

#### Option 1: Cloudflare Flexible SSL (Easiest)
1. In Cloudflare Dashboard, go to SSL/TLS
2. Select "Flexible" SSL mode
3. Traffic is encrypted between browser and Cloudflare
4. Access your app at `https://bank.yourdomain.com:8000`

#### Option 2: Cloudflare Tunnel (Recommended)
1. Install cloudflared in your container
2. Configure a tunnel to your application
3. Full end-to-end encryption
4. No port number needed

#### Option 3: Disable Cloudflare Proxy
1. Set proxy to "DNS only" (gray cloud)
2. Configure SSL certificate in your Django application
3. Direct connection to Azure container

## Managing Your Deployment

### View Logs

```bash
az container logs --resource-group insecure-banking-rg --name insecure-banking
```

### Stream Logs

```bash
az container logs --resource-group insecure-banking-rg --name insecure-banking --follow
```

### Check Container Status

```bash
az container show --resource-group insecure-banking-rg --name insecure-banking --output table
```

### Update Environment Variables

```bash
az container create \
  --resource-group insecure-banking-rg \
  --name insecure-banking \
  --image your-image \
  --environment-variables SECRET_KEY="new-key" DEBUG="False"
```

Note: This requires redeployment. Update your `.env` and run `./deploy-azure.sh` again.

### Delete Deployment

```bash
az container delete --resource-group insecure-banking-rg --name insecure-banking --yes
```

### Delete Everything

```bash
az group delete --name insecure-banking-rg --yes
```

## Cost Considerations

Azure Container Instances pricing is based on:
- CPU cores per second
- Memory GB per second
- Running time

Typical costs for this application:
- 1 CPU, 1 GB RAM, running 24/7: ~$30-40/month
- Consider stopping containers when not in use for testing

Stop a container:
```bash
az container stop --resource-group insecure-banking-rg --name insecure-banking
```

Start a container:
```bash
az container start --resource-group insecure-banking-rg --name insecure-banking
```

## Troubleshooting

### Container won't start

Check logs:
```bash
az container logs --resource-group insecure-banking-rg --name insecure-banking
```

Common issues:
- Invalid SECRET_KEY
- Wrong ALLOWED_HOSTS configuration
- Image pull failures

### Cannot access application

1. Check container state:
   ```bash
   az container show --resource-group insecure-banking-rg --name insecure-banking
   ```

2. Verify IP and FQDN are accessible
3. Check firewall rules (Azure usually allows all by default)
4. Verify port 8000 is exposed

### Cloudflare DNS not working

1. Verify DNS record was created:
   - Check Cloudflare Dashboard > DNS
2. If using proxy (orange cloud):
   - May need to configure port forwarding
   - Or use Cloudflare Tunnel
3. Try DNS only mode (gray cloud) for testing

### Image build fails

1. Ensure Docker is running
2. Check network connectivity
3. Verify Azure CLI is logged in
4. Try method 2 (Azure Container Registry) instead

## Advanced Configuration

### Using Bicep Templates

For infrastructure as code, use the included Bicep template:

```bash
az deployment group create \
  --resource-group insecure-banking-rg \
  --template-file deploy/azure-deploy.bicep \
  --parameters \
    containerImage='your-registry.azurecr.io/insecure-banking:latest' \
    dnsNameLabel='insecure-banking-app' \
    secretKey='your-secret-key' \
    allowedHosts='your-domain.com'
```

### Using Docker Compose

For local testing before deployment:

```bash
docker-compose up -d
```

Access at http://localhost:8000

### Custom Domain (Non-Cloudflare)

1. Deploy to Azure
2. Note the container IP address
3. Create an A record in your DNS provider pointing to the Azure IP
4. Update ALLOWED_HOSTS in your `.env`
5. Redeploy

## Security Notes

⚠️ **This is an intentionally insecure application for educational purposes**

If using in production-like environments:
- Always use strong SECRET_KEY
- Set DEBUG=False
- Configure proper ALLOWED_HOSTS
- Use HTTPS (Cloudflare Tunnel or SSL certificate)
- Consider Azure Virtual Network for additional isolation
- Implement proper authentication and authorization
- Regular security updates

## Support

For issues or questions:
- Check Azure container logs
- Review the troubleshooting section
- Check Azure Container Instances documentation
- Review Cloudflare DNS documentation

## Additional Resources

- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)
- [Cloudflare API Documentation](https://api.cloudflare.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
