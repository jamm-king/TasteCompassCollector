# TasteCompassCollector/main.py

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from utils.io import load_keywords_from_file
from spiders.naver_blog_spider import NaverBlogSpider


def run_naver_blog_spider():
    keywords = load_keywords_from_file("search_keywords.txt")
    process = CrawlerProcess(get_project_settings())

    process.crawl(NaverBlogSpider, keywords=keywords)
    process.start()


if __name__ == "__main__":
    run_naver_blog_spider()
