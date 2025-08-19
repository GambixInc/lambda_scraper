# Website Scraper API Guide for Frontend Developers

## Overview

This API provides comprehensive website scraping capabilities with automatic data persistence to DynamoDB. The scraper includes anti-bot protection features and returns detailed information about scraped websites.

## Base URL

```
https://your-lambda-function-url.lambda-url.us-east-1.on.aws/
```

## Authentication

No authentication required - the API uses `user_id` parameter for data organization.

## API Endpoints

### Dual-Mode API

**Endpoint:** `POST /` or `GET /`

This API supports two modes of operation:

1. **Create New Scrape** - When both `url` and `user_id` are provided
2. **Get User Projects** - When only `user_id` is provided

The API automatically detects which mode to use based on the parameters provided.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ | Unique identifier for the user (used for DynamoDB filtering) |
| `url` | string | ❌ | The website URL to scrape (required for new scrapes, omit for getting projects) |
| `retries` | number | ❌ | Number of retry attempts (1-5, default: 3, only for new scrapes) |

#### Request Examples

**Mode 1: Create New Scrape**

**GET Request:**
```
GET /?url=https://example.com&user_id=user123&retries=3
```

**POST Request:**
```json
{
  "url": "https://example.com",
  "user_id": "user123",
  "retries": 3
}
```

**Mode 2: Get User Projects**

**GET Request:**
```
GET /?user_id=user123
```

**POST Request:**
```json
{
  "user_id": "user123"
}
```

#### Response Format

**Mode 1: Create New Scrape Response**

The API returns an array with one object containing the scrape results:

