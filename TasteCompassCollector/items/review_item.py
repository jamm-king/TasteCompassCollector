import scrapy


class ReviewItem(scrapy.Item):
    source = scrapy.Field()
    url = scrapy.Field()
    address = scrapy.Field()
    text = scrapy.Field()
