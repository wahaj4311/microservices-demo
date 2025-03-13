# Create Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "workspace" {
  name                = "${var.project_name}-${var.environment}-workspace"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# Enable Container Insights for AKS
resource "azurerm_monitor_diagnostic_setting" "aks_diagnostics" {
  name                       = "${var.project_name}-${var.environment}-aks-diag"
  target_resource_id         = var.aks_cluster_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.workspace.id

  log {
    category = "kube-apiserver"
    enabled  = true
  }

  log {
    category = "kube-controller-manager"
    enabled  = true
  }

  log {
    category = "kube-scheduler"
    enabled  = true
  }

  log {
    category = "kube-audit"
    enabled  = true
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
} 