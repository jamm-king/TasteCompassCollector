import logging
import time
from scrapy import signals


class CustomHeadersMiddleware:
    """
    Adds custom headers and cookies to each request.

    Settings:
    - CUSTOM_REQUEST_HEADERS: dict of header names to values
    - CUSTOM_REQUEST_COOKIES: dict of cookie names to values
    """
    @classmethod
    def from_crawler(cls, crawler):
        headers = crawler.settings.getdict('CUSTOM_REQUEST_HEADERS', {})
        cookies = crawler.settings.getdict('CUSTOM_REQUEST_COOKIES', {})
        return cls(headers=headers, cookies=cookies)

    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}

    def process_request(self, request, spider):
        # Set headers if not already present
        for name, value in self.headers.items():
            request.headers.setdefault(name, value)
        # Update cookies
        if self.cookies:
            request.cookies.update(self.cookies)


class ProxyMiddleware:
    """
    Rotates through a list of proxies for each request.

    Settings:
    - PROXY_LIST: list of proxy URLs (http://host:port)
    """
    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.getlist('PROXY_LIST', [])
        return cls(proxy_list=proxy_list)

    def __init__(self, proxy_list=None):
        self.proxy_list = proxy_list or []
        self._index = 0

    def process_request(self, request, spider):
        if not self.proxy_list:
            return
        # Round-robin proxy selection
        proxy = self.proxy_list[self._index % len(self.proxy_list)]
        request.meta['proxy'] = proxy
        self._index += 1


class LoggingMiddleware:
    """
    Logs request and response details including timings.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # Connect to spider_opened/closed signals if needed
        mw = cls()
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(mw.spider_closed, signal=signals.spider_closed)
        return mw

    def spider_opened(self, spider):
        self.logger.info(f"Spider opened: {spider.name}")

    def spider_closed(self, spider):
        self.logger.info(f"Spider closed: {spider.name}")

    def process_request(self, request, spider):
        request.meta['start_time'] = time.time()
        self.logger.debug(f"Starting request: {request.method} {request.url}")

    def process_response(self, request, response, spider):
        elapsed = time.time() - request.meta.get('start_time', time.time())
        self.logger.debug(
            f"Received response {response.status} for {request.url} in {elapsed:.2f}s"
        )
        return response

    def process_exception(self, request, exception, spider):
        self.logger.error(f"Error on {request.url}: {exception}")
        # Let other middlewares handle or ignore
        return None
