import datetime
from typing import Dict, List, Optional
import secrets
from urllib import request
from fastapi import APIRouter, HTTPException, Depends, Header,Request, Response
from odmantic import ObjectId
from pydantic import SecretStr, SecretBytes, ValidationError
from smartidentity.database import engine
from smartidentity.models.application import  Application, AppCredential
from smartidentity.models.user import User, Cookie, Token
from smartidentity.utils.debugging import dbg
from smartidentity.auth import *
from smartidentity.config import ENCRYPT_TOKEN, tok
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=ENCRYPT_TOKEN)
auth_handler = AuthHandler()
router = APIRouter(prefix="")
templates = Jinja2Templates(directory="smartidentity/templates")


@router.get("/refresh", tags=["login"])
async def refresh_token(from_value: Optional[str] = None,
                            username=Depends(auth_handler.auth_wrapper),
                            auth: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    hd = Header(None, alias="Authorization")

    dbg(username, auth)


@router.post(
    "/login_form",
    response_class=HTMLResponse, tags=["login"]
)
async def post_basic_form(
    request: Request,
    response: Response,
    username: str = Form(default=''),
    password: str = Form(default='')
):

    if not (username and password):
        return templates.TemplateResponse("login.html", {"request": request, "message": "L'username e password sono obbligatori"})
    collection = await engine.find(User, User.username == username)
    user: Optional[User] = None
    for user_ in collection:
        if user_.username == username:
            user = user_
            break
    
    if (user is None) or (not auth_handler.verify_password(password, user.password)):
        return templates.TemplateResponse("login.html", {"request": request, "message": "Nome utente o password errata"})
    token_id =  Token(**{
        "lifetime": SESSION_EXP_SEC,
        "is_valid": True,
        "kind": "access_token", 
        "jti": secrets.token_urlsafe()
    })
    exp_token =  Token(**{
        "lifetime": REFRESHED_EXP_SEC,
        "is_valid": True,
        "kind": "refresh_token",
        "jti": secrets.token_urlsafe()
    })

    user = user.dict()
    user["tokens"].append(token_id)
    user["tokens"].append(exp_token)
    user = User(**user)
    await engine.save(user)
    token = await auth_handler.encode_token(user.username, token_id, "access_token")
    response.headers["X-secu"] = token
    tok = f"Bearer {token}"
    response.set_cookie(key="access_token", value='Bearer ' + token, httponly=True)
    return RedirectResponse("http://0.0.0.0:9000/api/v1/backoffice/users")
    return templates.TemplateResponse("login.html", {"request": request, "token": token, "message": "il token e' stato generato correttamente"})




#  let headers = new Headers({'Content-Type': 'application/json'});  
#  headers.append('Authorization','Bearer ')
#  let options = new RequestOptions({headers: headers});
#  return this.http.post(APIname,body,options)
#   .map(this.extractData)
#   .catch(this.handleError);



@router.get("/login_form", response_class=HTMLResponse, tags=["login"])
async def post_basic_form(request: Request, response: Response, username: str = Form(default=''), password: str = Form(default='')):

    if not (username and password):
        return templates.TemplateResponse("login.html", {"request": request, "message": "L'username e password sono obbligatori"})
    collection = await engine.find(User, User.username == username)
    user: Optional[User] = None
    for user_ in collection:
        if user_.username == username:
            user = user_
            break
    
    if (user is None) or (not auth_handler.verify_password(password, user.password)):
        return templates.TemplateResponse("login.html", {"request": request, "message": "Nome utente o password errata"})
    token_id =  Token(**{
        "lifetime": SESSION_EXP_SEC,
        "is_valid": True,
        "kind": "access_token", 
        "jti": secrets.token_urlsafe()
    })
    exp_token =  Token(**{
        "lifetime": REFRESHED_EXP_SEC,
        "is_valid": True,
        "kind": "refresh_token",
        "jti": secrets.token_urlsafe()
    })

    user = user.dict()
    user["tokens"].append(token_id)
    user["tokens"].append(exp_token)
    user = User(**user)
    await engine.save(user)
    token = await auth_handler.encode_token(user.username, token_id, "access_token")
    response.headers["X-secu"] = token
    response.set_cookie(key="access_token", value='Bearer ' + token, httponly=True)

    return templates.TemplateResponse("login.html", {"request": request, "token": token, "message": "il token e' stato generato correttamente"})





@router.post('/login', tags=["login"])
async def login(rqst: Request,
    auth_details: AuthDetails,
    response: Response,
    auth: str = Header(None, alias="Authorization"),
    
    ):
    global tok

    q = () if not auth_details else User.username == auth_details.username
    collection = await engine.find(User, q)
    user: Optional[User] = None
    for user_ in collection:
        if user_.username == auth_details.username:
            user = user_
            break
    
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user.password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token_id =  Token(**{
        "lifetime": SESSION_EXP_SEC,
        "is_valid": True,
        "kind": "access_token", 
        "jti": secrets.token_urlsafe()
    })
    exp_token =  Token(**{
        "lifetime": REFRESHED_EXP_SEC,
        "is_valid": True,
        "kind": "refresh_token",
        "jti": secrets.token_urlsafe()
    })

    user = user.dict()
    user["tokens"].append(token_id)
    user["tokens"].append(exp_token)
    user = User(**user)
    await engine.save(user)

    token = await auth_handler.encode_token(user.username, token_id, "access_token")
    # auth.credentials = token
    ref_token = await auth_handler.encode_token(user.username, exp_token, "refresh_token")
    # response.set_cookie(key="access_token", value='Bearer ' + token, httponly=True)
    tok = token
    return {"token_id": token, "refresh_token": ref_token}




