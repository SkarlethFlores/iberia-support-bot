# scraper.py  - updated to load from local JSON
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ScrapedPage:
    url: str
    topic: str
    subtopic: str
    section_heading: str
    text: str
    fare_classes: list = field(default_factory=list)
    language: str = "en"
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

def scrape_all() -> list:
    with open("data/iberia_knowledge.json", "r") as f:
        raw = json.load(f)

    pages = []
    for item in raw:
        pages.append(ScrapedPage(
            url=item["url"],
            topic=item["topic"],
            subtopic=item["subtopic"],
            section_heading=item["section_heading"],
            text=item["text"],
            fare_classes=item.get("fare_classes", []),
        ))

    print(f"✅ Loaded {len(pages)} sections from knowledge base")
    return pages

if __name__ == "__main__":
    pages = scrape_all()
    p = pages[0]
    print(f"\n--- Preview ---")
    print(f"Topic: {p.topic} / {p.subtopic}")
    print(f"Heading: {p.section_heading}")
    print(f"Fare classes: {p.fare_classes}")
    print(f"Text preview: {p.text[:200]}...")