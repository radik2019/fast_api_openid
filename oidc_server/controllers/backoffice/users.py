import datetime
from lib2to3.pgen2 import token
from turtle import title
from typing import Dict, List, Optional
import secrets
from urllib import request
from fastapi import APIRouter, HTTPException, Depends, Header,Request, Response
from odmantic import ObjectId
from pydantic import SecretStr, SecretBytes, ValidationError
from smartidentity.database import engine
from smartidentity.models.application import  Application, AppCredential
from smartidentity.models.user import (
    User, Cookie, Token
)
from smartidentity.utils.debugging import dbg
from smartidentity.auth import *
from smartidentity.config import ENCRYPT_TOKEN

from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from fastapi.responses import HTMLResponse


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=ENCRYPT_TOKEN)
auth_handler = AuthHandler()
router = APIRouter(prefix="/users")

templates = Jinja2Templates(directory="./smartidentity/templates")

@router.post("/addtoken", tags=["token"])
async def set_token(token: Token, id: ObjectId):
    
    user = await engine.find_one(User, User.id == id)
    await user.tokens.append(Token(token))
    collection = await engine.save(user)
    return collection



@router.get("", tags=["users"])
async def get_users():
    
    collection = await engine.find(User, ())
    return collection


@router.get("/{id}", response_model=User, tags=["users"])
async def get_user_by_id(id: ObjectId):
    user = await engine.find_one(User, User.id == id)
    if user is None:
        raise HTTPException(404)
    return user


@router.post("", response_model=User, tags=["users"])
async def create_user(data: User):

    hashed_password = auth_handler.get_password_hash(data.password)
    data.password = hashed_password
    inst = await engine.save(data)
    return inst


@router.put("/{id}", response_model=User, tags=["users"])
async def update_user_by_id(data: User, id: ObjectId):
    data =data.dict()
    user = await engine.find_one(User, User.id == id)
    if user is None:
        raise HTTPException(status_code=400)
    user = user.dict()
    for i in data:
        if i != "created" and i != "id":
            user[i] = data[i]
            if i == "password":
                user["password"] = auth_handler.get_password_hash(data[i])
    user["updated"] = datetime.datetime.utcnow()
    user = User(**user)
    inst = await engine.save(user)
    return inst


@router.patch("/{id}", response_model=User, tags=["users"])
async def partial_update_user_by_id(data: dict, id: ObjectId):
    user = await engine.find_one(User, User.id == id)
    if user is None:
        raise HTTPException(404)
    user = user.dict()
    for i in data:
        if i != "created" and i != "id":
            user[i] = data[i]
            if i == "password":
                user["password"] = auth_handler.get_password_hash(data[i])
    user["updated"] = datetime.datetime.utcnow()
    user = User(**user)
    inst = await engine.save(user)
    return inst


@router.delete("/{id}", response_model=User, tags=["users"])
async def delete_user_by_id(id: ObjectId):
    user = await engine.find_one(User, User.id == id)
    if user is None:
        raise HTTPException(404)
    await engine.delete(user)
    return user






