from typing import Any, Dict, Union, List, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.settings import get_db
from core.models import Chat, User, ChatMessage
from auth.database import get_user_by_email
from auth.scheme import TokenData
from auth.token import verify_token


def get_user_by_token(token: str) -> Union[User, None]:
    token_data: Union[HTTPException, TokenData] = verify_token(token)
    if token_data is not HTTPException:
        with next(get_db()) as db:
            user = get_user_by_email(db, token_data.email)
        return user
    return None


def _add_message(
    user: Union[User, None], chat_id: int, message: str
) -> Union[Tuple[Dict, User], None]:
    """
    :param db:
    :param user:
    :param chat_id:
    :param message:
    :return: new chat_message
    """
    if not user:
        return None

    with next(get_db()) as db:
        chat: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat or not (chat.user1_id == user.id or chat.user2_id == user.id):
            return None

        chat_message = ChatMessage(content=message, user_id=user.id, chat_id=chat.id)
        db.add(chat_message)
        db.commit()

        return (
            chat_message.as_dict(),
            chat.user1 if chat.user1_id != user.id else chat.user2,
        )


def get_chats_with_last_message_by_user(user: User) -> Dict[Any, Any]:
    sql_statement = f"""
        select json_agg(json_build_object(
        'chat_id', chat_id,
        'companion', json_build_object('id', id, 'name', name, 'surname', surname, '_phone_number', _phone_number, 'phone_country_code', phone_country_code, 'email', email, 'image', image),
        'last_message', last_message)) from (
            (
                select chat.id as chat_id, "user".id as id, "user".name as name, "user".surname as surname, "user"._phone_number as _phone_number, "user".phone_country_code as phone_country_code, "user".email as email, "user".image as image,
                chat_message as last_message
                from chat, chat_message, "user"
                where chat.user1_id = {user.id} and chat_message.chat_id = chat.id and chat_message.created_at =
                (select max (chat_message.created_at) from chat_message where chat_id = chat.id)
                and "user".id = chat.user2_id
            ) union
            (
                select chat.id as chat_id, "user".id as id, "user".name as name, "user".surname as surname, "user"._phone_number as _phone_number, "user".phone_country_code as phone_country_code, "user".email as email, "user".image as image,
                chat_message as last_message
                from chat, chat_message, "user"
                where chat.user2_id = {user.id} and chat_message.chat_id = chat.id and chat_message.created_at =
                (select max (chat_message.created_at) from chat_message where chat_id = chat.id)
                and "user".id = chat.user1_id
            )
        ) as subquery;
    """

    with next(get_db()) as db:
        result = db.execute(sql_statement)
    result_dict = {}
    for i in result:
        result_dict = i[0]
    return result_dict


def get_chat_messages(user: User, chat_id: int) -> Union[None, dict]:
    with next(get_db()) as db:
        chat: Chat = db.query(Chat).filter(Chat.id == chat_id).first()

        if chat.user1_id != user.id and chat.user2_id != user.id:
            return None

        sql_statement = f"""
            select json_agg(json_build_object('id', id, 'created_at', created_at, 'updated_at', updated_at,
            'content', content, 'user_id', user_id, 'chat_id', chat_id))
            from chat_message where chat_id = {chat_id};
        """

        result = db.execute(sql_statement)
    result_dict = {}
    for i in result:
        result_dict = i[0]
    return result_dict
