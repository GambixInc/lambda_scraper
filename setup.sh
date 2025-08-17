#!/bin/bash

# Lambda Scraper Setup Script
# This script helps set up AWS configuration for deployment

# Parse command line arguments
AWS_PROFILE="${AWS_PROFILE:-}"
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            AWS_PROFILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile PROFILE     AWS profile to use"
            echo "  --help               Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  AWS_PROFILE          AWS profile to use"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build AWS CLI command with profile if specified
AWS_CMD="aws"
if [ -n "$AWS_PROFILE" ]; then
    AWS_CMD="aws --profile $AWS_PROFILE"
    echo "🔧 Using AWS profile: $AWS_PROFILE"
fi

echo "🔧 Lambda Scraper Setup"
echo "========================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed."
    echo ""
    echo "Please install AWS CLI first:"
    echo "  macOS: brew install awscli"
    echo "  Ubuntu/Debian: sudo apt-get install awscli"
    echo "  Or download from: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    echo ""
    exit 1
fi

echo "✅ AWS CLI is installed"

# Check if AWS credentials are configured
if $AWS_CMD sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials are configured"
    ACCOUNT_ID=$($AWS_CMD sts get-caller-identity --query Account --output text)
    USER_ARN=$($AWS_CMD sts get-caller-identity --query Arn --output text)
    echo "   Account ID: $ACCOUNT_ID"
    echo "   User: $USER_ARN"
else
    echo "❌ AWS credentials not configured for profile: ${AWS_PROFILE:-default}"
    echo ""
    echo "You need to configure AWS credentials. Choose an option:"
    echo ""
    if [ -n "$AWS_PROFILE" ]; then
        echo "1. Interactive setup for profile '$AWS_PROFILE':"
        echo "   aws configure --profile $AWS_PROFILE"
        echo ""
        echo "2. Environment variables:"
        echo "   export AWS_ACCESS_KEY_ID=your_access_key"
        echo "   export AWS_SECRET_ACCESS_KEY=your_secret_key"
        echo "   export AWS_DEFAULT_REGION=us-east-1"
        echo "   export AWS_PROFILE=$AWS_PROFILE"
    else
        echo "1. Interactive setup (recommended):"
        echo "   aws configure"
        echo ""
        echo "2. Environment variables:"
        echo "   export AWS_ACCESS_KEY_ID=your_access_key"
        echo "   export AWS_SECRET_ACCESS_KEY=your_secret_key"
        echo "   export AWS_DEFAULT_REGION=us-east-1"
    fi
    echo ""
    echo "3. AWS SSO (if using AWS SSO):"
    echo "   aws configure sso"
    echo ""
    exit 1
fi

# Check for required permissions
echo ""
echo "🔍 Checking AWS permissions..."

# Test ECR permissions
if $AWS_CMD ecr describe-repositories --max-items 1 &> /dev/null; then
    echo "✅ ECR access confirmed"
else
    echo "❌ ECR access denied. You need ECR permissions."
    echo "   Required permissions: ecr:CreateRepository, ecr:DescribeRepositories"
fi

# Test Lambda permissions
if $AWS_CMD lambda list-functions --max-items 1 &> /dev/null; then
    echo "✅ Lambda access confirmed"
else
    echo "❌ Lambda access denied. You need Lambda permissions."
    echo "   Required permissions: lambda:CreateFunction, lambda:UpdateFunctionCode"
fi

# Test IAM permissions
if $AWS_CMD iam list-roles --max-items 1 &> /dev/null; then
    echo "✅ IAM access confirmed"
else
    echo "❌ IAM access denied. You need IAM permissions."
    echo "   Required permissions: iam:CreateRole, iam:AttachRolePolicy"
fi

echo ""
echo "📋 Required AWS Permissions:"
echo "============================"
echo ""
echo "Your AWS user/role needs these permissions:"
echo ""
echo "ECR (Elastic Container Registry):"
echo "  - ecr:CreateRepository"
echo "  - ecr:DescribeRepositories"
echo "  - ecr:GetAuthorizationToken"
echo "  - ecr:BatchCheckLayerAvailability"
echo "  - ecr:GetDownloadUrlForLayer"
echo "  - ecr:BatchGetImage"
echo "  - ecr:InitiateLayerUpload"
echo "  - ecr:UploadLayerPart"
echo "  - ecr:CompleteLayerUpload"
echo "  - ecr:PutImage"
echo ""
echo "Lambda:"
echo "  - lambda:CreateFunction"
echo "  - lambda:UpdateFunctionCode"
echo "  - lambda:CreateFunctionUrlConfig"
echo "  - lambda:GetFunctionUrlConfig"
echo ""
echo "IAM:"
echo "  - iam:CreateRole"
echo "  - iam:AttachRolePolicy"
echo "  - iam:GetRole"
echo ""
echo "CloudWatch Logs:"
echo "  - logs:CreateLogGroup"
echo "  - logs:CreateLogStream"
echo "  - logs:PutLogEvents"
echo ""

# Create .env file template
echo "📝 Creating environment file template..."
cat > .env.example << EOF
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$ACCOUNT_ID
AWS_PROFILE=${AWS_PROFILE:-}

# Optional: Override function name
# FUNCTION_NAME=lambda-scraper

# Optional: Override ECR repository name
# ECR_REPO_NAME=lambda-scraper
EOF

echo "✅ Created .env.example file"
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. Copy .env.example to .env and customize if needed:"
echo "   cp .env.example .env"
echo ""
echo "2. Run the deployment:"
if [ -n "$AWS_PROFILE" ]; then
    echo "   ./deploy.sh --profile $AWS_PROFILE"
else
    echo "   ./deploy.sh"
fi
echo ""
echo "3. Test your deployed function (after deployment):"
echo "   curl \"https://your-function-url/?url=https://httpbin.org/html\""
echo ""
echo "📚 Documentation:"
echo "================="
echo "  - AWS CLI Setup: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
echo "  - AWS Profiles: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html"
echo "  - AWS Permissions: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html"
echo "  - Lambda Container Images: https://docs.aws.amazon.com/lambda/latest/dg/images-create.html"
