from app.ddragon import get_latest_version, get_champions, get_completed_items
from app.threat import build_threat_profile
from app.engine import recommend_build

version = get_latest_version()
champs = get_champions(version)
items = get_completed_items(version)

enemies = [
    {"champion": "Zed",      "kills": 8, "deaths": 1, "assists": 2},
    {"champion": "Syndra",   "kills": 3, "deaths": 2, "assists": 4},
    {"champion": "Leona",    "kills": 0, "deaths": 5, "assists": 9},
    {"champion": "Soraka",   "kills": 0, "deaths": 3, "assists": 11},
    {"champion": "Malphite", "kills": 2, "deaths": 4, "assists": 5},
]

profile = build_threat_profile(enemies, champs)

champ_id = "Sett"

info = champs[champ_id]["info"]
my_ad_share = info["attack"] / (info["attack"] + info["magic"])
my_tags = champs[champ_id]["tags"]

build = recommend_build(items, profile, my_ad_share, my_tags=my_tags)

for r in build:
    print(r["item"]["name"], r["score"], "-", r["reason"])

expected = {"Stridebreaker", "Black Cleaver", "Overlord's Bloodmail", "Sterak's Gage", "Spear of Shojin"}
print("matches:", {r["item"]["name"] for r in build} & expected)