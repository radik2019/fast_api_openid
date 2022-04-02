from turtle import title
from fastapi import APIRouter
from . import users, applications, login, web_interface

router = APIRouter(prefix="/backoffice")

router.include_router(users.router)

router.include_router(applications.router)

login_router = APIRouter(prefix="")

login_router.include_router(login.router)
login_router.include_router(web_interface.router)



