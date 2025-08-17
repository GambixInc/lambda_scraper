import scrapy
from lambda_scraper.items import ScrapedItem


class BasicSpider(scrapy.Spider):
    name = 'basic'
    
    def __init__(self, url=None, *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = ['https://example.com']
    
    def parse(self, response):
        item = ScrapedItem()
        
        # Extract basic information
        item['url'] = response.url
        item['title'] = response.css('title::text').get()
        
        # Extract all text content (simplified)
        item['content'] = ' '.join(response.css('*::text').getall()).strip()
        
        # Extract all links
        item['links'] = response.css('a::attr(href)').getall()
        
        yield item
        
        # Optional: Follow links for deeper scraping (commented out for basic version)
        # for link in response.css('a::attr(href)').getall():
        #     if link:
        #         yield response.follow(link, self.parse)
