from backend.services.hackernews_service import fetch_discussions as fetch_hn
from backend.services.reddit_service import fetch_discussions as fetch_reddit
from backend.services.rss_service import fetch_discussions as fetch_rss


class CollectorAgent:
    def run(self) -> list[dict]:
        return [*fetch_reddit(), *fetch_hn(), *fetch_rss()]
