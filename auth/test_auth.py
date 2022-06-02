import random
from typing import Any, Union, Tuple

from fastapi.testclient import TestClient
from requests import Response  # type: ignore

from main import app

client = TestClient(app)


def create_user(
    email: Union[None, str] = None, password: Union[None, str] = None
) -> Tuple[str, str, Response]:
    value: int = random.randint(10000000, 100000000)
    email = email if email else f"{value}@gmail.com"
    password = password if password else str(value)
    response = client.post("/user/create", json={"email": email, "password": password})
    return email, password, response


def login(email: str, password: str) -> Any:
    response = client.post(
        "/user/login", data={"username": email, "password": password}
    )
    return response.json()["access_token"]


def test_create_user() -> None:
    email, password, response = create_user()
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["email"] == email

    email, password, response = create_user(email=email, password=password)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["detail"] == "User already exists"


def test_login() -> None:
    email, password, _ = create_user()

    response = client.post(
        "/user/login", data={"username": email, "password": password}
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["token_type"] == "bearer"


def test_logout() -> None:
    email, password, _ = create_user()
    token = login(email, password)

    response = client.post("/user/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_profile() -> None:
    email, password, _ = create_user()
    token = login(email, password)

    response = client.get("/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email

    response = client.get(
        "/user/profile", headers={"Authorization": f"Bearer {token}123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

    response = client.get("/user/profile")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
