from typing import Any, Union, Dict, List, Optional

from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from chat.services import (
    _add_message,
    get_chats_with_last_message_by_user,
    get_chat_messages,
    get_user_by_token,
)
from core.models import User

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> Union[User, None]:
        await websocket.accept()
        return await self.auth(websocket)

    async def auth(self, websocket: WebSocket) -> Union[User, None]:
        data: Any = await websocket.receive_json()

        try:
            if data["request"]["type"] == "CONNECT":
                token: str = data["request"]["body"]["token"]
                user: Union[User, None] = get_user_by_token(token)
                if user:
                    self.active_connections[user.id] = websocket
                    await self.send_auth_status("SUCCESS", websocket)
                    return user
        except KeyError:
            print(KeyError)

        await self.send_auth_status("FAILED", websocket)
        return None

    def get_websocket_by_user(self, user: User) -> Union[None, WebSocket]:
        try:
            return self.active_connections[user.id]
        except KeyError:
            return None

    async def send_personal_json(
        self, json: dict, websocket: WebSocket = None, user: Optional[User] = None
    ) -> None:
        if websocket:
            await websocket.send_json(json)
        elif user:
            websocket = self.get_websocket_by_user(user)

            if websocket:
                await websocket.send_json(json)
        return

    @staticmethod
    async def send_auth_status(status: str, websocket: WebSocket) -> None:
        await websocket.send_json(
            {"response": {"type": "AUTHENTICATION", "status": status}}
        )
        return

    def disconnect(self, user: User) -> None:
        try:
            del self.active_connections[user.id]
        except KeyError:
            pass
        return


manager: ConnectionManager = ConnectionManager()


@router.get("/")
async def get(
    request: Request, response_class: HTMLResponse = HTMLResponse
) -> HTMLResponse:
    with open(
        "C:\\Users\\Mapct\\projects\\infa\\hosting\\templates\\index.html", "r"
    ) as html:
        return HTMLResponse(html.read(), status_code=200)


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    user = await manager.connect(websocket=websocket)
    if not user:
        return

    await send_chats(user)

    try:
        while True:
            data = await websocket.receive_json()
            await process_request(data, user)
    except WebSocketDisconnect:
        manager.disconnect(user=user)


async def process_request(data: dict, user: User) -> None:
    try:
        print(data)
        if data["request"]["type"] == "MESSAGE":
            await add_message_and_send_to_companion(data=data, user=user)

        elif data["request"]["type"] == "GET_MESSAGES":
            await send_chat_messages(data=data, user=user)
    except KeyError:
        pass
    return


async def send_chats(user: User) -> None:
    if user:
        chats = get_chats_with_last_message_by_user(user=user)

        data = {"response": {"type": "CHATS", "body": {"chats": chats}}}
        return await manager.send_personal_json(json=data, user=user)


async def add_message_and_send_to_companion(data: dict, user: User) -> None:
    chat_id = data["request"]["body"]["chat_id"]
    message = data["request"]["body"]["message"]
    if chat_id and message:
        companion: Union[User, None] = _add_message(
            user=user, chat_id=chat_id, message=message
        )
        if companion:
            await send_new_message(
                users=[user, companion], chat_id=chat_id, message=message
            )


async def send_chat_messages(data: dict, user: User) -> None:
    chat_id = data["request"]["body"]["chat_id"]
    messages = get_chat_messages(user=user, chat_id=chat_id)
    if messages:
        response = {"response": {"type": "MESSAGES", "body": {"messages": messages}}}
        await manager.send_personal_json(json=response, user=user)


async def send_new_message(users: List[User], chat_id: int, message: str) -> None:
    response = {
        "response": {
            "type": "MESSAGE",
            "body": {"message": message, "chat_id": chat_id},
        }
    }
    for user in users:
        await manager.send_personal_json(json=response, user=user)
