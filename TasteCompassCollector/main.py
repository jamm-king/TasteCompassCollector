# TasteCompassCollector/main.py

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from TasteCompassCollector.utils.io import load_keywords_from_file
from TasteCompassCollector.spiders.naver_blog_spider import NaverBlogSpider


def run_naver_blog_spider():
    keywords = load_keywords_from_file("TasteCompassCollector/search_keywords.txt")
    process = CrawlerProcess(get_project_settings())

    process.crawl(NaverBlogSpider, keywords=["포항시 맛집"])
    process.start()


if __name__ == "__main__":
    run_naver_blog_spider()
