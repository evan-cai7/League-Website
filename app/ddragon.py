import httpx


def get_latest_version() -> str:
    response = httpx.get("https://ddragon.leagueoflegends.com/api/versions.json")
    response.raise_for_status()
    versions = response.json()
    return versions[0]

