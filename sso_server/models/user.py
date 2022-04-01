import datetime
from typing import List, Optional, Optional, Dict

import secrets

from enum import Enum, unique
# from wsgiref.validate import validator
from odmantic import Model, ObjectId, Reference, EmbeddedModel, Field
from pydantic import SecretStr, EmailStr, validator
from passlib.context import CryptContext
from pydantic.fields import ModelField

from .application import Application
from sso_server.utils.debugging import dbg
from sso_server.config import (
    SESSION_EXP_MIN, SESSION_EXP_SEC, SESSION_EXP_DAYS, 
    REFRESHED_EXP_MIN, REFRESHED_EXP_SEC, REFRESHED_EXP_DAYS,
    ALGORITHMS
)
from sso_server.database import engine



class TokenKind(str, Enum):
    REFRESH = "refresh_token"
    ACCESS = "access_token"


class Token(EmbeddedModel):
    lifetime: int
    is_valid: bool = True
    kind: TokenKind
    jti: str
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Cookie(EmbeddedModel):
    value: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    lifetime: int
    user_agent: str
    application: Application = Reference(key_name="application_id")
    is_valid: bool = True
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class User(Model):
    first_name: str
    last_name: str
    avatar: str
    username: str = Field(unique=True)
    password: str
    work_email: EmailStr
    tokens: List[Token] = list()
    cookies: List[Cookie] = list()
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        collection = "users"
        parse_doc_with_default_factories = True

    def get_tokens(self):
        return self.tokens
    
