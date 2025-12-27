#!/bin/bash
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Azure Container Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Azure CLI is not installed. Please install it first:${NC}"
    echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged into Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged into Azure. Running 'az login'...${NC}"
    az login
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}No .env file found. Using defaults or command-line arguments.${NC}"
fi

# Get configuration from environment or prompt user
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-insecure-banking-rg}
LOCATION=${AZURE_LOCATION:-eastus}
CONTAINER_NAME=${AZURE_CONTAINER_NAME:-insecure-banking}
DNS_NAME_LABEL=${AZURE_DNS_NAME_LABEL:-insecure-banking-$(date +%s)}
IMAGE_NAME="insecure-banking:latest"
ACR_NAME=""

echo
echo -e "${YELLOW}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Container Name: $CONTAINER_NAME"
echo "  DNS Label: $DNS_NAME_LABEL"
echo

# Prompt for Django secret key
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}Enter Django SECRET_KEY (or press Enter to generate one):${NC}"
    read SECRET_KEY
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -base64 48)
        echo -e "${GREEN}Generated SECRET_KEY: $SECRET_KEY${NC}"
    fi
fi

# Get allowed hosts
if [ -z "$ALLOWED_HOSTS" ]; then
    ALLOWED_HOSTS="$DNS_NAME_LABEL.$LOCATION.azurecontainer.io,*"
fi

DEBUG=${DEBUG:-False}

echo -e "${GREEN}Step 1: Creating or checking resource group...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output table

echo
echo -e "${GREEN}Step 2: Building and pushing Docker image...${NC}"
echo -e "${YELLOW}Choose deployment method:${NC}"
echo "1. Deploy from local Docker image (build locally)"
echo "2. Deploy from Azure Container Registry (recommended for production)"
echo "3. Deploy from Docker Hub"
read -p "Select option (1-3): " DEPLOY_METHOD

case $DEPLOY_METHOD in
    1)
        echo -e "${GREEN}Building Docker image locally...${NC}"
        GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        REPO_URL=$(git config --get remote.origin.url 2>/dev/null | sed 's/git@/https:\/\//; s/.com:/.com\//; s/\.git$//' || echo "")
        
        docker build \
            --build-arg GIT_COMMIT="$GIT_COMMIT" \
            --build-arg REPO_URL="$REPO_URL" \
            --file Dockerfile \
            --tag "$IMAGE_NAME" .
        
        echo -e "${YELLOW}Note: Local images need to be pushed to a registry for Azure Container Instances.${NC}"
        echo -e "${YELLOW}Consider using Azure Container Registry (option 2) for production deployments.${NC}"
        
        # For local deployment, we'll use Azure Container Registry
        read -p "Create and use Azure Container Registry? (y/n): " USE_ACR
        if [ "$USE_ACR" = "y" ]; then
            ACR_NAME="insecurebanking$(date +%s)"
            echo -e "${GREEN}Creating Azure Container Registry: $ACR_NAME${NC}"
            az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic --admin-enabled true
            
            echo -e "${GREEN}Logging into ACR...${NC}"
            az acr login --name "$ACR_NAME"
            
            echo -e "${GREEN}Tagging and pushing image to ACR...${NC}"
            docker tag "$IMAGE_NAME" "$ACR_NAME.azurecr.io/$IMAGE_NAME"
            docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME"
            
            IMAGE_NAME="$ACR_NAME.azurecr.io/$IMAGE_NAME"
        else
            echo -e "${RED}Cannot deploy local image without pushing to a registry. Exiting.${NC}"
            exit 1
        fi
        ;;
    2)
        read -p "Enter Azure Container Registry name (or leave empty to create new): " ACR_NAME
        if [ -z "$ACR_NAME" ]; then
            ACR_NAME="insecurebanking$(date +%s)"
            echo -e "${GREEN}Creating Azure Container Registry: $ACR_NAME${NC}"
            az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic --admin-enabled true
        fi
        
        echo -e "${GREEN}Building image with ACR...${NC}"
        GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        REPO_URL=$(git config --get remote.origin.url 2>/dev/null | sed 's/git@/https:\/\//; s/.com:/.com\//; s/\.git$//' || echo "")
        
        az acr build --registry "$ACR_NAME" --image "$IMAGE_NAME" \
            --build-arg GIT_COMMIT="$GIT_COMMIT" \
            --build-arg REPO_URL="$REPO_URL" \
            --file Dockerfile .
        
        IMAGE_NAME="$ACR_NAME.azurecr.io/$IMAGE_NAME"
        ;;
    3)
        read -p "Enter Docker Hub image name (e.g., username/insecure-banking:latest): " IMAGE_NAME
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}Step 3: Deploying container to Azure...${NC}"

