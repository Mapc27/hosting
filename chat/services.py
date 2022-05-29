from typing import Any, Dict, Union, Tuple

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.settings import get_db
from auth.database import get_user_by_email
from auth.scheme import TokenData
from auth.token import verify_token
from core.models import Chat, User, ChatMessage


def get_user_by_token(token: str, db: Session = Depends(get_db)) -> Union[User, None]:
    token_data: Union[HTTPException, TokenData] = verify_token(token)
    if token_data is not HTTPException:
        user = get_user_by_email(db, token_data.email)
        return user
    return None


def add_message_(
    user: Union[User, None], chat_id: int, message: str, db: Session = Depends(get_db)
) -> Union[Tuple[Dict, User], None]:
    """
    :return: new chat_message
    """
    if not user:
        return None

    chat: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat or user.id not in [chat.user1_id, chat.user2_id]:
        return None

    chat_message = ChatMessage(content=message, user_id=user.id, chat_id=chat.id)
    db.add(chat_message)
    db.commit()

    return (
        chat_message.as_dict(),
        chat.user1 if chat.user1_id != user.id else chat.user2,
    )


def get_chats_with_last_message_by_user(
    user: User, db: Session = Depends(get_db)
) -> Dict[Any, Any]:
    sql_statement = f"""
    select json_agg(json_build_object(
    'chat_id', chat_id,
    'companion', json_build_object('id', id, 'name', name, 'surname', surname, '_phone_number', _phone_number,
     'phone_country_code', phone_country_code, 'email', email, 'image', image),
    'last_message', last_message,
    'unread_message_count', (select count(id) from chat_message where chat_message.chat_id = subquery.chat_id
     and chat_message.user_id != {user.id} and chat_message.read = false)
        )) from (
        (
            select chat.id as chat_id, "user".id as id, "user".name as name, "user".surname as surname,
             "user"._phone_number as _phone_number, "user".phone_country_code as phone_country_code,
              "user".email as email, "user".image as image,
            chat_message as last_message
            from chat left join chat_message on chat.id = chat_message.chat_id, "user"
            where chat.user1_id = {user.id} and "user".id = chat.user2_id
              and (chat_message.created_at is null or chat_message.created_at =
            (select max (chat_message.created_at) from chat_message where chat_id = chat.id))
        ) union
        (
            select chat.id as chat_id, "user".id as id, "user".name as name, "user".surname as surname,
             "user"._phone_number as _phone_number, "user".phone_country_code as phone_country_code,
              "user".email as email, "user".image as image,
            chat_message as last_message
            from chat left outer join chat_message on chat.id = chat_message.chat_id, "user"
            where chat.user2_id = {user.id} and "user".id = chat.user1_id
              and (chat_message.created_at is null or chat_message.created_at =
            (select max (chat_message.created_at) from chat_message where chat_id = chat.id))
        )
    ) as subquery;
    """

    result = db.execute(sql_statement)

    result_dict = {}
    for i in result:
        result_dict = i[0]
    return result_dict


def get_chat_messages_and_mark_read(
    user: User, chat_id: int, db: Session = Depends(get_db)
) -> Union[None, dict, str]:
    chat: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return "Chat not found"

    if user.id not in [chat.user1_id, chat.user2_id]:
        return "User not in chat"

    mark_all_messages_as_read(user, chat_id, db)

    sql_statement = f"""
        select json_agg(json_build_object('id', id, 'created_at', created_at, 'updated_at', updated_at,
        'content', content, 'user_id', user_id, 'chat_id', chat_id, 'read', read))
        from chat_message where chat_id = {chat_id};
    """

    result = db.execute(sql_statement)

    result_dict = {}
    for i in result:
        result_dict = i[0]
        break
    return result_dict


def mark_all_messages_as_read(user: User, chat_id: int, db: Session) -> None:
    unread_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.chat_id == chat_id,
            ChatMessage.user_id != user.id,
            ChatMessage.read == False,
        )
        .all()
    )
    for message in unread_messages:
        message.read = True
    db.commit()
