# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  # Remove hyphens and convert to lowercase for valid ACR name
  name                = replace(lower("${var.project_name}${var.environment}acr${var.random_suffix}"), "-", "")
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
  admin_enabled       = true
  tags                = var.tags
} 