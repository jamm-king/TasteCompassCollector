def is_restaurant_review(text: str) -> bool:
    keywords = ["맛집", "식당", "후기", "점심", "저녁", "코스요리", "브런치"]
    return any(keyword in text for keyword in keywords)
