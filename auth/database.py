from typing import Any, Union

from sqlalchemy.orm import Session

from core.models import User
from auth.hashed import get_password_hash, verify_password
from auth.scheme import UserCreate, Profile, ChangeProfile


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


def change_user_data(profile_scheme: ChangeProfile, user: User, db: Session) -> dict:
    if profile_scheme.name:
        user.name = profile_scheme.name

    if profile_scheme.surname:
        user.surname = profile_scheme.surname

    if profile_scheme.birth_date:
        user.birth_date = profile_scheme.birth_date

    if profile_scheme.phone_number:
        user._phone_number = profile_scheme.phone_number

    if profile_scheme.phone_country_code:
        user.phone_country_code = profile_scheme.phone_country_code

    if profile_scheme.email:
        user.email = profile_scheme.email

    if profile_scheme.old_password and profile_scheme.new_password:
        if verify_password(profile_scheme.old_password, user.password):
            user.password = get_password_hash(profile_scheme.new_password)
        else:
            return {"detail": "The entered password is incorrect"}

    db.add(user)
    db.commit()
    db.refresh(user)
    return {"detail": "Success"}
