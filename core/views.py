from fastapi import APIRouter, Depends

from app.settings import Session, get_db
from auth.token import get_current_user
from core.models import Chat, User
from core.schemas import ChatCreate
from core.services import create_chat_

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
