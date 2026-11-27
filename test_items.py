from app.ddragon import get_latest_version, get_completed_items

version = get_latest_version()
items = get_completed_items(version)

print(len(items))
for item in list(items.values())[:8]:
    print(item["name"], item["gold"]["total"], item["tags"], item["stats"])