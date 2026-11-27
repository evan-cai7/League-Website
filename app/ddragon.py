from functools import lru_cache
import httpx

@lru_cache(maxsize=1)
def get_latest_version() -> str:
    response = httpx.get("https://ddragon.leagueoflegends.com/api/versions.json")
    response.raise_for_status()
    versions = response.json()
    return versions[0]

@lru_cache(maxsize=2)
def get_items(version: str) -> dict:
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    response = httpx.get(url)
    response.raise_for_status()
    raw = response.json()["data"]
    return {
        item_id: {"id": item_id, **item}
        for item_id, item in raw.items()
        if item["gold"]["purchasable"] and item["maps"].get("11")
    }

@lru_cache(maxsize=2)
def get_champions(version: str) -> dict:
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()["data"]

def get_completed_items(version: str) -> dict:
    items = get_items(version)
    return {
        item_id: item
        for item_id, item in items.items()
        if not item.get("into")
        and item["gold"]["total"] >= 1600
        and "Consumable" not in item.get("tags", [])
        and "Trinket" not in item.get("tags", [])
    }