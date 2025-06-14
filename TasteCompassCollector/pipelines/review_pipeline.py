import re

import requests


class ReviewPipeline:
    def process_item(self, item, spider):
        if "text" in item:
            item["text"] = re.sub(r'\u200b', '', item["text"]).strip()

        payload = {
            "source": item["source"],
            "url": item["url"],
            "address": item["address"],
            "text": item["text"],
        }
        try:
            response = requests.post("http://localhost:8080/api/reviews", json=payload)
            response.raise_for_status()
        except Exception as e:
            spider.logger.error(f"Failed to POST review: {e}")
        return item
