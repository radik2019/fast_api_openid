import datetime
from fastapi import APIRouter, HTTPException, Depends
from odmantic import ObjectId
from smartidentity.database import engine
from smartidentity.models import Application
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from smartidentity.config import ENCRYPT_TOKEN, tok
from smartidentity.auth import AuthHandler

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=ENCRYPT_TOKEN)
auth_handler = AuthHandler()
router = APIRouter(prefix="/users")

router = APIRouter(prefix="/applications")


@router.get("/{id}", response_model=Application, tags=["Applications"])
async def get_application_by_id(id: ObjectId):
    application = await engine.find_one(Application, Application.id == id)
    if application is None:
        raise HTTPException(404)
    return application


@router.get("", tags=["Applications"])
async def get_applications(username=Depends(auth_handler.auth_wrapper), head=tok, tags=["Applications"]):
    collection = await engine.find(Application, ())
    return collection


@router.post("", response_model=Application, tags=["Applications"])
async def create_application(data: Application):
    """create application"""
    inst = await engine.save(data)
    return inst


@router.delete("/{id}", tags=["Applications"])
async def delete_application(id: ObjectId):
    """delete application"""
    application = await engine.find_one(Application, Application.id == id)
    if application is None:
        raise HTTPException(404)
    await engine.delete(application)
    return application


@router.put("/{id}", response_model=Application, tags=["Applications"])
async def update_application(data: dict, id: ObjectId):
    application = await engine.find_one(Application, Application.id == id)
    if application is None:
        raise HTTPException(404)
    application = application.dict()
    for i in data:
        if i in application:
            if i != "created" and i != "id":
                application[i] = data[i]
    application["updated"] = datetime.datetime.utcnow()
    application = Application(**application)
    inst = await engine.save(application)
    return inst

