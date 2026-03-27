from typing import Any
from client import PlacesClient
from mapper import map_places
from email_extractor import EmailExtractor
from website_social_extractor import WebsiteSocialExtractor


class PlacesPipeline:
    def __init__(
        self,
        places_client: PlacesClient,
        email_extractor: EmailExtractor | None = None,
        website_social_extractor: WebsiteSocialExtractor | None = None,
    ):
        self.places_client = places_client
        self.email_extractor = email_extractor or EmailExtractor()
        self.website_social_extractor = website_social_extractor or WebsiteSocialExtractor()

    def run(
            self,
            query: str,
            *,
            max_pages: int = 3,
            max_results: int | None = None,
            language: str | None = None,
            region: str | None = None,
            enrich_emails: bool = True,
            enrich_socials: bool = True,
        ) -> list[dict[str, Any]]:
        print(f"[1/4] Searching places for: {query!r}")

        raw_places = self.places_client.search_text(
            query,
            max_pages=max_pages,
            max_results=max_results,
            language=language,
            region=region,
        )
        print(f"[2/4] Found {len(raw_places)} raw places")

        mapped_places = map_places(raw_places)
        print(f"[3/4] Mapped {len(mapped_places)} places")

        print("[4/4] Enriching places...")
        self._enrich(
            mapped_places,
            enrich_emails=enrich_emails,
            enrich_socials=enrich_socials,
        )

        print("[Done] Pipeline finished")
        return mapped_places
    def _enrich(
        self,
        places: list[dict[str, Any]],
        *,
        enrich_emails: bool,
        enrich_socials: bool,
    ) -> None:
        total = len(places)

        for index, item in enumerate(places, start=1):
            name = item.get("name") or "<unknown>"
            website = item.get("website")

            print(f"  -> [{index}/{total}] Processing: {name}")

            if not website:
                print("     No website")
                item["email"] = None
                item["instagram"] = None
                item["facebook"] = None
                item["linkedin"] = None
                item["tiktok"] = None
                continue

            print(f"     Website: {website}")

            if enrich_emails:
                emails = self.email_extractor.extract_emails(website)
                item["email"] = ", ".join(emails) if emails else None
                if item["email"]:
                    print(f"     Email(s): {item['email']}")
                else:
                    print("     No emails found")

            if enrich_socials:
                socials = self.website_social_extractor.extract_socials(website)
                item["instagram"] = socials["instagram"]
                item["facebook"] = socials["facebook"]
                item["linkedin"] = socials["linkedin"]
                item["tiktok"] = socials["tiktok"]

                print(
                    "     Socials:"
                    f" insta={bool(item['instagram'])},"
                    f" fb={bool(item['facebook'])},"
                    f" linkedin={bool(item['linkedin'])},"
                    f" tiktok={bool(item['tiktok'])}"
                )