# TasteCompassCollector/spiders/naver_blog_spider.py

from TasteCompassCollector.items.review_item import ReviewItem
import html
import json
import re
import scrapy
from urllib.parse import quote


class NaverBlogSpider(scrapy.Spider):
    name = "naver_blog"

    BLOG_POST_URL = re.compile(r"https://blog\.naver\.com/[A-Za-z0-9_-]+/\d+")

    def __init__(self, keywords=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not keywords:
            raise ValueError("keywords must be provided to NaverBlogSpider")
        self.keywords = keywords

    def start_requests(self):
        for keyword in self.keywords:
            encoded = quote(keyword)
            url = f"https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword={encoded}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True}
            )

    def parse(self, response):
        raw_links = response.css("a.desc_inner::attr(href)").getall()

        for link in raw_links:
            full_url = response.urljoin(link)

            if self.BLOG_POST_URL.match(full_url):
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_detail,
                    meta={"playwright": True}
                )

    def parse_detail(self, response):
        iframe_src = response.css("iframe#mainFrame::attr(src)").get()
        if iframe_src:
            iframe_url = "https://blog.naver.com" + iframe_src
            yield scrapy.Request(
                url=iframe_url,
                callback=self.parse_post_view,
                meta={
                    "playwright": True,
                    # "playwright_page_methods": [
                    #     {"method": "wait_for_selector", "args": ["div.se-text"]},
                    # ],
                    "original_url": response.url,
                }
            )

    def parse_post_view(self, response):
        yield from self._extract_item(response)

    def _extract_item(self, response):
        item = ReviewItem()

        # source, url
        item["source"] = "naver_blog"
        item["url"] = response.meta.get("original_url")

        # text
        paragraphs = response.css(
            "div.se-text > div.se-component-content > div.se-section-text "
            "> div.se-module-text > p.se-text-paragraph > span::text"
        ).getall()
        item["text"] = "\n".join([p.strip() for p in paragraphs if p.strip()])

        # x, y (longitude, latitude)
        raw = response.css(
            "div.se-placesMap > script.__se_module_data::attr(data-module)"
        ).get()

        if raw:
            unescaped = html.unescape(raw)
            module_data = json.loads(unescaped)
            places = module_data.get("data", {}).get("places", [])
            if places:
                place = places[0]
                lat = place.get("latlng", {}).get("latitude")
                lng = place.get("latlng", {}).get("longitude")

                item["x"] = lng
                item["y"] = lat

        self.logger.info(item)

        yield item
