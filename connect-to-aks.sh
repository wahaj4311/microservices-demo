#!/bin/bash
set -e

# Get resource group and cluster name from Terraform output
echo "Getting AKS cluster information from Terraform output..."
cd terraform
RESOURCE_GROUP=$(terraform output -raw resource_group_name)
CLUSTER_NAME=$(terraform output -raw aks_cluster_name)
ACR_NAME=$(terraform output -raw acr_name)
cd ..

# Get AKS credentials
echo "Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --overwrite-existing

# Check nodes
echo "Checking AKS nodes..."
kubectl get nodes

# Check pods
echo "Checking pods..."
kubectl get pods

# Check services
echo "Checking services..."
kubectl get services

# Ask if user wants to deploy the test application
read -p "Do you want to deploy a test application (nginx) to verify the AKS cluster? (y/n): " DEPLOY_TEST

if [[ "$DEPLOY_TEST" == "y" || "$DEPLOY_TEST" == "Y" ]]; then
  echo "Deploying test application..."
  kubectl apply -f test-deployment.yaml
  
  echo "Waiting for API Gateway external IP..."
  API_GATEWAY_IP=""
  TIMEOUT=300  # 5 minutes timeout
  START_TIME=$(date +%s)
  
  while [ -z "$API_GATEWAY_IP" ]; do
    API_GATEWAY_IP=$(kubectl get service api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    # Check if timeout has been reached
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
      echo "Timeout waiting for external IP. Please check the service status manually:"
      echo "kubectl get service api-gateway"
      break
    fi
    
    if [ -z "$API_GATEWAY_IP" ]; then
      echo "Waiting for API Gateway external IP... ($ELAPSED_TIME seconds elapsed)"
      sleep 10
    fi
  done
  
  if [ -n "$API_GATEWAY_IP" ]; then
    echo "API Gateway is accessible at: http://$API_GATEWAY_IP"
    echo "You can test the API Gateway with: curl http://$API_GATEWAY_IP"
  fi
fi

# Login to ACR
echo "Logging in to ACR..."
az acr login --name $ACR_NAME

echo "Your AKS cluster is ready! You can now deploy your microservices."
echo "Done!" 