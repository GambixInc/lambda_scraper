import json
import logging
import random
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cors_headers():
    """Get consistent CORS headers for all responses"""
    return {
        'Content-Type': 'application/json'
    }

def create_response(status_code, body, headers=None):
    """Create a consistent response with proper headers"""
    response_headers = get_cors_headers()
    if headers:
        response_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps(body) if isinstance(body, (dict, list)) else body
    }

def get_realistic_headers():
    """Generate realistic browser headers to avoid bot detection"""
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"'
    }

def scrape_url(url, max_retries=3):
    """Scrape a URL using requests and BeautifulSoup with anti-bot protection"""
    
    # Create a session for better connection handling
    session = requests.Session()
    
    # Set realistic headers
    session.headers.update(get_realistic_headers())
    
    # Add random delay to appear more human-like
    delay = random.uniform(1, 3)
    logger.info(f"Adding delay of {delay:.2f} seconds before request")
    time.sleep(delay)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} to scrape {url}")
            
            # Make request with longer timeout and session
            response = session.get(
                url, 
                timeout=15,  # Increased timeout
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            
            # Check if we got HTML content
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                logger.warning(f"Non-HTML content type: {content_type}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else 'No title found'
            
            # Extract text content (more sophisticated)
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text_content = soup.get_text()
            # Clean up whitespace more thoroughly
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract links (more comprehensive)
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Handle relative URLs
                if href.startswith('/'):
                    parsed_url = urlparse(url)
                    href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                elif href.startswith(('http://', 'https://')):
                    links.append(href)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '') if meta_keywords else ''
            
            logger.info(f"Successfully scraped {url} on attempt {attempt + 1}")
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'keywords': keywords,
                'content': text_content[:2000] + '...' if len(text_content) > 2000 else text_content,
                'links': unique_links[:15],  # Increased link limit
                'content_length': len(text_content),
                'links_count': len(unique_links),
                'status_code': response.status_code,
                'content_type': content_type
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))  # Longer delay for timeouts
                continue
            else:
                logger.error(f"All attempts timed out for {url}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1} for {url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 7))  # Even longer delay for connection errors
                continue
            else:
                logger.error(f"All connection attempts failed for {url}")
                return None
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error on attempt {attempt + 1} for {url}: {str(e)}")
            if e.response.status_code == 429:  # Rate limited
                logger.warning("Rate limited - adding longer delay")
                time.sleep(random.uniform(10, 20))
                continue
            elif e.response.status_code in [403, 401]:  # Forbidden/Unauthorized
                logger.error(f"Access forbidden/unauthorized for {url}")
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1} for {url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))
                continue
            else:
                return None
    
    return None

def lambda_handler(event, context):
    """AWS Lambda handler function with enhanced error handling and CORS support"""
    
    # Handle OPTIONS requests (CORS preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
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
        return create_response(400, {
            'error': 'Missing URL parameter',
            'usage': 'Provide url as query parameter (?url=https://example.com) or in request body',
            'example': {
                'GET': '?url=https://example.com',
                'POST': '{"url": "https://example.com"}'
            }
        })
    
    # Validate URL format
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Ensure we have a valid scheme
        if parsed_url.scheme not in ['http', 'https']:
            return create_response(400, {
                'error': 'Invalid URL scheme',
                'message': 'Only HTTP and HTTPS URLs are supported'
            })
            
    except Exception as e:
        return create_response(400, {
            'error': 'Invalid URL format',
            'message': str(e),
            'usage': 'Provide a valid URL starting with http:// or https://'
        })
    
    # Get additional parameters
    max_retries = 3
    if 'queryStringParameters' in event and event['queryStringParameters']:
        try:
            retries_param = event['queryStringParameters'].get('retries')
            if retries_param:
                max_retries = min(int(retries_param), 5)  # Cap at 5 retries
        except ValueError:
            pass
    
    # Scrape the URL
    logger.info(f"Starting scrape of {url} with max_retries={max_retries}")
    result = scrape_url(url, max_retries)
    
    if result is None:
        return create_response(500, {
            'error': 'Failed to scrape the URL',
            'url': url,
            'message': 'The scraper encountered an error or the website may be blocking automated access',
            'suggestions': [
                'Check if the URL is accessible in a browser',
                'The site may have anti-bot protection',
                'Try again later if the site is temporarily unavailable'
            ]
        })
    
    # Add metadata about the scraping process
    result['scraped_at'] = time.time()
    result['scraper_version'] = '2.0'
    result['scraper_features'] = [
        'anti-bot-protection',
        'realistic-headers',
        'retry-logic',
        'rate-limiting-handling'
    ]
    
    return create_response(200, [result])
