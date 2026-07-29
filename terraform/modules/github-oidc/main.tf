provider aws {
  region = "us-east-1"
}

# ====================================================================
# 1. OIDC Provider - AWS trusts GitHub as an identity provider
# ====================================================================

resource "aws_iam_openid_connect_provider" "github" {
    url = "https://token.actions.githubusercontent.com"
    client_id_list = [
        "sts.amazonaws.com"
    ]
    thumbprint_list = [
        "6938fd4d98bab03faadb97b34396831e3780aea1"
    ]
}

# ====================================================================
# 2. IAM Role - AWS role that GitHub Actions can assume
# ====================================================================

resource "aws_iam_role" "github_actions" {
    name = "github-actions-ecr-push"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Principal = {
                    Federated = aws_iam_openid_connect_provider.github.arn
                }
                Action = "sts:AssumeRoleWithWebIdentity"
                Condition = {
                    StringEquals = {
                        "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
                    }
                    StringLike = {
                        "token.actions.githubusercontent.com:sub" = "repo:robpalacios1@40041666/k8s-microservices-terraform@1307833115:environment:dev"
                    }
                }
            }
        ]
    })

    tags = {
        Name = "github-actions-ecr-push"
        Environment = "dev"
    }
}

# ====================================================================
# 3. Permisons - Attach policies to the IAM role for ECR access
# ====================================================================

resource "aws_iam_role_policy" "ecr_push" {
    name = "ecr-push-policy"
    role = aws_iam_role.github_actions.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "ecr:GetAuthorizationToken"
                ]
                Resource = "*"
            },
            {
                Effect = "Allow"
                Action = [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload"
                ]
                Resource = "*"
            }
        ]
    })
}