from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.settings import get_db
from auth import scheme
from auth.database import get_user_by_email, create_user
from auth.scheme import Wishlist
from auth.services import create_wishlist_, get_wishlist_, delete_wishlist_
from auth.token import verify_token, create_access_token, get_current_user
from core.models import User

router = APIRouter(prefix="/user", tags=["authentication"])


@router.post("/login")
async def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    user = get_user_by_email(db, request.username)
    if not user or not verify_token(user.password, request.password):
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
def logout(user: User = Depends(get_current_user)) -> scheme.TokenData:
    token_data = scheme.TokenData(email=user.email, expires=0)
    return token_data


@router.get("/wishlist")
def get_wishlist(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    return {"user_id": user.id, "wishlist": get_wishlist_(user, db)}


@router.post("/wishlist")
def create_wishlist(
    wishlist: Wishlist,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    liked_housing = create_wishlist_(user, wishlist.housing_id, db)
    if not liked_housing:
        return {"detail": "Like already exists"}
    return {"user_id": user.id, "wish": liked_housing.as_dict()}


@router.delete("/wishlist")
def delete_wishlist(
    wishlist: Wishlist,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    liked_housing = delete_wishlist_(user, wishlist.housing_id, db)
    if not liked_housing:
        return {"detail": "Like doesn't exists"}
    return {"user_id": user.id, "wish": liked_housing.as_dict()}
