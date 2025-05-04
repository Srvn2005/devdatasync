variable "region" {
  description = "AWS region to deploy resources"
  default     = "us-east-1"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
  type        = list(string)
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS node group"
  default     = ["t3.medium"]
  type        = list(string)
}

variable "node_disk_size" {
  description = "Disk size for EKS nodes in GB"
  default     = 20
  type        = number
}

variable "node_desired_capacity" {
  description = "Desired number of nodes in the EKS node group"
  default     = 2
  type        = number
}

variable "node_max_capacity" {
  description = "Maximum number of nodes in the EKS node group"
  default     = 4
  type        = number
}

variable "node_min_capacity" {
  description = "Minimum number of nodes in the EKS node group"
  default     = 2
  type        = number
}