from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClipItem:
    id: int | None
    content: str
    content_type: str  # text, html, image, files
    preview: str
    created_at: str
