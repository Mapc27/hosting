import random
from typing import Any, Union, Tuple, Callable, Dict

from fastapi.testclient import TestClient
from requests import Response  # type: ignore

from main import app

client = TestClient(app)


def create_user(
    email: Union[None, str] = None, password: Union[None, str] = None
) -> Tuple[str, str, Response]:
    value: int = random.randint(10000000, 100000000)
    email = email if email else f"test_{value}@gmail.com"
    password = password if password else str(value)
    response = client.post("/user/create", json={"email": email, "password": password})
    return email, password, response


def login(email: str, password: str) -> Any:
    response = client.post(
        "/user/login", data={"username": email, "password": password}
    )
    return response.json()["access_token"]


def delete(headers: dict) -> None:
    client.delete("/user", headers=headers)


def auth_and_create_user() -> Tuple[str, str, dict, Response, str]:
    email, password, response = create_user()
    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}
    return email, password, headers, response, token


def auth(func: Callable) -> Callable:
    def wrapper() -> None:
        email, password, headers, response, token = auth_and_create_user()
        kwargs = {
            "email": email,
            "password": password,
            "headers": headers,
            "response": response,
            "token": token,
        }
        func(**kwargs)
        delete(headers=headers)

    return wrapper


def test_create_user() -> None:
    email, password, response = create_user()
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["email"] == email

    email, password, response = create_user(email=email, password=password)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["detail"] == "User already exists"

    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}
    delete(headers=headers)


def test_login() -> None:
    email, password, _ = create_user()

    response = client.post(
        "/user/login", data={"username": email, "password": password}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["token_type"] == "bearer"

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    delete(headers=headers)


@auth
def test_logout(**kwargs: Dict[str, Union[str, Response, dict]]) -> None:
    headers = kwargs.get("headers")
    email = kwargs.get("email")

    response = client.post("/user/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email


@auth
def test_profile(**kwargs: Dict[str, Union[str, Response, dict]]) -> None:
    email = kwargs.get("email")
    headers = kwargs.get("headers")

    response = client.get("/user/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email

    response = client.get("/user/profile")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_change_profile() -> None:
    email, password, _ = create_user()
    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    new_email = f"{random.randint(10, 100)}@gmail.com"
    response = client.post(
        "/user/change_profile", headers=headers, json={"email": new_email}
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Success"

    token = login(new_email, password)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/user/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == new_email

    delete(headers=headers)


@auth
def test_create_image(**kwargs: Dict[str, Union[str, Response, dict]]) -> None:
    headers = kwargs.get("headers")

    with open("test/test_image.jpg", "rb") as file:
        form = {"image": file}
        response = client.post("/user/image", files=form, headers=headers)

    assert response.status_code == 200
    assert response.json()["image"] is not None

    response = client.delete("/user/image", headers=headers)

    assert response.status_code == 200
    assert response.json()["image"] is None


@auth
def test_get_user(**kwargs: Dict[str, Union[str, Response, dict]]) -> None:
    response: Response = kwargs.get("response")
    headers = kwargs.get("headers")

    user_id = response.json()["id"]
    response = client.get(f"/user/{user_id}", headers=headers)
    assert response.json()["email"] is not None
