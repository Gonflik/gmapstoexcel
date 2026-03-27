from typing import Dict, Any, Optional


def _get_display_name(place: Dict[str, Any]) -> Optional[str]:
    display_name = place.get("displayName")
    if isinstance(display_name, dict):
        return display_name.get("text")
    return None


def map_place(place: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": _get_display_name(place),
        "address": place.get("formattedAddress"),
        "rating": place.get("rating"),
        "website": place.get("websiteUri"),
        "phone": place.get("internationalPhoneNumber"),
        "email": None,
        "instagram": None,
        "facebook": None,
        "linkedin": None,
        "tiktok": None,
    }


def map_places(places: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [map_place(place) for place in places]