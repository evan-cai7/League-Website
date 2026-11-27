from app.ddragon import get_latest_version, get_champions
from app.tags import BURST_MAGES
from app.threat import build_threat_profile

champs = get_champions(get_latest_version())

missing = [name for name in BURST_MAGES if name not in champs]
print("Not found:", missing)


enemies = [
    {"champion": "Zed",      "kills": 8, "deaths": 1, "assists": 2},
    {"champion": "Syndra",   "kills": 3, "deaths": 2, "assists": 4},
    {"champion": "Leona",    "kills": 0, "deaths": 5, "assists": 9},
    {"champion": "Soraka",   "kills": 0, "deaths": 3, "assists": 11},
    {"champion": "Malphite", "kills": 2, "deaths": 4, "assists": 5},
]

print(build_threat_profile(enemies, champs))