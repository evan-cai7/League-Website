from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.ddragon import get_latest_version, get_items, get_champions

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    version = get_latest_version()
    items = get_items(version)
    return templates.TemplateResponse(
        request, "index.html", {"version": version, "items": items.values()}
    )

@app.get("/build")
def build(request: Request):
    version = get_latest_version()
    champs = get_champions(version)
    champ_list = sorted(champs.values(), key=lambda c: c["name"])
    return templates.TemplateResponse(
        request, "build.html", {"version": version, "champs": champ_list}
    )
