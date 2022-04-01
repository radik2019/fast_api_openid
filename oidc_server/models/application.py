import datetime
from typing import List, Optional
from slugify import slugify
from odmantic import EmbeddedModel, Model, Field
from smartidentity.database import engine


class AppCredential(EmbeddedModel):
    client_id: str
    client_secret: str
    class Config:
        collection = "app_credentials"


class Application(Model):
    # nome applicazione
    name : str
    slug: str
    url : str
    is_active: bool

    # Uris di redirect
    redirect_uris: List[str]
    response_types: List[str]
    grant_types: List[str]
    scope: List[str]

    # Applicazione registrata
    # Viene generato quando si registra l'applicazione
    app_credentials: Optional[AppCredential]


    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        collection = "applications"


async def create_application():
    ...
