variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "microservices-demo"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
  default     = "eastus"
}

variable "kubernetes_version" {
  description = "The version of Kubernetes"
  type        = string
  default     = "1.27.7"
}

variable "node_count" {
  description = "The number of nodes in the AKS cluster"
  type        = number
  default     = 2
}

variable "node_size" {
  description = "The size of the AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "admin_username" {
  description = "The admin username for the AKS cluster"
  type        = string
  default     = "azureuser"
}

variable "vnet_address_space" {
  description = "The address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "aks_subnet_prefix" {
  description = "The subnet prefix for AKS"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
    Project     = "microservices-demo"
  }
} 