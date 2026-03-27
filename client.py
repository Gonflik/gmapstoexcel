import time
import requests
from typing import List, Dict, Optional


class PlacesClient:
    BASE_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(
        self,
        api_key: str,
        *,
        timeout: int = 10,
        max_retries: int = 3,
        rate_limit_delay: float = 1.2,
        page_delay: float = 2.0,
    ):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.page_delay = page_delay

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.rating,"
                "places.websiteUri,"
                "places.internationalPhoneNumber"
            ),
        }

    def _post(self, payload: Dict) -> Dict:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=self._headers(),
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response.json()

                if response.status_code in (429, 500, 502, 503):
                    time.sleep(self.rate_limit_delay * attempt)
                    continue

                # Non-retryable error
                raise RuntimeError(
                    f"Request failed: {response.status_code} {response.text}"
                )

            except requests.RequestException as e:
                last_error = e
                time.sleep(self.rate_limit_delay * attempt)

        raise RuntimeError(f"Max retries exceeded: {last_error}")

    def search_text(
            self,
            query: str,
            *,
            max_pages: int = 3,
            max_results: int | None = None,
            language: str | None = None,
            region: str | None = None,
        ) -> list[dict]:
            all_places: list[dict] = []
            next_page_token: str | None = None

            for page in range(max_pages):
                payload = {
                    "textQuery": query,
                    "pageSize": 20,
                }

                if language:
                    payload["languageCode"] = language
                if region:
                    payload["regionCode"] = region
                if next_page_token:
                    payload["pageToken"] = next_page_token

                data = self._post(payload)
                places = data.get("places", [])
                all_places.extend(places)

                print(f"[Search] Page {page + 1}: got {len(places)} places")
                print(f"[Search] nextPageToken: {data.get('nextPageToken')}")

                if max_results is not None and len(all_places) >= max_results:
                    return all_places[:max_results]

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

                time.sleep(self.page_delay)

            return all_places