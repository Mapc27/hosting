from typing import Callable

from fastapi.testclient import TestClient
from requests import Response  # type: ignore

from auth.test_auth import auth_and_create_user
from main import app

client = TestClient(app)


def chat(func: Callable) -> Callable:
    def wrapper() -> None:
        user1_email, user1_password, headers1, response1 = auth_and_create_user()

        user2_email, user2_password, headers2, response2 = auth_and_create_user()
        user2_id = response2.json()["id"]

        response = client.post(
            "/chats",
            headers=headers1,
            json={"user_id": user2_id},
        )
        chat_id = response.json()["chat_id"]
        func(user2_id=user2_id, headers1=headers1, chat_id=chat_id, response=response)

        client.delete("/chats", headers=headers1, json={"chat_id": chat_id})
        client.delete("/user", headers=headers1)
        client.delete("/user", headers=headers2)

    return wrapper


@chat
def test_create_chat(
    user2_id: int, headers1: dict, chat_id: int, response: Response
) -> None:
    assert response.status_code == 200
    assert response.json()["unread_message_count"] == 0

    response = client.post(
        "/chats",
        headers=headers1,
        json={"user_id": user2_id},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Chat already exists"


@chat
def test_get_chat(
    user2_id: int, headers1: dict, chat_id: int, response: Response
) -> None:
    response = client.get(f"/chats/short/{chat_id}", headers=headers1)
    assert response.status_code == 200
    assert response.json()["companion"]["id"] == user2_id


def test_housing_attrs() -> None:
    response = client.post("/housing/attrs")
    assert response.status_code == 200
    assert response.json() == {"detail": "Success"}


def test_housing_fields() -> None:
    response = client.get("/housing/fields/")
    assert response.status_code == 200
    assert response.json() is not None
