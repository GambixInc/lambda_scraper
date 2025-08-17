# Lambda Scraper

A simple, dockerized web scraping tool built with Scrapy that can scrape any website with a basic URL input.

## Features

- Basic web scraping functionality
- Extracts page title, content, and links
- Dockerized for easy deployment
- Simple command-line interface
- Respects robots.txt rules
- Built-in request throttling

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t lambda_scraper .
```

### 2. Run the Scraper

```bash
docker run --rm lambda_scraper https://example.com
```

The JSON output will be returned directly to your terminal.

### 3. Save Output to File (Optional)

If you want to save the output to a file:

```bash
docker run --rm lambda_scraper https://example.com > output.json
```

## Usage Examples

### Basic scraping:
```bash
docker run --rm lambda_scraper https://httpbin.org/html
```

### Scrape a news website:
```bash
docker run --rm lambda_scraper https://news.ycombinator.com
```

### Scrape and save output:
```bash
docker run --rm lambda_scraper https://example.com > scraped_data.json
```

## Output Format

The scraper outputs data in JSON format with the following structure:

```json
[
  {
    "url": "https://example.com",
    "title": "Page Title",
    "content": "Extracted text content...",
    "links": ["https://link1.com", "https://link2.com"]
  }
]
```

## Project Structure

```
lambda_scraper/
├── Dockerfile
├── requirements.txt
├── scrapy.cfg
├── run_scraper.sh
├── lambda_scraper/
│   ├── __init__.py
│   ├── settings.py
│   ├── items.py
│   └── spiders/
│       ├── __init__.py
│       └── basic_spider.py
└── README.md
```

## Configuration

The scraper is configured with conservative settings:
- Respects robots.txt
- 1-second delay between requests
- Auto-throttling enabled
- Random delay variation

You can modify these settings in `lambda_scraper/settings.py` if needed.

## Limitations

- This is a basic scraper designed for simple use cases
- Does not handle JavaScript-rendered content
- Does not follow pagination or complex crawling patterns
- Designed for single-page scraping

## Development

To run the scraper locally without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the spider:
   ```bash
   scrapy crawl basic -a url="https://example.com" -o - -t json
   ```