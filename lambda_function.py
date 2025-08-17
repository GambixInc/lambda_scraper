import json
import subprocess
import tempfile
import os
import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def lambda_handler(event, context):
    """
    AWS Lambda handler for web scraping
    Expects event with 'url' parameter
    """
    try:
        # Extract URL from event (supports both query params and body)
        url = None
        
        # Try query string parameters first
        if 'queryStringParameters' in event and event['queryStringParameters']:
            url = event['queryStringParameters'].get('url')
        
        # Try body if no query params
        if not url and 'body' in event:
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                url = body.get('url')
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Try direct event (for testing)
        if not url:
            url = event.get('url')
        
        if not url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Missing URL parameter',
                    'usage': 'Provide url as query parameter (?url=https://example.com) or in request body'
                })
            }
        
        # Run the scraper using Scrapy directly
        scraped_data = run_scrapy_spider(url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(scraped_data)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }


def run_scrapy_spider(url):
    """Run Scrapy spider and return scraped data"""
    # Capture stdout/stderr to avoid logging issues
    output = StringIO()
    error_output = StringIO()
    
    try:
        with redirect_stdout(output), redirect_stderr(error_output):
            # Create a simple spider class inline
            class SimpleSpider(scrapy.Spider):
                name = 'simple'
                start_urls = [url]
                
                def parse(self, response):
                    item = {
                        'url': response.url,
                        'title': response.css('title::text').get(),
                        'content': ' '.join(response.css('*::text').getall()).strip(),
                        'links': response.css('a::attr(href)').getall()
                    }
                    return item
            
            # Create settings
            settings = get_project_settings()
            settings.set('ROBOTSTXT_OBEY', True)
            settings.set('DOWNLOAD_DELAY', 1)
            settings.set('AUTOTHROTTLE_ENABLED', True)
            settings.set('AUTOTHROTTLE_START_DELAY', 1)
            settings.set('AUTOTHROTTLE_MAX_DELAY', 60)
            settings.set('AUTOTHROTTLE_TARGET_CONCURRENCY', 1.0)
            settings.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
            settings.set('TWISTED_REACTOR', 'twisted.internet.asyncioreactor.AsyncioSelectorReactor')
            
            # Create crawler process
            process = CrawlerProcess(settings)
            process.crawl(SimpleSpider)
            
            # Collect results
            results = []
            def collect_item(item, response, spider):
                results.append(item)
            
            # Add item pipeline to collect results
            process.settings.set('ITEM_PIPELINES', {'__main__': collect_item})
            
            # Start the crawler
            process.start()
            
            return results if results else [{'url': url, 'title': None, 'content': 'No content found', 'links': []}]
            
    except Exception as e:
        # Fallback to simple requests if Scrapy fails
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return [{
                'url': url,
                'title': soup.title.string if soup.title else None,
                'content': soup.get_text().strip(),
                'links': [a.get('href') for a in soup.find_all('a', href=True)]
            }]
        except Exception as fallback_error:
            return [{
                'url': url,
                'title': None,
                'content': f'Error scraping: {str(e)}',
                'links': []
            }]
