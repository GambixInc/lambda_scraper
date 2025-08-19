#!/bin/bash

# IAM Permissions Update Script for Lambda DynamoDB Access
# This script updates the Lambda execution role with DynamoDB permissions

set -e

# Configuration
ROLE_NAME="lambda-execution-role"
TABLE_NAME="website-scrapes"
REGION="${AWS_REGION:-us-east-1}"
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
        --role-name)
            ROLE_NAME="$2"
            shift 2
            ;;
        --table-name)
            TABLE_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile PROFILE     AWS profile to use"
            echo "  --region REGION       AWS region (default: us-east-1)"
            echo "  --role-name NAME      IAM role name (default: lambda-execution-role)"
            echo "  --table-name NAME     DynamoDB table name (default: website-scrapes)"
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

echo "🔐 Updating IAM permissions for Lambda DynamoDB access..."
echo "Role Name: $ROLE_NAME"
echo "Table Name: $TABLE_NAME"
echo "Region: $REGION"

# Check if role exists
echo "🔍 Checking if IAM role '$ROLE_NAME' exists..."
if ! $AWS_CMD iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "❌ IAM role '$ROLE_NAME' not found!"
    echo "Please create the Lambda execution role first using the deploy script."
    exit 1
fi

echo "✅ IAM role found: $ROLE_NAME"

# Create DynamoDB policy document
echo "📝 Creating DynamoDB policy document..."
cat > /tmp/dynamodb-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DescribeTable"
            ],
            "Resource": "arn:aws:dynamodb:${REGION}:*:table/${TABLE_NAME}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:ListTables"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
POLICY_NAME="${TABLE_NAME}-dynamodb-policy"
echo "⚡ Creating IAM policy '$POLICY_NAME'..."

# Check if policy already exists and get its ARN
POLICY_ARN=$($AWS_CMD iam list-policies --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text 2>/dev/null || echo "")

if [ -n "$POLICY_ARN" ] && [ "$POLICY_ARN" != "None" ]; then
    echo "ℹ️ Policy '$POLICY_NAME' already exists, updating..."
    
    # Create new policy version
    $AWS_CMD iam create-policy-version \
        --policy-arn "$POLICY_ARN" \
        --policy-document file:///tmp/dynamodb-policy.json \
        --set-as-default
    
    echo "✅ Updated existing policy '$POLICY_NAME'"
else
    # Create new policy
    POLICY_RESPONSE=$($AWS_CMD iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document file:///tmp/dynamodb-policy.json \
        --description "DynamoDB access policy for $TABLE_NAME table")
    
    # Extract the policy ARN from the response
    POLICY_ARN=$(echo "$POLICY_RESPONSE" | jq -r '.Policy.Arn')
    
    echo "✅ Created new policy '$POLICY_NAME'"
fi

# Attach policy to role
echo "🔗 Attaching policy to role..."
$AWS_CMD iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn "$POLICY_ARN"

echo "✅ Attached DynamoDB policy to role '$ROLE_NAME'"

# Verify the role has the policy
echo "🔍 Verifying role permissions..."
ATTACHED_POLICIES=$($AWS_CMD iam list-attached-role-policies --role-name $ROLE_NAME --query 'AttachedPolicies[].PolicyName' --output text)

echo "📋 Current attached policies for role '$ROLE_NAME':"
for policy in $ATTACHED_POLICIES; do
    echo "  - $policy"
done

# Clean up temporary file
rm -f /tmp/dynamodb-policy.json

echo ""
echo "✅ IAM permissions updated successfully!"
echo ""
echo "🔑 DynamoDB Permissions Added:"
echo "  - GetItem: Read individual items"
echo "  - PutItem: Create new items"
echo "  - UpdateItem: Update existing items"
echo "  - DeleteItem: Delete items"
echo "  - Query: Query items by key"
echo "  - Scan: Scan all items (limited)"
echo "  - DescribeTable: Get table information"
echo "  - ListTables: List available tables"
echo ""
echo "📝 Table Access:"
echo "  - Table: $TABLE_NAME"
echo "  - Region: $REGION"
echo ""
echo "💡 Next Steps:"
echo "  1. Test DynamoDB connectivity: python dynamodb_helper.py"
echo "  2. Update lambda_function.py to use DynamoDB"
echo "  3. Deploy updated Lambda function"
