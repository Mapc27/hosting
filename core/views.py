from fastapi import APIRouter, Depends, UploadFile, Form, File
from sqlalchemy.orm import Session

from app.settings import get_db
from auth.token import get_current_user
from core.models import User
from core.schemas import ChatCreate
from core.services import (
    create_chat_,
    get_housing,
    get_chat_short_,
    create_housing_image_,
    delete_housing_image_,
)

router = APIRouter(prefix="", tags=["core"])


@router.post("/chats")
async def create_chat(
    chat_scheme: ChatCreate,
    user1: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:

    if user1.id == chat_scheme.user_id:
        return {"detail": "user_id is id of current user"}

    user2: User = db.query(User).filter(User.id == chat_scheme.user_id).first()
    if not user2:
        return {"detail": f"No such user with user_id = {chat_scheme.user_id}"}

    chat = create_chat_(user1, user2, db)
    if not chat:
        return {"detail": "Chat already exists"}

    return get_chat_short_(user1.id, chat.id, db)


@router.get("/chats/short/{chat_id}")
async def get_chat_short(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    json_chat = get_chat_short_(user.id, chat_id, db)
    return (
        json_chat
        if json_chat
        else {"detail": "Chat not found or user not a chat member"}
    )


@router.post("/housing/image/")
async def create_housing_image(
    housing_id: int = Form(...),
    is_main: bool = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    image: UploadFile = File(...),
) -> dict:
    if not image:
        return {"detail": "No upload file sent"}

    # check permissions
    housing = get_housing(user, housing_id, db)
    if not housing:
        return {"detail": "You is not owner or housing doesn't exists"}

    housing_image = await create_housing_image_(
        image, housing, db, True if is_main else None
    )
    return housing_image.as_dict()


@router.delete("/housing/image/")
async def delete_housing_image(
    housing_id: int = Form(...),
    image_id: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # check permissions
    housing = get_housing(user, housing_id, db)
    if not housing:
        return {"detail": "You is not owner or housing doesn't exists"}

    housing_image = delete_housing_image_(housing_id, image_id, db)
    return (
        housing_image.as_dict()
        if housing_image
        else {"detail": "This housing doesn't have this image"}
    )
