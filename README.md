# Lambda Scraper

A simple, serverless web scraping tool built with Python that runs on AWS Lambda. Can scrape any website with a simple API call.

## Features

- **Serverless**: Runs on AWS Lambda - no server management
- **Simple**: Single Python file with all dependencies
- **API Ready**: HTTP endpoints for easy integration
- **Auto-scaling**: Handles concurrent requests automatically
- **Cost-effective**: Pay per request
- **CORS Support**: Ready for web frontend integration
- **Error Handling**: Proper HTTP status codes and error messages
- **Fallback Support**: Uses requests/BeautifulSoup if Scrapy fails

## Quick Start

### 1. Prerequisites

- AWS CLI installed and configured
- Python 3.9+ installed
- AWS account with appropriate permissions

### 2. Setup AWS Configuration

Run the setup script to check your AWS configuration:

```bash
./setup.sh
```

This will:
- Check if AWS CLI is installed
- Verify AWS credentials are configured
- Test required permissions
- Create a `.env.example` file

### 3. Configure Environment Variables (Optional)

Copy the example environment file and customize if needed:

```bash
cp .env.example .env
```

Available environment variables:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Optional: Override function name
FUNCTION_NAME=lambda-scraper-python

# Optional: Override ECR repository name
ECR_REPO_NAME=lambda-scraper
```

### 4. Deploy to AWS Lambda

```bash
./deploy_python.sh --profile your-profile
```

This script will:
- Create deployment package with all dependencies
- Create/update Lambda function
- Enable Function URL with CORS
- Provide usage examples

## API Usage

### Function URL (Direct HTTPS endpoint)

#### GET with Query Parameter:
```bash
curl "https://your-function-url.lambda-url.us-east-1.on.aws/?url=https://httpbin.org/html"
```

#### POST with JSON Body:
```bash
curl -X POST https://your-function-url.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'
```

## Response Format

### Success Response (200):
```json
[
  {
    "url": "https://httpbin.org/html",
    "title": "Page Title",
    "content": "Extracted text content...",
    "links": ["https://link1.com", "https://link2.com"]
  }
]
```

### Error Response (400/500):
```json
{
  "error": "Missing URL parameter",
  "usage": "Provide url as query parameter (?url=https://example.com) or in request body"
}
```

## Configuration

### Lambda Settings

**Recommended Configuration:**
- **Memory**: 512 MB (minimum), 1024 MB (recommended)
- **Timeout**: 5 minutes (300 seconds)
- **Runtime**: Python 3.9

### Environment Variables

The deployment script supports these environment variables:

```bash
# Required for deployment
AWS_REGION=us-east-1                    # AWS region (default: us-east-1)
AWS_ACCOUNT_ID=123456789012             # AWS account ID (auto-detected if not set)

# Optional overrides
FUNCTION_NAME=lambda-scraper-python      # Lambda function name
```

### AWS Permissions Required

Your AWS user/role needs these permissions:

**Lambda:**
- `lambda:CreateFunction`
- `lambda:UpdateFunctionCode`
- `lambda:CreateFunctionUrlConfig`
- `lambda:GetFunctionUrlConfig`

**IAM:**
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `iam:GetRole`

**CloudWatch Logs:**
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

## Local Development

### Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test the function locally
python -c "
import lambda_function
result = lambda_function.lambda_handler({'url': 'https://httpbin.org/html'}, {})
print(result)
"
```

## Project Structure

```
lambda_scraper/
├── lambda_function.py                   # Main Lambda function
├── requirements.txt                     # Python dependencies
├── deploy_python.sh                     # Deployment script
├── setup.sh                            # AWS setup script
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore file
└── README.md                           # This file
```

## Dependencies

- **scrapy==2.11.0** - Main web scraping engine
- **requests==2.31.0** - HTTP client (fallback)
- **beautifulsoup4==4.12.2** - HTML parsing (fallback)
- **lxml==4.9.3** - XML/HTML parser

## Limitations

- **Lambda Timeout**: Maximum 15 minutes execution time
- **Memory**: Limited to 10GB RAM
- **Concurrent Executions**: Default limit of 1000 (can be increased)
- **JavaScript**: Does not handle JavaScript-rendered content
- **Complex Crawling**: Designed for single-page scraping

## Troubleshooting

### Common Issues

1. **AWS CLI Not Installed**: Install AWS CLI first
2. **Credentials Not Configured**: Run `aws configure` or set environment variables
3. **Permission Errors**: Ensure your AWS user has the required permissions
4. **Timeout Errors**: Increase Lambda timeout or optimize scraping
5. **Memory Errors**: Increase Lambda memory allocation
6. **CORS Errors**: Check CORS configuration in Function URL

### Logs

View Lambda execution logs in CloudWatch:
```bash
aws logs tail /aws/lambda/lambda-scraper-python --follow
```

## Cost Optimization

- **Memory**: Start with 512MB, increase if needed
- **Timeout**: Set appropriate timeout (5 minutes is usually sufficient)
- **Concurrency**: Monitor and adjust based on usage patterns

## Security Considerations

- **Input Validation**: URL validation is basic - consider adding more validation
- **Rate Limiting**: Consider adding API Gateway rate limiting
- **CORS**: Configure CORS properly for production use
- **VPC**: Consider running in VPC for additional security if needed