import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SOCIAL_PATTERNS = {
    "instagram": ["instagram.com"],
    "facebook": ["facebook.com"],
    "linkedin": ["linkedin.com"],
    "tiktok": ["tiktok.com"],
}


class WebsiteSocialExtractor:
    def __init__(self, timeout: int = 10, delay: float = 1.0):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/146.0.0.0 Safari/537.36"
                )
            }
        )

    def _fetch_html(self, url: str) -> str | None:
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None

            time.sleep(self.delay)
            return response.text
        except requests.RequestException:
            return None

    def extract_socials(self, website_url: str) -> dict[str, str | None]:
        html = self._fetch_html(website_url)
        result = {
            "instagram": None,
            "facebook": None,
            "linkedin": None,
            "tiktok": None,
        }

        if not html:
            return result

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urljoin(website_url, href)

            for platform, domains in SOCIAL_PATTERNS.items():
                if any(domain in full_url.lower() for domain in domains):
                    if result[platform] is None:
                        result[platform] = full_url

        return result