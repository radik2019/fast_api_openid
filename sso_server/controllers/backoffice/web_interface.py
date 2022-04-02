


from fastapi import APIRouter, Request

from sso_server.database import engine

from sso_server.utils.debugging import dbg
from sso_server.auth import *

from fastapi.templating import Jinja2Templates
from fastapi import Form

from fastapi.responses import HTMLResponse
from starlette.requests import Request


router = APIRouter(prefix="", tags=["Web Interface"])

templates = Jinja2Templates(directory="sso_server/templates")



@router.get(
    "/home",
    response_class=HTMLResponse
)
async def get_home_page(
    request: Request
):

    return templates.TemplateResponse("home.html", {"request": request, "message": "Nome utente o password errata"})



