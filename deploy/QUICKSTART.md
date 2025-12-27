# Quick Start: Deploy to Azure

Deploy this application to Azure Container Instances in just a few steps!

## 🚀 One-Command Deployment

```bash
# Clone the repository
git clone https://github.com/mighty-muffin/insecure-banking.git
cd insecure-banking

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings (or use defaults)

# Deploy!
cd deploy
chmod +x deploy-azure.sh
./deploy-azure.sh
```

That's it! Your application will be running in Azure.

## 🌐 Add Your Cloudflare Domain (Optional)

If you have a Cloudflare domain:

1. Get your Cloudflare API Token and Zone ID from [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Add them to `.env`:
   ```bash
   CLOUDFLARE_API_TOKEN=your-token-here
   CLOUDFLARE_ZONE_ID=your-zone-id
   CLOUDFLARE_DOMAIN=yourdomain.com
   CLOUDFLARE_SUBDOMAIN=bank
   ```
3. Run the Cloudflare setup:
   ```bash
   chmod +x setup-cloudflare.sh
   ./setup-cloudflare.sh
   ```

Your app will be accessible at `http://bank.yourdomain.com:8000`

## 📋 Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- Azure subscription (free tier works!)
- (Optional) Cloudflare account for custom domain

## 📖 Detailed Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Detailed configuration options
- Troubleshooting guide
- Cost optimization tips
- HTTPS setup with Cloudflare
- Advanced deployment scenarios

## 🎯 What Gets Deployed

- **Container Instance** running your application
- **Public IP** with automatic DNS name
- **Azure Container Registry** (optional) for your images
- **Cloudflare DNS** (optional) pointing to your container

## 💰 Cost Estimate

Running 24/7 with 1 CPU and 1 GB RAM:
- Approximately $30-40/month
- Can stop/start container to save costs during testing

## 🔒 Security Notes

⚠️ This is an **intentionally insecure** application for educational purposes.

For production use:
- Generate a strong SECRET_KEY
- Set DEBUG=False
- Use HTTPS (Cloudflare Tunnel recommended)
- Review security settings

## 🛠️ Management Commands

```bash
# View logs
az container logs --resource-group insecure-banking-rg --name insecure-banking

# Stop container
az container stop --resource-group insecure-banking-rg --name insecure-banking

# Delete deployment
az container delete --resource-group insecure-banking-rg --name insecure-banking --yes
```

## Need Help?

Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting and configuration options.
