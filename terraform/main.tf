terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  # Use local backend initially for simplicity
  backend "local" {
    path = "terraform.tfstate"
  }
  # Uncomment this when you're ready to use Azure Storage as backend
  # backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

provider "random" {}

# Random string for unique names
resource "random_string" "random" {
  length  = 8
  special = false
  upper   = false
}

# Create a resource group
resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# Networking Module
module "networking" {
  source = "./modules/networking"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  vnet_address_space  = var.vnet_address_space
  aks_subnet_prefix   = var.aks_subnet_prefix
  tags                = var.tags
}

# AKS Module
module "aks" {
  source = "./modules/aks"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  kubernetes_version  = var.kubernetes_version
  node_count         = var.node_count
  node_size          = var.node_size
  subnet_id          = module.networking.aks_subnet_id
  tags               = var.tags

  depends_on = [module.networking]
}

# ACR Module
module "acr" {
  source = "./modules/acr"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  random_suffix       = random_string.random.result
  tags                = var.tags
}

# Grant AKS access to ACR
resource "azurerm_role_assignment" "aks_acr" {
  scope                = module.acr.acr_id
  role_definition_name = "AcrPull"
  principal_id         = module.aks.kubelet_identity.object_id

  depends_on = [module.aks, module.acr]
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  aks_cluster_id      = module.aks.cluster_id
  tags                = var.tags

  depends_on = [module.aks]
}
