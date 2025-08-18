import json
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def scrape_url(url):
    """Scrape a URL using requests and BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Lambda-Scraper/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No title found'
        
        # Extract text content
        text_content = soup.get_text()
        text_content = ' '.join(text_content.split())  # Clean up whitespace
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(('http://', 'https://')):
                links.append(href)
        
        return {
            'url': url,
            'title': title,
            'content': text_content[:1000] + '...' if len(text_content) > 1000 else text_content,
            'links': links[:10]
        }
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return None

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    
    # Parse URL from event
    url = None
    
    # Check for URL in query parameters (GET request)
    if 'queryStringParameters' in event and event['queryStringParameters']:
        url = event['queryStringParameters'].get('url')
    
    # Check for URL in request body (POST request)
    if not url and 'body' in event and event['body']:
        try:
            body = json.loads(event['body'])
            url = body.get('url')
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Validate URL
    if not url:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Missing URL parameter',
                'usage': 'Provide url as query parameter (?url=https://example.com) or in request body'
            })
        }
    
    # Validate URL format
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
    except Exception:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Invalid URL format',
                'usage': 'Provide a valid URL starting with http:// or https://'
            })
        }
    
    # Scrape the URL
    result = scrape_url(url)
    
    if result is None:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Failed to scrape the URL',
                'url': url
            })
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps([result], indent=2)
    }
