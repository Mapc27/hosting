from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.views import Session, get_db
from auth import scheme
from auth.database import create_user
from auth.token import create_access_token, get_current_user, authenticate_user

router = APIRouter(prefix="/user", tags=["authentication"])


@router.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password or login",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/create')
def create(user: scheme.UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/logout")
def logout(user: scheme.User = Depends(get_current_user)):
    token_data = scheme.TokenData(email=user.email, expires=0)
    return token_data
