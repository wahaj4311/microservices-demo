output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "aks_cluster_name" {
  description = "The name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_id" {
  description = "The ID of the AKS cluster"
  value       = module.aks.cluster_id
}

output "kube_config" {
  description = "The kubeconfig for the AKS cluster"
  value       = module.aks.kube_config
  sensitive   = true
}

output "vnet_id" {
  description = "The ID of the Virtual Network"
  value       = module.networking.vnet_id
}

output "aks_subnet_id" {
  description = "The ID of the AKS subnet"
  value       = module.networking.aks_subnet_id
}

# ACR Outputs
output "acr_name" {
  description = "The name of the Container Registry"
  value       = module.acr.acr_name
}

output "acr_login_server" {
  description = "The login server URL for the Container Registry"
  value       = module.acr.acr_login_server
}

# Monitoring Outputs
output "log_analytics_workspace_name" {
  description = "The name of the Log Analytics Workspace"
  value       = module.monitoring.workspace_name
}

output "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics Workspace"
  value       = module.monitoring.workspace_id
} 