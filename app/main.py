from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.ddragon import get_latest_version, get_items

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    version = get_latest_version()
    items = get_items(version)
    return templates.TemplateResponse(
        request, "index.html", {"version": version, "items": items.values()}
    )

