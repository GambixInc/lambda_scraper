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

### Scrape Website

**Endpoint:** `POST /` or `GET /`

Scrapes a website and returns comprehensive data including content analysis, framework detection, and HTTP response details.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ | The website URL to scrape (must start with http:// or https://) |
| `user_id` | string | ✅ | Unique identifier for the user (used for DynamoDB filtering) |
| `retries` | number | ❌ | Number of retry attempts (1-5, default: 3) |

#### Request Examples

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

#### Response Format

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
```

#### Response Fields Explained

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

## Frontend Integration Examples

### JavaScript/TypeScript

**Using Fetch API:**
```javascript
async function scrapeWebsite(url, userId, retries = 3) {
  try {
    const response = await fetch('https://your-lambda-function-url.lambda-url.us-east-1.on.aws/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        user_id: userId,
        retries: retries
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Scraping failed');
    }

    const data = await response.json();
    return data[0]; // API returns array with single object
  } catch (error) {
    console.error('Scraping error:', error);
    throw error;
  }
}

// Usage
scrapeWebsite('https://example.com', 'user123')
  .then(result => {
    console.log('Scrape successful:', result);
    console.log('Project ID:', result.project_id);
    console.log('Word count:', result.word_count);
    console.log('Framework detected:', result.framework_detection);
  })
  .catch(error => {
    console.error('Scrape failed:', error);
  });
```

**Using Axios:**
```javascript
import axios from 'axios';

async function scrapeWebsite(url, userId, retries = 3) {
  try {
    const response = await axios.post('https://your-lambda-function-url.lambda-url.us-east-1.on.aws/', {
      url: url,
      user_id: userId,
      retries: retries
    });

    return response.data[0];
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || 'Scraping failed');
    }
    throw error;
  }
}
```

### React Hook Example

```javascript
import { useState, useCallback } from 'react';

function useWebsiteScraper() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const scrapeWebsite = useCallback(async (url, userId, retries = 3) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('https://your-lambda-function-url.lambda-url.us-east-1.on.aws/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          user_id: userId,
          retries: retries
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Scraping failed');
      }

      const data = await response.json();
      setResult(data[0]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { scrapeWebsite, loading, error, result };
}

// Usage in component
function ScraperComponent() {
  const { scrapeWebsite, loading, error, result } = useWebsiteScraper();
  const [url, setUrl] = useState('');
  const [userId, setUserId] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    scrapeWebsite(url, userId);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL"
          required
        />
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter user ID"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Website'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}
      
      {result && (
        <div className="result">
          <h3>Scrape Results</h3>
          <p><strong>Title:</strong> {result.title}</p>
          <p><strong>Project ID:</strong> {result.project_id}</p>
          <p><strong>Word Count:</strong> {result.word_count}</p>
          <p><strong>Saved to DB:</strong> {result.saved_to_dynamodb ? 'Yes' : 'No'}</p>
          <p><strong>Response Time:</strong> {result.curl_info.response_time_ms}ms</p>
        </div>
      )}
    </div>
  );
}
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

## Best Practices

1. **User ID Management:** Use consistent, unique user IDs for proper data organization
2. **Error Handling:** Always handle potential errors and check `saved_to_dynamodb` status
3. **Rate Limiting:** Don't make too many requests in quick succession
4. **URL Validation:** Ensure URLs are properly formatted before sending
5. **Project ID Storage:** Store the returned `project_id` for future reference

## Troubleshooting

**Common Issues:**

1. **"Missing user_id parameter"** - Ensure you're passing the `user_id` in your request
2. **"Invalid URL format"** - Make sure URLs start with `http://` or `https://`
3. **"Failed to scrape the URL"** - The website may have anti-bot protection or be temporarily unavailable
4. **`saved_to_dynamodb: false`** - Check the `dynamodb_error` field for details

**Debugging Tips:**

- Check the `curl_info.status_code` to see if the request was successful
- Look at `curl_info.response_time_ms` to identify slow responses
- Examine `framework_detection` to understand the website's technology stack
- Use the `retries` parameter to increase retry attempts for problematic sites

## Support

For issues or questions, check the error responses for detailed information about what went wrong. The API includes comprehensive error messages and usage examples.
