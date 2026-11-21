from app.ddragon import get_latest_version, get_items

version = get_latest_version()
items = get_items(version)

print(version)
print(len(items))
for item in list(items.values())[:5]:
    print(item["name"], item["gold"]["total"])

    