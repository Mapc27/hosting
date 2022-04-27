from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

from app.models import User
from app.views import Session
from auth.database import get_user_by_email
from auth.scheme import TokenData

SECRET_KEY = "206dl5m94fa26ca2556c81p16gb7a9563b9qfr099f6f0f4c0a6cf13b88e8d3k7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


def verify_token(
    token: str, credentials_exception: HTTPException
) -> Union[TokenData, HTTPException]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if email is None:
            return credentials_exception
        return TokenData(email=email, expires=expire)
    except JWTError:
        return credentials_exception


async def get_current_user(data: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(data, credentials_exception)
    if token_data == "credentials_exception":
        raise credentials_exception
    db = Session()

    return get_user_by_email(db, token_data.email)
