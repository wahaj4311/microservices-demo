#!/bin/bash
set -e

# Variables
RESOURCE_GROUP_NAME="terraform-state-rg"
STORAGE_ACCOUNT_NAME="microservicedemo$RANDOM"
CONTAINER_NAME="microservice-demo"
LOCATION="eastus"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Create storage account
echo "Creating storage account..."
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob

# Get storage account key
echo "Getting storage account key..."
ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP_NAME --account-name $STORAGE_ACCOUNT_NAME --query '[0].value' -o tsv)

# Create blob container
echo "Creating blob container..."
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME --account-key $ACCOUNT_KEY

# Update backend.tfvars
echo "Updating backend.tfvars..."
cat > backend.tfvars << EOF
resource_group_name  = "$RESOURCE_GROUP_NAME"
storage_account_name = "$STORAGE_ACCOUNT_NAME"
container_name       = "$CONTAINER_NAME"
key                  = "terraform.tfstate"
EOF

echo "Storage account created: $STORAGE_ACCOUNT_NAME"
echo "To initialize Terraform with this backend, run:"
echo "terraform init -backend-config=backend.tfvars" 