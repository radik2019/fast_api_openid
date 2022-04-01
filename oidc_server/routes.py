from fastapi import APIRouter
from .controllers import backoffice

api_v1_router = APIRouter(prefix="/api/v1")

api_v2_router = APIRouter(prefix="")

api_v1_router.include_router(backoffice.router)
api_v2_router.include_router(backoffice.login_router)