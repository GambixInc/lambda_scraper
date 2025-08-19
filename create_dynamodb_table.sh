#!/bin/bash

# DynamoDB Table Creation Script for Website Scraper
# This script creates the DynamoDB table for storing website scrape data

set -e

# Configuration
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

echo "🗄️  Creating DynamoDB table for website scraper..."
echo "Table Name: $TABLE_NAME"
echo "Region: $REGION"

# Check if table already exists
echo "🔍 Checking if table '$TABLE_NAME' already exists..."
if $AWS_CMD dynamodb describe-table --table-name $TABLE_NAME --region $REGION &> /dev/null; then
    echo "✅ Table '$TABLE_NAME' already exists!"
    echo ""
    echo "📊 Table Details:"
    $AWS_CMD dynamodb describe-table --table-name $TABLE_NAME --region $REGION --query 'Table.{Name:TableName,Status:TableStatus,PartitionKey:KeySchema[0].AttributeName,SortKey:KeySchema[1].AttributeName,BillingMode:BillingModeSummary.BillingMode}' --output table
    exit 0
fi

# Create the table
echo "⚡ Creating DynamoDB table '$TABLE_NAME'..."

$AWS_CMD dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=project_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=project_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION

echo "⏳ Waiting for table to be created..."

# Wait for table to be active
$AWS_CMD dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION

echo "✅ DynamoDB table '$TABLE_NAME' created successfully!"

# Show table details
echo ""
echo "📊 Table Details:"
$AWS_CMD dynamodb describe-table --table-name $TABLE_NAME --region $REGION --query 'Table.{Name:TableName,Status:TableStatus,PartitionKey:KeySchema[0].AttributeName,SortKey:KeySchema[1].AttributeName,BillingMode:BillingModeSummary.BillingMode}' --output table

echo ""
echo "🔑 Table Schema:"
echo "  Partition Key: user_id (String) - User identifier for filtering"
echo "  Sort Key: project_id (String) - Unique project identifier"
echo "  Billing Mode: Pay per request (no provisioned capacity needed)"
echo ""
echo "📝 Usage Examples:"
echo "  Query all scrapes for a user:"
echo "    $AWS_CMD dynamodb query --table-name $TABLE_NAME --key-condition-expression 'user_id = :uid' --expression-attribute-values '{':uid':{'S':'user123'}}' --region $REGION"
echo ""
echo "  Get specific project:"
echo "    $AWS_CMD dynamodb get-item --table-name $TABLE_NAME --key '{'user_id':{'S':'user123'},'project_id':{'S':'proj_abc123'}}' --region $REGION"
echo ""
echo "  List all tables:"
echo "    $AWS_CMD dynamodb list-tables --region $REGION"
echo ""
echo "💡 Next Steps:"
echo "  1. Update Lambda IAM role to include DynamoDB permissions"
echo "  2. Add boto3 to requirements.txt"
echo "  3. Create dynamodb_helper.py module"
echo "  4. Update lambda_function.py to save data"
