from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.ddragon import get_latest_version, get_items, get_champions
from app.threat import build_threat_profile

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

@app.post("/recommend")
async def recommend(request: Request):
    form = await request.form()
    my_champ = form["my_champ"]

    enemies = []
    for i in range(1, 6):
        enemies.append({
            "champion": form[f"enemy{i}"],
            "kills": int(form[f"enemy{i}_kills"]),
            "deaths": int(form[f"enemy{i}_deaths"]),
            "assists": int(form[f"enemy{i}_assists"]),
        })
    champs = get_champions(get_latest_version())
    profile = build_threat_profile(enemies, champs)

    return templates.TemplateResponse(
        request,
        "result.html",
        {"my_champ": my_champ, "enemies": enemies, "profile": profile},
    )