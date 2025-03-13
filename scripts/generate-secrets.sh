#!/bin/bash
set -e

# Function to generate a random string
generate_random_string() {
    openssl rand -base64 32 | tr -d '/+=' | cut -c1-32
}

# Function to encode in base64
encode_base64() {
    echo -n "$1" | base64
}

# Generate secrets
JWT_SECRET=$(generate_random_string)
echo "Generated JWT Secret: $JWT_SECRET"

# Database URLs - using Azure PostgreSQL naming convention
AUTH_DB_URL="postgresql://auth@auth-db-server.postgres.database.azure.com:5432/authdb?sslmode=require"
PRODUCT_DB_URL="postgresql://product@product-db-server.postgres.database.azure.com:5432/productdb?sslmode=require"
ORDER_DB_URL="postgresql://order@order-db-server.postgres.database.azure.com:5432/orderdb?sslmode=require"

# Encode all values
JWT_SECRET_BASE64=$(encode_base64 "$JWT_SECRET")
AUTH_DB_URL_BASE64=$(encode_base64 "$AUTH_DB_URL")
PRODUCT_DB_URL_BASE64=$(encode_base64 "$PRODUCT_DB_URL")
ORDER_DB_URL_BASE64=$(encode_base64 "$ORDER_DB_URL")

# Create .env file
cat > .env << EOF
# Azure Container Registry
ACR_LOGIN_SERVER=microservicesdemodevacred7ulf27.azurecr.io

# Auth Service Secrets (base64 encoded)
JWT_SECRET_BASE64=$JWT_SECRET_BASE64  # Original: $JWT_SECRET
AUTH_DB_URL_BASE64=$AUTH_DB_URL_BASE64  # Original: $AUTH_DB_URL

# Product Service Secrets (base64 encoded)
PRODUCT_DB_URL_BASE64=$PRODUCT_DB_URL_BASE64  # Original: $PRODUCT_DB_URL

# Order Service Secrets (base64 encoded)
ORDER_DB_URL_BASE64=$ORDER_DB_URL_BASE64  # Original: $ORDER_DB_URL

# Note: Values above are base64 encoded. Original values are commented.
# To decode any value: echo "base64-string" | base64 -d
EOF

echo "Secrets generated and saved to .env file"
echo "Please update the database URLs in the .env file with your actual Azure PostgreSQL connection strings" 