from fastapi import FastAPI
from .routes import api_v1_router, api_v2_router

from fastapi import FastAPI, Request
import time
from .routes import api_v1_router, api_v2_router
from sso_server.config import *
from sso_server.utils.debugging import dbg
from sso_server.config import setting
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=setting.TITLE,
    description = setting.DESCRIPTION,
    docs_url=setting.DOCS_URL,
    redoc_url=setting.REDOC_URL,
    version=setting.VERSION
)

# app.mount("sso_server/templates/images")
app.mount("/sso_server/static", StaticFiles(directory="sso_server/static"), name="static")


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     dbg(f"{request.headers} ")
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     return response



app.include_router(api_v1_router)
app.include_router(api_v2_router)



