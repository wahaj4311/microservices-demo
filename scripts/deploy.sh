#!/bin/bash

# Create secrets
echo "Creating secrets..."
kubectl create secret generic auth-secrets \
  --from-literal=jwt-secret=my-secret-key \
  --from-literal=database-url=postgresql://auth:password@localhost:5432/authdb

# Deploy services
echo "Deploying services..."
kubectl apply -f k8s/base/api-gateway/
kubectl apply -f k8s/base/auth-service/
kubectl apply -f k8s/base/product-service/
kubectl apply -f k8s/base/order-service/

# Check status
echo "Checking deployment status..."
kubectl get pods
kubectl get services 