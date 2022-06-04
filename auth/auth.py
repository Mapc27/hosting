import os
from typing import Any

from fastapi import Request, UploadFile, File
from starlette.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from typing import Union
from starlette.config import Config

from app.settings import get_db
from auth import scheme
from auth.hashed import verify_password
from auth.scheme import Wishlist, CreateWishlist, DeleteWishlist, ChangeProfile
from auth.services import (
    create_wishlist_,
    get_wishlist_,
    delete_wishlist_,
    get_wish_,
    delete_user_image_,
    create_user_image_,
)
from auth.database import get_user_by_email, create_user, change_user_data
from auth.token import create_access_token, get_current_user
from core.models import User, LikedHousing

router = APIRouter(prefix="/user", tags=["authentication"])

# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or None
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or None
GOOGLE_CLIENT_ID = (
    "186699558815-thgrsev7mbcbghv7f3svoej54mgaii8g.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"

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
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/oauth_token")
async def auth(request: Request, db: Session = Depends(get_db)) -> dict:
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_data = access_token["userinfo"]
    user = get_user_by_email(db, user_data["email"])
    if user:
        jwt = create_access_token(data={"sub": user_data["email"]})
        return {"access_token": jwt, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


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
async def create(
    user_scheme: scheme.UserCreate, db: Session = Depends(get_db)
) -> Union[User, dict]:
    user = get_user_by_email(db, user_scheme.email)
    if user:
        return {
            "detail": "User already exists",
        }
    return create_user(db, user_scheme)


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)) -> scheme.TokenData:
    token_data = scheme.TokenData(email=user.email, expires=0)
    return token_data


@router.delete("")
async def delete(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        return {"detail": "Failed"}
    return {"detail": "Success"}


@router.get("/wish/{liked_housing_id}")
async def get_wish(
    liked_housing_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "user_id": user.id,
        "wish": get_wish_(user, db, liked_housing_id=liked_housing_id),
    }


@router.get("/wishlist")
async def get_wishlist(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    return {"user_id": user.id, "wishlist": get_wishlist_(user, db)}


@router.post("/wishlist")
async def create_wishlist(
    wishlist: CreateWishlist,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    liked_housing: Union[LikedHousing, None] = create_wishlist_(
        user, wishlist.housing_id, db
    )
    if not liked_housing:
        return {
            "detail": f"Like already exists or Housing with id = {wishlist.housing_id} doesn't exists"
        }
    return liked_housing.as_dict()


@router.delete("/wishlist")
async def delete_wishlist(
    wishlist: DeleteWishlist,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if wishlist.liked_housing_id:
        liked_housing = delete_wishlist_(
            user, db, liked_housing_id=wishlist.liked_housing_id
        )
    elif wishlist.housing_id:
        liked_housing = delete_wishlist_(user, db, housing_id=wishlist.housing_id)
    else:
        return {"detail": "required liked_housing_id or housing_id"}

    if not liked_housing:
        return {"detail": "Like doesn't exists"}
    return {"user_id": user.id, "wish": liked_housing.as_dict()}


@router.get("/profile")
async def profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/change_profile")
async def change_profile(
    profile_scheme: ChangeProfile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return change_user_data(profile_scheme, user, db)


@router.post("/image")
async def create_user_image(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
) -> dict:
    await create_user_image_(image, user, db)
    return user.as_dict()


@router.delete("/image")
async def delete_user_image(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    delete_user_image_(user, db)
    return user.as_dict()


@router.get("/{user_id}")
async def get_user(
    user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    other_user: User = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        return {"detail": "User not found"}
    return other_user.as_dict()
