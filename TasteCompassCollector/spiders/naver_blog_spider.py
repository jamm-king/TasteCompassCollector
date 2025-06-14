# TasteCompassCollector/spiders/naver_blog_spider.py
import math
import json
import re
import html
from urllib.parse import quote

import scrapy

from TasteCompassCollector.items.review_item import ReviewItem


class NaverBlogSpider(scrapy.Spider):
    name = "naver_blog"
    # custom_settings = {
    #     'JOBDIR': f'crawls/{name}-job',
    # }

    BLOG_POST_URL = re.compile(r"https://blog\.naver\.com/[A-Za-z0-9_-]+/\d+")

    def __init__(self, keywords=None, max_pages=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not keywords:
            raise ValueError("keywords must be provided to NaverBlogSpider")
        self.keywords = keywords
        self.max_pages = int(max_pages)
        self.page_count = 0
        self.post_count = 0

    def start_requests(self):
        for keyword in self.keywords:
            encoded = quote(keyword)
            url = (
                f"https://section.blog.naver.com/Search/Post.naver"
                f"?pageNo=1&rangeType=ALL&orderBy=sim&keyword={encoded}"
            )
            yield scrapy.Request(
                url=url,
                callback=self.parse_search,
                meta={
                    "playwright": True,
                    "is_first": True,
                    "keyword": keyword,
                    "page": 1,
                }
            )

    def parse_search(self, response):
        keyword = response.meta["keyword"]
        page_no = response.meta.get("page", 1)

        raw_links = response.css("a.desc_inner::attr(href)").getall()
        valid_links = [response.urljoin(link) for link in raw_links
                       if self.BLOG_POST_URL.match(response.urljoin(link))]

        self.logger.debug(
            f"[{keyword}] Page {page_no}: Found {len(valid_links)} post URLs"
        )

        for link in valid_links:
            yield scrapy.Request(
                url=link,
                callback=self.parse_post,
                meta={"playwright": True},
                dont_filter=True
            )

        self.page_count += 1
        self.logger.info(
            f"[{keyword}] Completed page {page_no}. Total pages fetched: {self.page_count}"
        )

        if response.meta.get("is_first"):
            total_text = response.css('em.search_number::text').get() or "0"
            total_count = int(''.join(filter(str.isdigit, total_text)))
            total_pages = math.ceil(total_count / 7)
            last_page = min(self.max_pages, total_pages)

            encoded = quote(keyword)
            for p in range(2, last_page + 1):
                next_url = (
                    f"https://section.blog.naver.com/Search/Post.naver"
                    f"?pageNo={p}&rangeType=ALL&orderBy=sim&keyword={encoded}"
                )
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_search,
                    meta={
                        "playwright": True,
                        "is_first": False,
                        "keyword": keyword,
                        "page": p,
                    }
                )

    def parse_post(self, response):
        iframe_src = response.css("iframe#mainFrame::attr(src)").get()
        if iframe_src:
            iframe_url = f"https://blog.naver.com{iframe_src}"
            yield scrapy.Request(
                url=iframe_url,
                callback=self.parse_post_view,
                meta={
                    "playwright": True,
                    "original_url": response.url,
                }
            )

    def parse_post_view(self, response):
        for item in self._extract_item(response):
            self.post_count += 1
            self.logger.debug(f"Extracted post #{self.post_count}: {item['url']}")
            yield item

    def _extract_item(self, response):
        item = ReviewItem()

        item["source"] = "naver_blog"
        item["url"] = response.meta.get("original_url")

        paragraphs = response.css(
            "div.se-text > div.se-component-content > div.se-section-text "
            "> div.se-module-text > p.se-text-paragraph > span::text"
        ).getall()
        item["text"] = "\n".join(p.strip() for p in paragraphs if p.strip())

        address = response.css("p.se-map-address::text").get()
        item["address"] = address

        self.logger.debug(f"Parsed item: {item}")
        yield item

    def _extract_position(self, response):
        raw = response.css(
            "div.se-placesMap > script.__se_module_data::attr(data-module)"
        ).get()
        if raw:
            try:
                unescaped = html.unescape(raw)
                module_data = json.loads(unescaped)
                places = module_data.get("data", {}).get("places", [])
                if places:
                    place = places[0]
                    lat = place.get("latlng", {}).get("latitude")
                    lng = place.get("latlng", {}).get("longitude")

                    return lng, lat
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Failed to parse location data on post: {response.url}"
                )

    def closed(self, reason):
        self.logger.info(
            f"Spider closed: fetched {self.page_count} pages and {self.post_count} posts "
            f"for keywords {self.keywords}. Reason: {reason}"
        )