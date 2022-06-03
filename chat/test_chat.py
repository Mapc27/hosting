import random
from typing import Callable, Dict, Union

from fastapi.testclient import TestClient
from requests import Response  # type: ignore
from starlette.testclient import WebSocketTestSession


from core.test_core import chat
from main import app


client = TestClient(app)


def auth(func: Callable) -> Callable:
    @chat
    def wrapper(**kwargs: Dict[str, Union[str, Response, dict, int]]) -> None:
        token1 = kwargs.get("token1")
        data = {"request": {"type": "CONNECT", "body": {"token": token1}}}

        with client.websocket_connect("/chat/ws/") as websocket:
            websocket.send_json(data=data)
            response = websocket.receive_json()
            assert response == {
                "response": {"type": "AUTHENTICATION", "status": "SUCCESS"}
            }

            response = websocket.receive_json()
            assert response["response"]["type"] == "CHATS"
            assert response["response"]["body"]["chats"] is not None
            func(websocket, **kwargs)

    return wrapper


@auth
def test_auth(
    websocket: WebSocketTestSession,
    **kwargs: Dict[str, Union[str, Response, dict, int]],
) -> None:
    pass


@auth
def test_get_messages(
    websocket: WebSocketTestSession,
    **kwargs: Dict[str, Union[str, Response, dict, int]],
) -> None:
    chat_id = kwargs.get("chat_id")
    data = {"request": {"type": "GET_MESSAGES", "body": {"chat_id": chat_id}}}

    websocket.send_json(data=data)
    response = websocket.receive_json()
    assert response["response"]["type"] == "MESSAGES"
    assert response["response"]["body"]["chat_id"] == chat_id
    assert response["response"]["body"]["messages"] is None


@auth
def test_send_message(
    websocket: WebSocketTestSession,
    **kwargs: Dict[str, Union[str, Response, dict, int]],
) -> None:
    chat_id = kwargs.get("chat_id")
    data = {
        "request": {
            "type": "MESSAGE",
            "body": {
                "chat_id": chat_id,
                "message": f"test_message_{random.randint(100, 10000000)}",
            },
        }
    }

    websocket.send_json(data=data)
    response = websocket.receive_json()
    assert response["response"]["type"] == "MESSAGE"
    assert response["response"]["body"]["chat_id"] == chat_id
    assert response["response"]["body"]["chat_message"] is not None
