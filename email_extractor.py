import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


EMAIL_REGEX = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
)

COMMON_CONTACT_PATHS = [
    "/contact",
    "/contacts",
    "/contact-us",
    "/about",
    "/about-us",
    "/uk/contact",
    "/ua/contact",
    "/контакти",
    "/контакты",
]


class EmailExtractor:
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
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None

            time.sleep(self.delay)
            return response.text
        except requests.RequestException:
            return None

    def _extract_emails_from_html(self, html: str) -> set[str]:
        emails = set()

        # plain text emails
        emails.update(EMAIL_REGEX.findall(html))

        soup = BeautifulSoup(html, "html.parser")

        # mailto links
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().startswith("mailto:"):
                email = href[7:].split("?")[0].strip()
                if email:
                    emails.add(email)

        return self._clean_emails(emails)

    def _clean_emails(self, emails: set[str]) -> set[str]:
        cleaned = set()

        for email in emails:
            email = email.strip().lower()
            email = email.rstrip(".,;:")
            if not email:
                continue

            # skip obvious junk
            if any(
                bad in email
                for bad in (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".svg",
                    "@example.com",
                )
            ):
                continue

            cleaned.add(email)

        return cleaned

    def _find_contact_links(self, base_url: str, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        found = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(" ", strip=True).lower()

            full_url = urljoin(base_url, href)

            if self._same_domain(base_url, full_url):
                if any(word in href.lower() for word in ("contact", "about", "контакт")):
                    found.add(full_url)
                elif any(word in text for word in ("contact", "contacts", "about", "контакти", "контакты")):
                    found.add(full_url)

        return list(found)

    def _same_domain(self, base_url: str, other_url: str) -> bool:
        base_netloc = urlparse(base_url).netloc.replace("www.", "")
        other_netloc = urlparse(other_url).netloc.replace("www.", "")
        return base_netloc == other_netloc

    def _candidate_urls(self, website_url: str, homepage_html: str | None) -> list[str]:
        candidates = [website_url.rstrip("/")]

        for path in COMMON_CONTACT_PATHS:
            candidates.append(urljoin(website_url.rstrip("/") + "/", path.lstrip("/")))

        if homepage_html:
            candidates.extend(self._find_contact_links(website_url, homepage_html))

        # dedupe while preserving order
        seen = set()
        unique = []
        for url in candidates:
            if url not in seen:
                seen.add(url)
                unique.append(url)

        return unique

    def extract_emails(self, website_url: str, max_pages: int = 5) -> list[str]:
        homepage_html = self._fetch_html(website_url)
        if not homepage_html:
            return []

        emails = set()
        emails.update(self._extract_emails_from_html(homepage_html))

        candidate_urls = self._candidate_urls(website_url, homepage_html)

        for url in candidate_urls[1:max_pages]:
            html = self._fetch_html(url)
            if not html:
                continue
            emails.update(self._extract_emails_from_html(html))

        return sorted(emails)