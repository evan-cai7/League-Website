from app.ddragon import get_latest_version, get_items, get_champions

version = get_latest_version()
items = get_items(version)
champs = get_champions(version)

print(version, len(items), len(champs))
print(list(champs.keys())[:5])
print(champs["Sett"]["tags"], champs["Sett"]["info"])

