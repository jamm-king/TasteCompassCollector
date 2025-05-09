# TasteCompassCollector/utils/io.py

from pathlib import Path


def load_keywords_from_file(filepath: str) -> list[str]:
    """
    주어진 텍스트 파일에서 키워드를 한 줄씩 읽어 리스트로 반환
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Keyword file not found: {filepath}")

    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
