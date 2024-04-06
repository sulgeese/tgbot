from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.requests import select_current_events

router = APIRouter(prefix="")
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    data = await select_current_events(request.state.session)
    return templates.TemplateResponse(request=request, name="index.html", context={"data": data})
