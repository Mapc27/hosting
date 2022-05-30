from fastapi import APIRouter, Depends

from app.settings import Session, get_db
from auth.token import get_current_user
from core.models import (
    Chat,
    User,
    HousingCategory,
    HousingType,
    Housing,
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
    create_category,
    create_housing_type,
    create_housing,
    create_comfort_category,
    create_comfort,
    create_housing_comfort,
    create_housing_pricing,
)

router = APIRouter(prefix="", tags=["core"])


@router.post("/chats")
def create_chat(
    chat_scheme: ChatCreate,
    user1: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user2: User = db.query(User).filter(User.id == chat_scheme.user_id).first()

    if not user2:
        return {"detail": f"No such user with user_id = {chat_scheme.user_id}"}

    if user1.id == chat_scheme.user_id:
        return {"detail": "user_id is id of current user"}

    chat = (
        db.query(Chat)
        .filter(Chat.user1_id == user1.id, Chat.user2_id == user2.id)
        .first()
    )
    if chat:
        return {"chat_id": chat.id}
    else:
        return {"chat_id": create_chat_(user1, user2, db)}


@router.post("/housing")
def create_house(
    category_scheme: CategoryCreate,
    house_scheme: HouseCreate,
    type_scheme: HousingTypeCreate,
    comfort_category_scheme: ComfortCategoryCreate,
    comfort_scheme: ComfortCreate,
    housing_pricing_scheme: HousingPricingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    category: HousingCategory = (
        db.query(HousingCategory)
        .filter(HousingCategory.name == category_scheme.name)
        .first()
    )
    if not category:
        category = create_category(category_scheme, db)

    housing_type: HousingType = (
        db.query(HousingType).filter(HousingType.name == type_scheme.name).first()
    )
    if not housing_type:
        housing_type = create_housing_type(type_scheme, db)

    housing = create_housing(house_scheme, user, category, housing_type, db)

    comfort_category: ComfortCategory = (
        db.query(ComfortCategory)
        .filter(ComfortCategory.name == comfort_category_scheme.name)
        .first()
    )
    if not comfort_category:
        comfort_category = create_comfort_category(comfort_category_scheme, db)

    comfort: Comfort = (
        db.query(Comfort).filter(Comfort.name == comfort_category_scheme.name).first()
    )
    if not comfort:
        comfort = create_comfort(comfort_scheme, comfort_category, db)

    create_housing_comfort(comfort, housing, db)

    create_housing_pricing(housing_pricing_scheme, housing, db)
