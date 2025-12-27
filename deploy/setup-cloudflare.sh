#!/bin/bash
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cloudflare DNS Setup Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if curl/jq is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}curl is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq is not installed. Please install it first.${NC}"
    echo "Install with: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment from .env file...${NC}"
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
fi

if [ -f .env.deployment ]; then
    echo -e "${GREEN}Loading deployment configuration...${NC}"
    set -a
    # shellcheck source=/dev/null
    source .env.deployment
    set +a
fi

# Check required variables
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo -e "${RED}CLOUDFLARE_API_TOKEN is not set. Please set it in .env file.${NC}"
    exit 1
fi

if [ -z "$CLOUDFLARE_ZONE_ID" ]; then
    echo -e "${RED}CLOUDFLARE_ZONE_ID is not set. Please set it in .env file.${NC}"
    exit 1
fi

if [ -z "$CLOUDFLARE_DOMAIN" ]; then
    echo -e "${RED}CLOUDFLARE_DOMAIN is not set. Please set it in .env file.${NC}"
    exit 1
fi

SUBDOMAIN=${CLOUDFLARE_SUBDOMAIN:-bank}
FULL_DOMAIN="$SUBDOMAIN.$CLOUDFLARE_DOMAIN"

if [ -z "$CONTAINER_IP" ]; then
    echo -e "${YELLOW}CONTAINER_IP not found in .env.deployment${NC}"
    read -p "Enter the Azure Container IP address: " CONTAINER_IP
fi

echo
echo -e "${YELLOW}Configuration:${NC}"
echo "  Domain: $FULL_DOMAIN"
echo "  Target IP: $CONTAINER_IP"
echo "  Zone ID: ${CLOUDFLARE_ZONE_ID:0:10}..."
echo

# Create or update DNS record
echo -e "${GREEN}Checking for existing DNS records...${NC}"

# Get existing record ID if it exists
RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records?name=$FULL_DOMAIN&type=A" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" | jq -r '.result[0].id // empty')

if [ -n "$RECORD_ID" ] && [ "$RECORD_ID" != "null" ]; then
    echo -e "${YELLOW}Existing A record found. Updating...${NC}"
    RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records/$RECORD_ID" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{
            \"type\": \"A\",
            \"name\": \"$SUBDOMAIN\",
            \"content\": \"$CONTAINER_IP\",
            \"ttl\": 1,
            \"proxied\": true
        }")
else
    echo -e "${GREEN}Creating new A record...${NC}"
    RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{
            \"type\": \"A\",
            \"name\": \"$SUBDOMAIN\",
            \"content\": \"$CONTAINER_IP\",
            \"ttl\": 1,
            \"proxied\": true
        }")
fi

# Check if successful
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')

if [ "$SUCCESS" = "true" ]; then
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}DNS Configuration Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "${YELLOW}Your domain is now configured:${NC}"
    echo -e "  ${GREEN}http://$FULL_DOMAIN:8000${NC}"
    echo
    echo -e "${YELLOW}Note: If using Cloudflare proxy (orange cloud), you'll need to:${NC}"
    echo "1. Set up a Cloudflare Tunnel, or"
    echo "2. Disable proxy (gray cloud) and use DNS only mode"
    echo "3. Or configure port forwarding rules in Cloudflare"
    echo
    echo -e "${YELLOW}For HTTPS access:${NC}"
    echo "1. Consider using Cloudflare Tunnel for automatic HTTPS"
    echo "2. Or disable proxy and add SSL certificate to your container"
    echo "3. Or use Cloudflare Flexible SSL (encrypts traffic between browser and Cloudflare)"
    echo
    
    # Update .env file with domain
    if [ -f .env ]; then
        # Use a backup file for cross-platform compatibility
        if grep -q "ALLOWED_HOSTS=" .env; then
            sed -i.bak "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$FULL_DOMAIN,*.azurecontainer.io|" .env && rm -f .env.bak
        else
            echo "ALLOWED_HOSTS=$FULL_DOMAIN,*.azurecontainer.io" >> .env
        fi
        echo -e "${GREEN}Updated ALLOWED_HOSTS in .env file${NC}"
    fi
    
else
    echo -e "${RED}Failed to configure DNS record${NC}"
    echo "Response: $RESPONSE" | jq '.'
    exit 1
fi
