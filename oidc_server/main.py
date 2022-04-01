from fastapi import FastAPI
from .routes import api_v1_router, api_v2_router

from fastapi import FastAPI, Request
import time
from .routes import api_v1_router, api_v2_router
from smartidentity.config import *
from smartidentity.utils.debugging import dbg

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    

    dbg(f"{request.method}  {request.headers['referer']}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # response.headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJuYmYiOjE2NDg3Mjg0MDUsImp0aSI6Il9WZV9LbTZpcExpM29faEhSbWNEMmJWdkx0RU1vRzhpZk1hX280NkxhU2siLCJyb2xlIjpmYWxzZSwiZXhwIjoxNjQ4NzMxODI1LCJpYXQiOjE2NDg3Mjg0MDV9.XXJah0PKJoEsMHPqBcLvSdHzqH8z_PuGVT88jmAzzM8"
    dbg(dir(response))
    response.headers["dskfgj"] = "348957934"
    dbg(response.headers)
    return response


app.include_router(api_v1_router)
app.include_router(api_v2_router)



