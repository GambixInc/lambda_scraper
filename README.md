# Lambda Scraper

A sophisticated, serverless web scraping tool built with Python that runs on AWS Lambda. Features advanced anti-bot protection, comprehensive HTTP analysis, and detailed content extraction - combining the best of both scraping and curl-like functionality.

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
- **Comprehensive HTTP Analysis**: Full curl-like information including headers, timing, security
- **Content Structure Analysis**: Detailed breakdown of HTML elements and structure
- **Framework Detection**: Automatic detection of common web frameworks and libraries
- **Security Analysis**: Security headers and SSL information
- **Performance Metrics**: Response times and compression analysis

## Anti-Bot Protection Features

### 🛡️ Realistic Browser Headers
- **Rotating User-Agents**: Multiple real Mac browser User-Agent strings
- **Complete Header Set**: All modern browser headers including:
  - `Accept`, `Accept-Language`, `Accept-Encoding`
  - `DNT`, `Connection`, `Upgrade-Insecure-Requests`
  - `Sec-Fetch-*` headers for security
  - `Sec-Ch-Ua` headers for browser identification

### ⏱️ Respectful Timing
- **Random Delays**: 1-3 second random delays before each request
- **Smart Error Delays**: 
  - 2-5 seconds for timeouts
  - 3-7 seconds for connection errors
  - 10-20 seconds for rate limiting (429 responses)

### 🔄 Smart Retry Logic
- **Configurable Retries**: Default 3, max 5 attempts
- **Error-Specific Handling**: Different strategies for different error types
- **Rate Limit Detection**: Automatic handling of HTTP 429 responses

### 🎯 Session Management
- **Persistent Sessions**: Better connection handling with `requests.Session()`
- **Connection Pooling**: More efficient resource usage
- **Automatic Redirects**: Proper redirect following

## Comprehensive Data Collection

### 🌐 HTTP/Curl-like Information
- **Response Headers**: All HTTP headers including server, date, cache control
- **Security Headers**: X-Frame-Options, CSP, HSTS, XSS Protection
- **Performance Metrics**: Response time, compression status, chunked transfer
- **Redirect Analysis**: Redirect chain, final URL, redirect count
- **Cache Information**: ETags, cache control, expiration headers
- **Connection Details**: Keep-alive, transfer encoding, content encoding

### 📊 Content Analysis
- **Text Statistics**: Word count, character count, content length
- **HTML Structure**: Headings (H1-H6), paragraphs, lists, tables
- **Media Analysis**: Images, scripts, stylesheets, forms
- **Meta Data**: All meta tags, descriptions, keywords
- **Link Analysis**: Internal/external links, link count

### 🔍 Framework Detection
- **Frontend Frameworks**: React, Vue, Angular detection
- **CSS Frameworks**: Bootstrap and other CSS libraries
- **CMS Platforms**: WordPress, Drupal, Joomla detection
- **E-commerce**: Shopify, WooCommerce detection
- **JavaScript Libraries**: jQuery and other JS libraries

### 🛡️ Security Analysis
- **SSL/TLS**: HTTPS status, certificate information
- **Security Headers**: Complete security header analysis
- **Domain Analysis**: Domain, path, query parameters
- **Content Security**: CSP policies, XSS protection

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
The API returns an array with a single object containing comprehensive website analysis data.

