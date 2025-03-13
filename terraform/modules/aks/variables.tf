variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
}

variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "kubernetes_version" {
  description = "The version of Kubernetes"
  type        = string
}

variable "node_count" {
  description = "The number of nodes in the AKS cluster"
  type        = number
}

variable "node_size" {
  description = "The size of the AKS nodes"
  type        = string
}

variable "subnet_id" {
  description = "The ID of the subnet where AKS will be deployed"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
} 