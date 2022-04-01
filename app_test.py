from typing import Optional
from pydantic import BaseModel

from fastapi import Body, FastAPI, status, Depends
from fastapi.responses import JSONResponse
from sso_server.auth import *
from fastapi.responses import HTMLResponse, RedirectResponse
from sso_server.utils.debugging import *
from sso_server.config import tok


app = FastAPI()

db = list()



class Product(BaseModel):
    name: str
    quantity: int = 0


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=ENCRYPT_TOKEN)

auth_handler = AuthHandler()


import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # dbg(request.headers)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["Authorization"] = tok
    dbg(
        # request.base_url
        request.url
        )
    dbg(request.scope)
    return response



@app.post("/products")
async def upsert_item(product: Product ):


    db.append(product.dict())
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=product.dict())


@app.get("/products",
        tags = ["Prodotti"],
        description = "la lista dei prodotti")
async def upsert_item(headers="cmok", username=Depends(auth_handler.auth_wrapper)):
    
    if not username:
        return RedirectResponse("http://0.0.0.0:9000/login_form", status_code=302)
    print(username)
    return JSONResponse(status_code=status.HTTP_200_OK, content=db)
