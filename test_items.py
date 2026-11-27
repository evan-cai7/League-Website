from app.ddragon import get_latest_version, get_items
from app.tags import EXCLUDED_ITEMS

all_names = {i["name"] for i in get_items(get_latest_version()).values()}
print("Not found:", [n for n in EXCLUDED_ITEMS if n not in all_names])