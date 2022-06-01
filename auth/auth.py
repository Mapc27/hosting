import os
from typing import Any

from fastapi import Request
from starlette.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config

from auth.hashed import verify_password
from core.models import User
from app.settings import get_db
from auth import scheme
from auth.database import create_user, get_user_by_email
from auth.token import create_access_token, get_current_user

router = APIRouter(prefix="/user", tags=["authentication"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or None
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or None

config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/oauth_login")
async def login_oauth(request: Request) -> Any:
    # redirect_uri = router.url_path_for("/oauth_token")
    redirect_uri = "http://127.0.0.1:8000/oauth_token"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/oauth_token")
async def auth(request: Request) -> JSONResponse:
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_data = await oauth.google.parse_id_token(request, access_token)
    jwt = create_access_token(data={"sub": user_data["email"]})
    return JSONResponse({"result": True, "access_token": jwt})


@router.post("/login")
async def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    user = get_user_by_email(db, request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password or login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password or login",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/create")
def create(user: scheme.UserCreate, db: Session = Depends(get_db)) -> User:
    return create_user(db, user)


@router.post("/logout")
def logout(user: scheme.User = Depends(get_current_user)) -> scheme.TokenData:
    token_data = scheme.TokenData(email=user.email, expires=0)
    return token_data
