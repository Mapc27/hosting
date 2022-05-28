from sqlalchemy.orm import Session

from core.models import Chat, User


def create_chat_(user1: User, user2: User, db: Session) -> int:
    chat: Chat = Chat(user1_id=user1.id, user2_id=user2.id)
    db.add(chat)
    db.commit()
    return chat.id