```json
[
  {
    // ===== BASIC INFORMATION =====
    "url": "https://example.com",
    "title": "Page Title",
    "description": "Meta description if available",
    "keywords": "Meta keywords if available",
    "content": "Extracted and cleaned text content (truncated to 2000 chars)...",
    "links": ["https://link1.com", "https://link2.com"],
    "content_length": 1234,
    "links_count": 15,
    "status_code": 200,
    "content_type": "text/html",
    
    // ===== SCRAPER METADATA =====
    "scraped_at": 1703123456.789,
    "scraper_version": "2.0",
    "scraper_features": [
      "anti-bot-protection",
      "realistic-headers",
      "retry-logic",
      "rate-limiting-handling"
    ],
    
    // ===== HTTP/CURL-LIKE INFORMATION =====
    "curl_info": {
      "status_code": 200,
      "content_type": "text/html; charset=utf-8",
      "content_length": 3741,
      "encoding": "utf-8",
      "url_final": "https://example.com/",
      "redirected": false,
      "redirect_count": 0,
      "redirect_chain": [],
      "response_time_ms": 245.67,
      "server": "nginx/1.18.0",
      "date": "Mon, 18 Aug 2025 19:25:55 GMT",
      "last_modified": "Mon, 13 Jan 2025 20:11:20 GMT",
      "etag": "\"84238dfc8092e5d9c0dac8ef93371a07:1736799080.121134\"",
      "cache_control": "max-age=2891",
      "expires": "",
      "content_encoding": "gzip",
      "transfer_encoding": "",
      "connection": "keep-alive",
      "keep_alive": "",
      "all_headers": {
        "Accept-Ranges": "bytes",
        "Content-Type": "text/html",
        "ETag": "\"84238dfc8092e5d9c0dac8ef93371a07:1736799080.121134\"",
        "Last-Modified": "Mon, 13 Jan 2025 20:11:20 GMT",
        "Vary": "Accept-Encoding",
        "Content-Encoding": "gzip",
        "Cache-Control": "max-age=2891",
        "Date": "Mon, 18 Aug 2025 19:25:55 GMT",
        "Alt-Svc": "h3=\":443\"; ma=93600,h3-29=\":443\"; ma=93600",
        "Content-Length": "648",
        "Connection": "keep-alive"
      },
      "cookies": {},
      "is_compressed": true,
      "is_chunked": false,
      "has_cache_headers": true,
      "security_headers": {
        "x_frame_options": "",
        "x_content_type_options": "",
        "x_xss_protection": "",
        "strict_transport_security": "",
        "content_security_policy": "",
        "referrer_policy": ""
      }
    },
    
    // ===== ENHANCED SCRAPING DATA =====
    "meta_tags": {
      "viewport": "width=device-width, initial-scale=1",
      "robots": "index, follow",
      "author": "Example Author",
      "og:title": "Example Page Title",
      "og:description": "Example page description",
      "twitter:card": "summary_large_image"
    },
    "images": [
      {"src": "https://example.com/image1.jpg", "alt": "Image description"},
      {"src": "https://example.com/image2.png", "alt": "Another image"}
    ],
    "forms": [
      {"action": "/search", "method": "get"},
      {"action": "/contact", "method": "post"}
    ],
    "scripts": [
      "https://example.com/js/main.js",
      "https://cdn.example.com/jquery.min.js"
    ],
    "stylesheets": [
      "https://example.com/css/style.css",
      "https://cdn.example.com/bootstrap.min.css"
    ],
    
    // ===== CONTENT ANALYSIS =====
    "content_analysis": {
      "headings": {
        "h1": 1,
        "h2": 3,
        "h3": 5,
        "h4": 2,
        "h5": 0,
        "h6": 0
      },
      "paragraphs": 25,
      "lists": {
        "ul": 3,
        "ol": 1
      },
      "tables": 2,
      "divs": 45,
      "spans": 67,
      "images_count": 8,
      "forms_count": 2,
      "scripts_count": 5,
      "stylesheets_count": 3
    },
    
    // ===== FRAMEWORK DETECTION =====
    "framework_detection": {
      "jquery": true,
      "react": false,
      "vue": false,
      "angular": false,
      "bootstrap": true,
      "wordpress": false,
      "drupal": false,
      "joomla": false,
      "shopify": false,
      "woocommerce": false
    },
    
    // ===== TEXT STATISTICS =====
    "word_count": 1250,
    "character_count": 8500,
    
    // ===== URL ANALYSIS =====
    "has_ssl": true,
    "domain": "example.com",
    "path": "/",
    "query_params": {}
  }
]
```

