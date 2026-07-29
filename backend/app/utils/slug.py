import re
import unicodedata
from typing import Optional


def generate_slug(text: str, max_length: int = 100) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip("-")
    return text or "untitled"


def generate_unique_slug(text: str, existing_slugs: set[str], max_length: int = 100) -> str:
    slug = generate_slug(text, max_length)
    if slug not in existing_slugs:
        return slug

    counter = 1
    while True:
        new_slug = f"{slug}-{counter}"
        if new_slug not in existing_slugs:
            return new_slug
        counter += 1
