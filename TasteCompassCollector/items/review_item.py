import scrapy


class ReviewItem(scrapy.Item):
    source = scrapy.Field()
    url = scrapy.Field()
    text = scrapy.Field()
    x = scrapy.Field()
    y = scrapy.Field()
