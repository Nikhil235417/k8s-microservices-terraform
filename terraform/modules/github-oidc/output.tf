output "role_arn" {
  description = "ARN of the IAM role created for GitHub Actions to assume"
  value = aws_iam_role.github_actions.arn
}