    
from datetime import datetime, timedelta


from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException, Security, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from odmantic import Model, Reference
from odmantic import ObjectId
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from smartidentity.config import (
    SESSION_EXP_MIN, SESSION_EXP_SEC, SESSION_EXP_DAYS, 
    REFRESHED_EXP_MIN, REFRESHED_EXP_SEC, REFRESHED_EXP_DAYS,
    ALGORITHMS
)

from smartidentity.utils.debugging import dbg
from smartidentity.database import engine
from smartidentity.models.user import User
from smartidentity.models.application import Application, AppCredential
import binascii
from base64 import b64decode
from typing import Optional

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from fastapi.responses import HTMLResponse, RedirectResponse


class AuthDetails(BaseModel):
    username: str
    password: str


class MyHTTPBearer(HTTPBearer):
    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")

        scheme, credentials = get_authorization_scheme_param(authorization)

        if not (authorization and scheme and credentials):

            if self.auto_error:
                

                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class AuthHandler():
    security = MyHTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET_token'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    async def encode_token(self, user_id, login_payload, token_type):
        usr = await engine.find_one(User, User.username == user_id)
        last_tokens = usr.tokens[-2:]
        token_obj = last_tokens[0] if last_tokens[0].kind == token_type else last_tokens[1]
        payload = {
            # 'iss': 'url_smartidentity',
            'sub': user_id,
            # 'aud': '/api/v1/applications',
            'nbf': token_obj.created,
            'jti': token_obj.jti,
            'role': usr.is_admin,
            'exp': token_obj.created + timedelta(seconds=token_obj.lifetime),
            'iat': token_obj.created
        }
        jwbt = jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )
        return jwbt

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=ALGORITHMS)
            return payload['sub']
        except jwt.ExpiredSignatureError:

            raise HTTPException(status_code=401, detail='Signature has expired')

        except jwt.JWTClaimsError as e:

            raise HTTPException(status_code=401, detail='Invalid token')

    async def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        clnt = self.decode_token(auth.credentials)

        return clnt

