from typing import Any, Union

from sqlalchemy.orm import Session

from core.models import User
from auth.hashed import get_password_hash
from auth.scheme import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    hashed = get_password_hash(user.password)
    db_user: User = User(
        password=hashed,
        email=user.email,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: Union[str, None, Any]) -> User:
    user: User = db.query(User).filter(User.email == email).first()
    return user
