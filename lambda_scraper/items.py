import scrapy


class ScrapedItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    links = scrapy.Field()