# Get ACR credentials if using ACR
if [ ! -z "$ACR_NAME" ]; then
    ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)
    ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
    ACR_SERVER="$ACR_NAME.azurecr.io"
    
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$CONTAINER_NAME" \
        --image "$IMAGE_NAME" \
        --cpu 1 \
        --memory 1 \
        --registry-login-server "$ACR_SERVER" \
        --registry-username "$ACR_USERNAME" \
        --registry-password "$ACR_PASSWORD" \
        --dns-name-label "$DNS_NAME_LABEL" \
        --ports 8000 \
        --environment-variables \
            SECRET_KEY="$SECRET_KEY" \
            DEBUG="$DEBUG" \
            ALLOWED_HOSTS="$ALLOWED_HOSTS" \
        --output table
else
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$CONTAINER_NAME" \
        --image "$IMAGE_NAME" \
        --cpu 1 \
        --memory 1 \
        --dns-name-label "$DNS_NAME_LABEL" \
        --ports 8000 \
        --environment-variables \
            SECRET_KEY="$SECRET_KEY" \
            DEBUG="$DEBUG" \
            ALLOWED_HOSTS="$ALLOWED_HOSTS" \
        --output table
fi

echo
echo -e "${GREEN}Step 4: Getting container details...${NC}"
CONTAINER_IP=$(az container show --resource-group "$RESOURCE_GROUP" --name "$CONTAINER_NAME" --query "ipAddress.ip" -o tsv)
CONTAINER_FQDN=$(az container show --resource-group "$RESOURCE_GROUP" --name "$CONTAINER_NAME" --query "ipAddress.fqdn" -o tsv)

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${YELLOW}Access your application at:${NC}"
echo -e "  ${GREEN}http://$CONTAINER_FQDN:8000${NC}"
echo -e "  ${GREEN}http://$CONTAINER_IP:8000${NC}"
echo
echo -e "${YELLOW}Container Details:${NC}"
echo "  Name: $CONTAINER_NAME"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  FQDN: $CONTAINER_FQDN"
echo "  IP: $CONTAINER_IP"
echo

# Save configuration
cat > .env.deployment <<EOF
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP
AZURE_LOCATION=$LOCATION
AZURE_CONTAINER_NAME=$CONTAINER_NAME
AZURE_DNS_NAME_LABEL=$DNS_NAME_LABEL
CONTAINER_FQDN=$CONTAINER_FQDN
CONTAINER_IP=$CONTAINER_IP
SECRET_KEY=$SECRET_KEY
ACR_NAME=$ACR_NAME
EOF

echo -e "${GREEN}Deployment configuration saved to .env.deployment${NC}"
echo

if [ ! -z "$CLOUDFLARE_API_TOKEN" ] && [ ! -z "$CLOUDFLARE_ZONE_ID" ]; then
    echo -e "${YELLOW}Cloudflare DNS detected. Run ./deploy/setup-cloudflare.sh to configure DNS.${NC}"
else
    echo -e "${YELLOW}To configure Cloudflare DNS:${NC}"
    echo "1. Set CLOUDFLARE_API_TOKEN, CLOUDFLARE_ZONE_ID, and CLOUDFLARE_DOMAIN in .env"
    echo "2. Run ./deploy/setup-cloudflare.sh"
fi

echo
echo -e "${YELLOW}To view logs:${NC}"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo
echo -e "${YELLOW}To delete the deployment:${NC}"
echo "  az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes"
