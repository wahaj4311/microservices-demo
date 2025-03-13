# Terraform Infrastructure for Microservices Demo

This directory contains Terraform configurations to set up the Azure infrastructure for the microservices demo application.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0+)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (v2.30.0+)
- Azure subscription

## Getting Started

1. **Login to Azure**

   ```bash
   az login
   ```

2. **Initialize Terraform with local backend**

   ```bash
   terraform init
   ```

3. **Create a terraform.tfvars file (optional)**

   Create a `terraform.tfvars` file to override default variable values:

   ```hcl
   project_name = "your-project"
   environment = "dev"
   location = "eastus"
   ```

4. **Plan and Apply**

   ```bash
   terraform plan
   terraform apply
   ```

## Using Azure Storage as Backend

When you're ready to use Azure Storage as a backend for state management:

1. **Set up the Azure Storage Account**

   Run the provided script:

   ```bash
   ./setup-backend.sh
   ```

2. **Update main.tf**

   Comment out the local backend and uncomment the Azure backend:

   ```hcl
   # Comment this out
   # backend "local" {
   #   path = "terraform.tfstate"
   # }
   
   # Uncomment this
   backend "azurerm" {}
   ```

3. **Initialize with the backend config**

   ```bash
   terraform init -backend-config=backend.tfvars
   ```

## Modules

The infrastructure is organized into the following modules:

- **Networking**: Sets up the Virtual Network, Subnet, and Network Security Group
- **AKS**: Creates the Azure Kubernetes Service cluster

## Outputs

After applying the Terraform configuration, you'll get the following outputs:

- Resource Group name
- AKS Cluster name and ID
- Kubernetes configuration
- Virtual Network ID
- AKS Subnet ID 