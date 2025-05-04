output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.mess_eks_cluster.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_security_group.eks_cluster_sg.id
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = aws_eks_cluster.mess_eks_cluster.name
}

output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "frontend_repository_url" {
  description = "URL of the ECR repository for frontend"
  value       = aws_ecr_repository.mess_frontend.repository_url
}

output "backend_repository_url" {
  description = "URL of the ECR repository for backend"
  value       = aws_ecr_repository.mess_backend.repository_url
}

output "artifacts_bucket_name" {
  description = "Name of the S3 bucket for artifacts"
  value       = aws_s3_bucket.mess_artifacts.bucket
}

output "kubeconfig_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.mess_eks_cluster.name}"
}
