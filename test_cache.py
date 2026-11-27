import time
from app.ddragon import get_latest_version, get_items

version = get_latest_version()

start = time.time()
get_items(version)
print("first call: ", round(time.time() - start, 4))

start = time.time()
get_items(version)
print("second call:", round(time.time() - start, 4))