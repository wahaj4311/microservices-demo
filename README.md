# Microservices Demo on Azure Kubernetes Service (AKS)

This project demonstrates a microservices architecture deployed on Azure Kubernetes Service (AKS) with a complete CI/CD pipeline using Azure DevOps.

## Setting up Azure DevOps Agent

To set up the self-hosted Azure DevOps agent:

1. Set the required environment variables:
   ```bash
   export AZURE_DEVOPS_ORG='your-org-name'  # e.g., 'umairgl123'
   export AZURE_DEVOPS_PAT='your-pat-token'  # Your Personal Access Token
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup-agent.sh
   ```

   The script will:
   - Install necessary dependencies
   - Download and configure the Azure DevOps agent
   - Install and start the agent service

3. Verify the agent is running:
   ```bash
   sudo ./svc.sh status
   ```

**Important**: Never commit sensitive information like PAT tokens to the repository. Always use environment variables for sensitive data.

## Architecture

The application consists of the following microservices:

- **API Gateway**: Entry point for all client requests
- **Auth Service**: Handles authentication and authorization
- **Product Service**: Manages product data
- **Order Service**: Processes orders

## Infrastructure

The infrastructure is provisioned using Terraform and includes:

- **Azure Kubernetes Service (AKS)**: For orchestrating the microservices
- **Azure Container Registry (ACR)**: For storing Docker images
- **Virtual Network**: For secure networking
- **Azure Monitor**: For monitoring and logging

## Directory Structure

```
├── api-gateway/           # API Gateway service
├── auth-service/          # Authentication service
├── product-service/       # Product management service
├── order-service/         # Order processing service
├── k8s/                   # Kubernetes manifests
├── terraform/             # Terraform infrastructure code
│   ├── modules/           # Terraform modules
│   │   ├── aks/           # AKS module
│   │   ├── acr/           # ACR module
│   │   ├── networking/    # Networking module
│   │   └── monitoring/    # Monitoring module
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Terraform variables
│   └── outputs.tf         # Terraform outputs
├── azure-pipelines.yml    # Azure DevOps pipeline configuration
├── connect-to-aks.sh      # Script to connect to AKS cluster
└── README.md              # This file
```

## Getting Started

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Terraform](https://www.terraform.io/downloads.html)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Docker](https://docs.docker.com/get-docker/)
- Azure subscription

### Deploying the Infrastructure

1. **Login to Azure**

   ```bash
   az login
   ```

2. **Initialize Terraform**

   ```bash
   cd terraform
   terraform init
   ```

3. **Apply Terraform Configuration**

   ```bash
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

4. **Connect to AKS Cluster**

   ```bash
   ../connect-to-aks.sh
   ```

### Setting Up CI/CD Pipeline

1. Create a project in Azure DevOps
2. Import this repository
3. Create service connections to Azure and AKS
4. Set up the pipeline using the `azure-pipelines.yml` file

## Development

### Building and Running Locally

Each microservice can be built and run locally using Docker:

```bash
# Build API Gateway
cd api-gateway
docker build -t api-gateway .
docker run -p 8080:80 api-gateway
```

### Deploying to AKS Manually

You can deploy the microservices to AKS manually using kubectl:

```bash
kubectl apply -f k8s/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Microsoft Azure Documentation
- Kubernetes Documentation
- Terraform Documentation
