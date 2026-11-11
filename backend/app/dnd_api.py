"""Client for the free D&D 5e API (https://www.dnd5eapi.co).

Every call has a timeout. Any failure (network error, timeout, bad status,
unexpected JSON) is raised as DndApiError so routes can handle it in one way.
The class and equipment lists rarely change, so they are cached in memory
after the first successful call.
"""
import random

import httpx

from .config import DND_API_BASE, DND_API_TIMEOUT


class DndApiError(Exception):
    """The D&D 5e API could not be reached or returned something unexpected."""


_cache: dict[str, list[dict]] = {}


def _get(path: str) -> dict:
    url = f"{DND_API_BASE}{path}"
    try:
        response = httpx.get(url, timeout=DND_API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as exc:
        raise DndApiError("The D&D 5e API took too long to respond.") from exc
    except httpx.HTTPStatusError as exc:
        raise DndApiError(f"The D&D 5e API returned an error ({exc.response.status_code}).") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise DndApiError("Could not reach the D&D 5e API.") from exc


def _get_list(path: str) -> list[dict]:
    if path not in _cache:
        data = _get(path)
        results = data.get("results")
        if not isinstance(results, list) or not results:
            raise DndApiError("The D&D 5e API returned an empty list.")
        _cache[path] = results
    return _cache[path]


def list_classes() -> list[dict]:
    """[{index, name}, ...] for character classes, e.g. {"index": "wizard", "name": "Wizard"}."""
    return [{"index": c["index"], "name": c["name"]} for c in _get_list("/classes")]


def random_equipment() -> dict:
    """Pick a random equipment item and return its full API response."""
    items = _get_list("/equipment")
    choice = random.choice(items)
    item = _get(f"/equipment/{choice['index']}")
    if "index" not in item or "name" not in item:
        raise DndApiError("The D&D 5e API returned an item without a name.")
    return item


def clear_cache() -> None:
    _cache.clear()
