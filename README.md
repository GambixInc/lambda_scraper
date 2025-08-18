# Lambda Scraper

A sophisticated, serverless web scraping tool built with Python that runs on AWS Lambda. Features advanced anti-bot protection and can scrape most websites with a simple API call.

## Features

- **Serverless**: Runs on AWS Lambda - no server management
- **Anti-Bot Protection**: Realistic browser headers, random delays, retry logic
- **Rate Limiting Handling**: Automatic handling of 429 responses with exponential backoff
- **Session Management**: Persistent connections for better performance
- **Robust Error Handling**: Comprehensive error handling with detailed logging
- **API Ready**: HTTP endpoints for easy integration
- **Auto-scaling**: Handles concurrent requests automatically
- **Cost-effective**: Pay per request
- **CORS Support**: Ready for web frontend integration
- **Enhanced Content Extraction**: Better text cleaning, meta data extraction
- **Configurable Retries**: Customizable retry attempts per request

## Anti-Bot Protection Features

### 🛡️ Realistic Browser Headers
- Rotating User-Agent strings from real browsers
- Complete set of modern browser headers (Accept, Accept-Language, etc.)
- Security headers (Sec-Fetch-*, Sec-Ch-Ua) to appear more legitimate

### ⏱️ Respectful Timing
- Random delays (1-3 seconds) before each request
- Longer delays for errors (2-7 seconds for timeouts, 3-7 for connection errors)
- Extended delays for rate limiting (10-20 seconds)

### 🔄 Smart Retry Logic
- Configurable retry attempts (default: 3, max: 5)
- Different delay strategies for different error types
- Automatic handling of HTTP 429 (rate limit) responses

### 🎯 Session Management
- Persistent HTTP sessions for better connection handling
- Proper connection pooling
- Automatic redirect following

## Quick Start

### 1. Prerequisites

- AWS CLI installed and configured
- Python 3.9+ installed
- AWS account with appropriate permissions

### 2. Configure AWS

Make sure your AWS CLI is configured:

```bash
aws configure
# or for a specific profile
aws configure --profile your-profile
```

### 3. Deploy to AWS Lambda

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

#### GET with Custom Retries:
```bash
curl "https://your-function-url.lambda-url.us-east-1.on.aws/?url=https://httpbin.org/html&retries=5"
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
    "description": "Meta description if available",
    "keywords": "Meta keywords if available",
    "content": "Extracted and cleaned text content...",
    "links": ["https://link1.com", "https://link2.com"],
    "content_length": 1234,
    "links_count": 15,
    "status_code": 200,
    "content_type": "text/html",
    "scraped_at": 1703123456.789,
    "scraper_version": "2.0",
    "scraper_features": [
      "anti-bot-protection",
      "realistic-headers",
      "retry-logic",
      "rate-limiting-handling"
    ]
  }
]
```

### Error Response (400/500):
```json
{
  "error": "Failed to scrape the URL",
  "url": "https://example.com",
  "message": "The scraper encountered an error or the website may be blocking automated access",
  "suggestions": [
    "Check if the URL is accessible in a browser",
    "The site may have anti-bot protection",
    "Try again later if the site is temporarily unavailable"
  ]
}
```

## Configuration

### Lambda Settings

**Recommended Configuration:**
- **Memory**: 1024 MB (recommended for better performance)
- **Timeout**: 5 minutes (300 seconds)
- **Runtime**: Python 3.9

### Query Parameters

- **url** (required): The URL to scrape
- **retries** (optional): Number of retry attempts (1-5, default: 3)

## What This Scraper Can Handle

### ✅ Basic Anti-Bot Protection
- Header validation checks
- Request frequency monitoring
- Simple bot pattern detection

### ✅ Rate Limiting
- Automatic detection of 429 responses
- Exponential backoff with random delays
- Retry logic with increasing delays

### ✅ Connection Issues
- Timeout handling with retries
- Connection error recovery
- Network instability handling

## What This Scraper Cannot Handle

### ❌ Advanced Protection
- JavaScript challenges requiring execution
- CAPTCHA systems
- Advanced browser fingerprinting
- IP-based rate limiting (same IP address)

### ❌ Dynamic Content
- JavaScript-rendered content
- Single Page Applications (SPAs)
- Content loaded via AJAX

## Project Structure

```
lambda_scraper/
├── lambda_function.py                   # Main Lambda function with anti-bot protection
├── requirements.txt                     # Python dependencies
├── deploy_python.sh                     # Deployment script
├── .gitignore                          # Git ignore file
└── README.md                           # This file
```

## Dependencies

- **requests==2.31.0** - HTTP client with session management
- **beautifulsoup4==4.12.2** - HTML parsing and content extraction
- **lxml==4.9.3** - XML/HTML parser (included with BeautifulSoup)

## Limitations

- **Lambda Timeout**: Maximum 15 minutes execution time
- **Memory**: Limited to 10GB RAM
- **Concurrent Executions**: Default limit of 1000 (can be increased)
- **JavaScript**: Does not handle JavaScript-rendered content
- **Complex Crawling**: Designed for single-page scraping
- **IP Rotation**: Uses Lambda's IP address (no proxy rotation)

## Troubleshooting

### Common Issues

1. **AWS CLI Not Installed**: Install AWS CLI first
2. **Credentials Not Configured**: Run `aws configure` or set environment variables
3. **Permission Errors**: Ensure your AWS user has the required permissions
4. **Timeout Errors**: Increase Lambda timeout or optimize scraping
5. **Memory Errors**: Increase Lambda memory allocation
6. **CORS Errors**: Check CORS configuration in Function URL
7. **Blocked by Website**: Some sites may still block Lambda IPs

### Logs

View Lambda execution logs in CloudWatch:
```bash
aws logs tail /aws/lambda/lambda-scraper-python --follow
```

## Cost Optimization

- **Memory**: Start with 1024MB for better performance
- **Timeout**: Set appropriate timeout (5 minutes is usually sufficient)
- **Concurrency**: Monitor and adjust based on usage patterns
- **Retries**: Limit retry attempts to avoid excessive costs

## Security Considerations

- **Input Validation**: Enhanced URL validation with scheme checking
- **Rate Limiting**: Built-in rate limiting handling
- **CORS**: Configure CORS properly for production use
- **VPC**: Consider running in VPC for additional security if needed
- **Headers**: Realistic headers help avoid detection but don't guarantee access