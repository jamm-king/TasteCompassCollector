# TasteCompassCollector/utils/io.py

from pathlib import Path


def load_keywords_from_file(filepath: str) -> list[str]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Keyword file not found: {filepath}")

    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
