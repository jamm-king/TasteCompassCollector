import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from TasteCompassCollector.spiders.naver_blog_spider import NaverBlogSpider

if __name__ == "__main__":
    settings = get_project_settings()
    settings.set("FEEDS", {
        "live_results.json": {
            "format": "json",
            "encoding": "utf-8",
            "overwrite": True,
        }
    })
    settings.set("LOG_LEVEL", "INFO")

    process = CrawlerProcess(settings)
    process.crawl(NaverBlogSpider, keywords=["포항시 맛집"])
    process.start()

    with open("live_results.json", encoding="utf-8") as f:
        data = json.load(f)
    print(f"{len(data)} items collected")
    for item in data[:3]:
        print(item)