### Complete Field Reference

#### **Basic Information Fields:**
- `url` (string): The original URL that was scraped
- `title` (string): Page title from `<title>` tag
- `description` (string): Meta description content
- `keywords` (string): Meta keywords content
- `content` (string): Cleaned text content (truncated to 2000 chars)
- `links` (array): Array of absolute URLs found on the page
- `content_length` (number): Length of extracted text content
- `links_count` (number): Number of unique links found
- `status_code` (number): HTTP status code
- `content_type` (string): Content-Type header value

#### **Scraper Metadata:**
- `scraped_at` (number): Unix timestamp when scraping occurred
- `scraper_version` (string): Version of the scraper
- `scraper_features` (array): List of enabled features

#### **HTTP/Curl Information (`curl_info` object):**
- `status_code` (number): HTTP response status code
- `content_type` (string): Full content type with charset
- `content_length` (number): Raw response content length in bytes
- `encoding` (string): Response encoding (utf-8, ISO-8859-1, etc.)
- `url_final` (string): Final URL after redirects
- `redirected` (boolean): Whether the request was redirected
- `redirect_count` (number): Number of redirects followed
- `redirect_chain` (array): Array of URLs in redirect chain
- `response_time_ms` (number): Response time in milliseconds
- `server` (string): Server header value
- `date` (string): Date header value
- `last_modified` (string): Last-Modified header value
- `etag` (string): ETag header value
- `cache_control` (string): Cache-Control header value
- `expires` (string): Expires header value
- `content_encoding` (string): Content-Encoding header value
- `transfer_encoding` (string): Transfer-Encoding header value
- `connection` (string): Connection header value
- `keep_alive` (string): Keep-Alive header value
- `all_headers` (object): Complete HTTP headers object
- `cookies` (object): Response cookies object
- `is_compressed` (boolean): Whether response is compressed
- `is_chunked` (boolean): Whether response uses chunked transfer
- `has_cache_headers` (boolean): Whether cache headers are present
- `security_headers` (object): Security-related headers

#### **Enhanced Scraping Data:**
- `meta_tags` (object): All meta tags with name/content pairs
- `images` (array): Array of image objects with src and alt
- `forms` (array): Array of form objects with action and method
- `scripts` (array): Array of script source URLs
- `stylesheets` (array): Array of stylesheet URLs

#### **Content Analysis (`content_analysis` object):**
- `headings` (object): Count of each heading level (h1-h6)
- `paragraphs` (number): Number of `<p>` elements
- `lists` (object): Count of unordered and ordered lists
- `tables` (number): Number of `<table>` elements
- `divs` (number): Number of `<div>` elements
- `spans` (number): Number of `<span>` elements
- `images_count` (number): Number of `<img>` elements
- `forms_count` (number): Number of `<form>` elements
- `scripts_count` (number): Number of `<script>` elements
- `stylesheets_count` (number): Number of stylesheet links

#### **Framework Detection (`framework_detection` object):**
- `jquery` (boolean): jQuery detected
- `react` (boolean): React detected
- `vue` (boolean): Vue.js detected
- `angular` (boolean): Angular detected
- `bootstrap` (boolean): Bootstrap detected
- `wordpress` (boolean): WordPress detected
- `drupal` (boolean): Drupal detected
- `joomla` (boolean): Joomla detected
- `shopify` (boolean): Shopify detected
- `woocommerce` (boolean): WooCommerce detected

#### **Text Statistics:**
- `word_count` (number): Number of words in content
- `character_count` (number): Number of characters in content

#### **URL Analysis:**
- `has_ssl` (boolean): Whether URL uses HTTPS
- `domain` (string): Extracted domain name
- `path` (string): URL path component
- `query_params` (object): URL query parameters

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

### ✅ Comprehensive Analysis
- Full HTTP header analysis
- Content structure breakdown
- Framework and technology detection
- Security header analysis
- Performance metrics

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
├── lambda_function.py                   # Main Lambda function with comprehensive analysis
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