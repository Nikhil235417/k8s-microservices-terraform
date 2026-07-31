#VPC
output "vpc_id" {
  description = "VPC ID"
  value = module.vpc.vpc_id
}

#EKS
output "eks_cluster_endpoint" {
  description = "EKS Cluster Endpoint"
  value = module.eks.cluster_endpoint
}

output "eks_cluster_id" {
  description = "EKS Cluster ID"
  value = module.eks.cluster_id
}

output "eks_cluster_oidc_issuer_url" {
  description = "URL from emisor OIDC of cluster EKS"
  value = module.eks.cluster_oidc_issuer_url
}

#ECR
output "ecr_repository_urls" {
  description = "ECR Repository URL"
  value = module.ecr.repository_urls
}

#RDS
output "rds_endpoint" {
  description = "RDS Endpoint"
  value     = module.rds.db_endpoint
  sensitive = false
}

#ALB Controller
output "alb_controller_role_arn" {
  description = "IAM Role ARN for ALB Controller"
  value       = module.alb_controller.role_arn
}