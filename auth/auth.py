from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from auth.scheme import Profile
from core.models import User
from app.settings import get_db
from auth import scheme
from auth.database import get_user_by_email, create_user, change_user_data
from auth.token import verify_token, create_access_token, get_current_user

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
def logout(user: scheme.User = Depends(get_current_user)) -> scheme.TokenData:
    token_data = scheme.TokenData(email=user.email, expires=0)
    return token_data


@router.get("/profile")
def profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/change_profile")
def change_profile(
    profile_scheme: Profile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return change_user_data(profile_scheme, user, db)
