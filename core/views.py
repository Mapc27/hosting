from typing import Any

from fastapi import APIRouter, Depends, UploadFile, Form, File, HTTPException
from starlette import status

from app.settings import Session, get_db
from auth.token import get_current_user
from core.models import (
    User,
    HousingCategory,
    HousingType,
    ComfortCategory,
    Comfort,
)
from core.schemas import (
    ChatCreate,
    HouseCreate,
    CategoryCreate,
    HousingTypeCreate,
    ComfortCategoryCreate,
    ComfortCreate,
    HousingPricingCreate,
)
from core.services import (
    create_chat_,
    create_housing,
    create_comfort,
    create_housing_comfort,
    create_housing_pricing,
    get_housing_by_user,
    get_chat_short_,
    create_housing_image_,
    delete_housing_image_,
    set_main_housing_image_,
    get_pagination_data,
    get_housing_,
    create_characteristics,
    delete_housing_,
)

router = APIRouter(prefix="", tags=["core"])


@router.get("/offers")
def offers(db: Session = Depends(get_db), page: int = 0, limit: int = 50) -> Any:
    return get_pagination_data(db, page, limit)


def check_permissions_on_housing(user: User, housing_id: int, db: Session) -> None:
    if not get_housing_by_user(user, housing_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissions denied. User with id = {user.id} is not owner or housing with id = {housing_id} "
            "doesn't exists ",
        )


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

    check_permissions_on_housing(user, housing_id, db)

    housing_image = await create_housing_image_(
        image, housing_id, db, True if is_main else None
    )
    return housing_image.as_dict()


@router.delete("/housing/image/")
async def delete_housing_image(
    housing_id: int = Form(...),
    image_id: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    check_permissions_on_housing(user, housing_id, db)

    housing_image = delete_housing_image_(housing_id, image_id, db)
    return (
        housing_image.as_dict()
        if housing_image
        else {
            "detail": f"This housing with id = {housing_id} doesn't have this image with id = {image_id}"
        }
    )


@router.put("/housing/image/set_main")
async def set_main_housing_image(
    housing_id: int = Form(...),
    image_id: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    check_permissions_on_housing(user, housing_id, db)

    housing_image = set_main_housing_image_(housing_id, image_id, db)
    return (
        housing_image.as_dict()
        if housing_image
        else {
            "detail": f"This housing with id = {housing_id} doesn't have this image with id = {image_id}"
            f" or main image"
        }
    )


@router.post("/housing")
def create_house(
    house_scheme: HouseCreate,
    category_id: int,
    type_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    housing = create_housing(house_scheme, user, category_id, type_id, db)
    create_characteristics(house_scheme, housing, db)

    return housing.id


@router.delete("/housing")
def delete_housing(
    housing_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    check_permissions_on_housing(user, housing_id, db)
    housing = delete_housing_(housing_id, db)

    return housing.as_dict()


@router.get("/housing/{housing_id}")
def get_housing(housing_id: int, db: Session = Depends(get_db)) -> dict:
    return get_housing_(housing_id, db)