```json
[
  {
    "url": "https://example.com",
    "title": "Example Domain",
    "content": "This domain is for use in illustrative examples...",
    "project_id": "proj_1755608050_30e172ad",
    "saved_to_dynamodb": true,
    "scraped_at": 1755608050,
    "scraper_version": "2.0",
    "scraper_features": [
      "anti-bot-protection",
      "realistic-headers", 
      "retry-logic",
      "rate-limiting-handling"
    ],
    "curl_info": {
      "status_code": 200,
      "content_type": "text/html; charset=UTF-8",
      "content_length": 1256,
      "encoding": "UTF-8",
      "url_final": "https://example.com/",
      "redirected": false,
      "redirect_count": 0,
      "redirect_chain": [],
      "response_time_ms": 245.67,
      "headers": {
        "server": "ECS (nyb/1D2E)",
        "content-type": "text/html; charset=UTF-8",
        "content-length": "1256"
      },
      "cookies": {},
      "compression": "gzip",
      "cache_headers": {
        "cache-control": "max-age=604800"
      },
      "security_headers": {
        "x-content-type-options": "nosniff"
      }
    },
    "meta_tags": {
      "description": "Example domain for use in illustrative examples",
      "keywords": "example, domain",
      "viewport": "width=device-width, initial-scale=1",
      "robots": "index, follow"
    },
    "images": [
      {
        "src": "/images/example.jpg",
        "alt": "Example image",
        "title": "Example"
      }
    ],
    "forms": [
      {
        "action": "/submit",
        "method": "POST",
        "inputs": [
          {"name": "email", "type": "email"},
          {"name": "submit", "type": "submit"}
        ]
      }
    ],
    "scripts": [
      {
        "src": "/js/main.js",
        "type": "text/javascript"
      }
    ],
    "stylesheets": [
      {
        "href": "/css/style.css",
        "rel": "stylesheet"
      }
    ],
    "content_analysis": {
      "headings": {
        "h1": 1,
        "h2": 3,
        "h3": 5
      },
      "paragraphs": 12,
      "lists": 2,
      "tables": 1,
      "divs": 25,
      "spans": 18,
      "images": 5,
      "forms": 1,
      "scripts": 3,
      "stylesheets": 2
    },
    "framework_detection": {
      "jquery": false,
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
    "word_count": 1250,
    "character_count": 8750,
    "has_ssl": true,
    "domain": "example.com",
    "path": "/",
    "query_params": {}
  }
]

**Mode 2: Get User Projects Response**

The API returns an object containing the user's projects:

```json
{
  "mode": "retrieve",
  "user_id": "user123",
  "projects": [
    {
      "user_id": "user123",
      "project_id": "proj_1755608050_30e172ad",
      "url": "https://example.com",
      "scraped_at": 1755608050,
      "status": "success",
      "scrape_data": {
        "url": "https://example.com",
        "title": "Example Domain",
        "content": "This domain is for use in illustrative examples...",
        "word_count": 1250,
        "character_count": 8750,
        "curl_info": {
          "status_code": 200,
          "response_time_ms": 245.67
        },
        "framework_detection": {
          "bootstrap": true,
          "wordpress": false
        }
      }
    },
    {
      "user_id": "user123",
      "project_id": "proj_1755608000_abc12345",
      "url": "https://another-example.com",
      "scraped_at": 1755608000,
      "status": "success",
      "scrape_data": {
        "url": "https://another-example.com",
        "title": "Another Example",
        "content": "Another example website content...",
        "word_count": 800,
        "character_count": 5600,
        "curl_info": {
          "status_code": 200,
          "response_time_ms": 189.23
        },
        "framework_detection": {
          "bootstrap": false,
          "wordpress": true
        }
      }
    }
  ],
  "count": 2
}
```

#### Response Fields Explained

**Mode 1: Create New Scrape Fields**

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | The scraped URL |
| `title` | string | Page title |
| `content` | string | Clean text content |
| `project_id` | string | Unique identifier for this scrape (used for DynamoDB) |
| `saved_to_dynamodb` | boolean | Whether data was successfully saved to database |
| `scraped_at` | number | Unix timestamp when scraping occurred |
| `scraper_version` | string | Version of the scraper |
| `scraper_features` | array | List of enabled features |

**Mode 2: Get User Projects Fields**

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | Always "retrieve" for this mode |
| `user_id` | string | The user ID that was requested |
| `projects` | array | Array of user's scrape projects |
| `count` | number | Total number of projects returned |

**CURL Information (`curl_info`):**
- `status_code`: HTTP response status
- `content_type`: MIME type of response
- `content_length`: Size of response in bytes
- `encoding`: Character encoding
- `url_final`: Final URL after redirects
- `redirected`: Whether redirects occurred
- `redirect_count`: Number of redirects
- `redirect_chain`: Array of redirect URLs
- `response_time_ms`: Response time in milliseconds
- `headers`: All response headers
- `cookies`: Response cookies
- `compression`: Compression type used
- `cache_headers`: Cache-related headers
- `security_headers`: Security-related headers

**Content Analysis (`content_analysis`):**
- Counts of HTML elements (headings, paragraphs, lists, etc.)
- Useful for understanding page structure

**Framework Detection (`framework_detection`):**
- Boolean flags for common frameworks and CMS platforms
- Helps identify the technology stack

**Page Statistics:**
- `word_count`: Number of words in content
- `character_count`: Number of characters
- `has_ssl`: Whether HTTPS is used
- `domain`: Extracted domain name
- `path`: URL path
- `query_params`: URL query parameters

#### Error Responses

**400 Bad Request - Missing Parameters:**
```json
{
  "error": "Missing user_id parameter",
  "usage": "Provide user_id as query parameter (?user_id=your_user_id) or in request body",
  "example": {
    "GET": "?url=https://example.com&user_id=your_user_id",
    "POST": "{"url": "https://example.com", "user_id": "your_user_id"}"
  }
}
```

**400 Bad Request - Invalid URL:**
```json
{
  "error": "Invalid URL format",
  "message": "Invalid URL format",
  "usage": "Provide a valid URL starting with http:// or https://"
}
```

**500 Internal Server Error - Scraping Failed:**
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

## How to Use

### 1. Create New Scrape
```javascript
fetch('https://your-lambda-function-url.lambda-url.us-east-1.on.aws/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com',
    user_id: 'user123'
  })
})
.then(response => response.json())
.then(data => console.log(data[0]));
```

### 2. Get User Projects
```javascript
fetch('https://your-lambda-function-url.lambda-url.us-east-1.on.aws/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123'
  })
})
.then(response => response.json())
.then(data => console.log(data.projects));
```



## Data Persistence

All scrape data is automatically saved to DynamoDB with the following structure:

- **Partition Key:** `user_id` (string)
- **Sort Key:** `project_id` (string)
- **Data:** Complete scrape results stored as JSON

The `project_id` is automatically generated and returned in the response for future reference.

## Rate Limiting & Anti-Bot Protection

The scraper includes several features to avoid detection:

- **Realistic Headers:** Rotating User-Agent strings and browser-like headers
- **Random Delays:** 1-3 second delays between requests
- **Retry Logic:** Automatic retries with exponential backoff
- **Session Management:** Maintains cookies and connection state
- **Rate Limiting Handling:** Respects 429 status codes with delays

## Quick Reference

**To scrape a website:** Send `url` + `user_id`
**To get user projects:** Send only `user_id`

**user_id is always required.**

## That's it!

Copy the examples above and replace `your-lambda-function-url` with your actual URL.
