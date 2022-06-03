import random
from typing import Callable, Dict, Union

from fastapi.testclient import TestClient
from requests import Response  # type: ignore

from auth.test_auth import auth_and_create_user, auth
from main import app

client = TestClient(app)


def chat(func: Callable) -> Callable:
    def wrapper() -> None:
        (
            user1_email,
            user1_password,
            headers1,
            response1,
            token1,
        ) = auth_and_create_user()
        (
            user2_email,
            user2_password,
            headers2,
            response2,
            token2,
        ) = auth_and_create_user()
        user2_id = response2.json()["id"]

        response = client.post(
            "/chats",
            headers=headers1,
            json={"user_id": user2_id},
        )
        chat_id = response.json()["chat_id"]

        kwargs = {
            "user1_email": user1_email,
            "user1_password": user1_password,
            "headers1": headers1,
            "response1": response1,
            "token1": token1,
            "user2_email": user2_email,
            "user2_password": user2_password,
            "headers2": headers2,
            "response2": response2,
            "token2": token2,
            "user2_id": user2_id,
            "chat_id": chat_id,
            "response": response,
        }

        func(**kwargs)

        client.delete("/chats", headers=headers1, json={"chat_id": chat_id})
        client.delete("/user", headers=headers1)
        client.delete("/user", headers=headers2)

    return wrapper


@chat
def test_create_chat(**kwargs: Dict[str, Union[str, Response, Dict, int]]) -> None:
    response: Response = kwargs.get("response")
    headers1 = kwargs.get("headers1")
    user2_id = kwargs.get("user2_id")

    if not response:
        raise AssertionError

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
def test_get_chat(**kwargs: dict) -> None:
    chat_id = kwargs.get("chat_id")
    headers1 = kwargs.get("headers1")
    user2_id = kwargs.get("user2_id")

    response = client.get(f"/chats/short/{chat_id}", headers=headers1)
    assert response.status_code == 200
    assert response.json()["companion"]["id"] == user2_id


def test_housing_attrs() -> None:
    response = client.post("/housing/attrs")
    assert response.status_code == 200
    assert response.json() in (
        {"detail": "Success"},
        {"detail": "Attrs already exists"},
    )


def test_housing_fields() -> None:
    response = client.get("/housing/fields/")
    assert response.status_code == 200
    assert response.json() is not None


def housing(func: Callable) -> Callable:
    @auth
    def wrapper(**kwargs: Dict[str, Union[str, Response, Dict, int]]) -> None:
        headers = kwargs.get("headers")
        fields = client.get("/housing/fields/", headers=headers).json()

        request_data = {
            "name": f"test_{random.randint(10, 1000)}",
            "address": f"test_{random.randint(10, 1000)}",
            "description": f"test_{random.randint(10, 1000)}",
            "type_id": random.choice(fields["housing_types"])["id"],
            "category_id": random.choice(fields["housing_categories"])["id"],
            "per_night": random.randint(10, 10000),
            "characteristics": [],
        }
        for characteristic_type in fields["characteristic_types"]:
            request_data["characteristics"].append(
                {
                    "characteristic_id": characteristic_type["id"],
                    "amount": random.randint(0, 30),
                }
            )

        response = client.post("/housing", headers=headers, json=request_data)
        housing_id = response.json()
        assert isinstance(response.json(), int)

        func(housing_id, **kwargs)

        response = client.delete(f"/housing/{housing_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == housing_id

    return wrapper


@housing
def test_edit_housing(
    housing_id: int, **kwargs: Dict[str, Union[str, Response, Dict, int]]
) -> None:
    headers = kwargs.get("headers")
    name = f"test_{random.randint(10, 1000)}"

    response = client.put(
        f"/housing/{housing_id}", headers=headers, json={"name": name}
    )
    assert response.status_code == 200
    assert response.json()["name"] == name


@housing
def test_housing_image(
    housing_id: int, **kwargs: Dict[str, Union[str, Response, Dict, int]]
) -> None:
    headers = kwargs.get("headers")

    with open("test/test_image.jpg", "rb") as file:
        form = {"image": file}
        response = client.post(
            "/housing/image/",
            files=form,
            headers=headers,
            data={"housing_id": housing_id},
        )

    image_id = response.json()["id"]
    assert response.status_code == 200
    assert response.json()["housing_id"] == housing_id
    assert response.json()["file_name"] is not None

    response = client.put(
        "/housing/image/set_main",
        headers=headers,
        data={"housing_id": housing_id, "image_id": image_id},
    )
    assert response.status_code == 200
    assert response.json()["housing_id"] == housing_id
    assert response.json()["file_name"] is not None
    assert response.json()["id"] == image_id

    wishlist(housing_id, **kwargs)

    response = client.delete(
        "/housing/image/",
        headers=headers,
        data={"housing_id": housing_id, "image_id": image_id},
    )

    assert response.status_code == 200
    assert response.json()["housing_id"] == housing_id
    assert response.json()["file_name"] is not None


def wishlist(
    housing_id: int, **kwargs: Dict[str, Union[str, Response, Dict, int]]
) -> None:
    headers = kwargs.get("headers")

    response = client.post(
        "/user/wishlist",
        headers=headers,
        json={"housing_id": housing_id},
    )
    assert response.status_code == 200
    assert response.json()["housing_id"] == housing_id

    response = client.get(
        "/user/wishlist",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["wishlist"][0]["housing_id"] == housing_id

    liked_housing_id = response.json()["wishlist"][0]["id"]

    response = client.get(
        f"/user/wish/{liked_housing_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["wish"]["housing_id"] == housing_id

    response = client.delete(
        "/user/wishlist", headers=headers, json={"housing_id": housing_id}
    )

    assert response.status_code == 200
    assert response.json()["wish"]["housing_id"] == housing_id
