# Get current Azure client configuration
data "azurerm_client_config" "current" {}

# Create AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.project_name}-${var.environment}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version
  tags                = var.tags

  default_node_pool {
    name                = "default"
    node_count          = var.node_count
    vm_size             = var.node_size
    vnet_subnet_id      = var.subnet_id
    
    # Node pool configuration
    max_pods            = 30
    os_disk_size_gb     = 50
    type                = "VirtualMachineScaleSets"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = "azure"
    load_balancer_sku = "standard"
    network_policy    = "calico"
    service_cidr      = "172.16.0.0/16"  # Non-overlapping CIDR
    dns_service_ip    = "172.16.0.10"    # Must be within service_cidr
  }

  # Basic RBAC without AAD integration for simplicity
  role_based_access_control_enabled = true
} 