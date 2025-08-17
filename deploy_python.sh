#!/bin/bash

# Python Lambda Scraper Deployment Script
# This script deploys a simple Python Lambda function (no Docker needed)

set -e

# Configuration
FUNCTION_NAME="lambda-scraper-python"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"
AWS_PROFILE="${AWS_PROFILE:-}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            AWS_PROFILE="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --function-name)
            FUNCTION_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile PROFILE     AWS profile to use"
            echo "  --region REGION       AWS region (default: us-east-1)"
            echo "  --function-name NAME  Lambda function name (default: lambda-scraper-python)"
            echo "  --help               Show this help message"
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

echo "🚀 Deploying Python Lambda Scraper to AWS..."
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"

# Get account ID if not provided
if [ -z "$ACCOUNT_ID" ]; then
    echo "🔍 Getting AWS Account ID..."
    ACCOUNT_ID=$($AWS_CMD sts get-caller-identity --query Account --output text)
fi

# Check for required IAM role
echo "🔍 Checking for Lambda execution role..."
ROLE_NAME="lambda-execution-role"
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

if ! $AWS_CMD iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "⚠️  Lambda execution role '$ROLE_NAME' not found."
    echo "Creating basic Lambda execution role..."
    
    # Create trust policy
    cat > /tmp/trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    # Create role
    $AWS_CMD iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Basic Lambda execution role for lambda-scraper"

    # Attach basic execution policy
    $AWS_CMD iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    echo "✅ Created Lambda execution role: $ROLE_NAME"
    rm /tmp/trust-policy.json
else
    echo "✅ Lambda execution role found: $ROLE_NAME"
fi

# Create deployment package
echo "📦 Creating deployment package..."
rm -rf deployment-package
mkdir -p deployment-package

# Install dependencies
pip install -r requirements.txt -t deployment-package/

# Copy function code
cp lambda_function.py deployment-package/

# Create ZIP file
cd deployment-package
zip -r ../lambda-scraper.zip .
cd ..

echo "✅ Created deployment package: lambda-scraper.zip"

# Create or update Lambda function
echo "⚡ Creating/updating Lambda function..."
FUNCTION_EXISTS=$($AWS_CMD lambda list-functions --region $REGION --query "Functions[?FunctionName=='$FUNCTION_NAME'].FunctionName" --output text)

if [ -z "$FUNCTION_EXISTS" ]; then
    echo "Creating new Lambda function..."
    $AWS_CMD lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://lambda-scraper.zip \
        --timeout 300 \
        --memory-size 1024 \
        --region $REGION
else
    echo "Updating existing Lambda function..."
    $AWS_CMD lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-scraper.zip \
        --region $REGION
fi

# Enable Function URL
echo "🌐 Enabling Function URL..."
$AWS_CMD lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --cors '{
        "AllowCredentials": false,
        "AllowHeaders": ["*"],
        "AllowMethods": ["*"],
        "AllowOrigins": ["*"],
        "ExposeHeaders": ["*"],
        "MaxAge": 86400
    }' \
    --region $REGION 2>/dev/null || echo "Function URL already exists"

# Get Function URL
echo "🔗 Getting Function URL..."
FUNCTION_URL=$($AWS_CMD lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION --query FunctionUrl --output text)

# Clean up
rm -rf deployment-package lambda-scraper.zip

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Function URL: $FUNCTION_URL"
echo ""
echo "📝 Usage Examples:"
echo "GET: curl \"$FUNCTION_URL?url=https://httpbin.org/html\""
echo "POST: curl -X POST $FUNCTION_URL -H \"Content-Type: application/json\" -d '{\"url\": \"https://httpbin.org/html\"}'"
echo ""
echo "📊 Monitor logs: $AWS_CMD logs tail /aws/lambda/$FUNCTION_NAME --follow"
