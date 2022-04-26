from sqlalchemy.orm import Session

from app import models
from auth.hashed import get_password_hash
from auth.scheme import UserCreate


def create_user(db: Session, user: UserCreate):
    hashed = get_password_hash(user.password)
    db_user = models.User(name=user.name, password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
