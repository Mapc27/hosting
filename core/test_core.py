from fastapi.testclient import TestClient
from auth.test_auth import create_user, login
from main import app


client = TestClient(app)


def test_create_chat() -> None:
    user1_email, user1_password, _ = create_user()
    token = login(user1_email, user1_password)

    user2_email, user2_password, response = create_user()
    user2_id = response.json()["id"]

    response = client.post(
        "/chats",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user2_id},
    )
    assert response.status_code == 200
    assert response.json()["unread_message_count"] == 0

    response = client.post(
        "/chats",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user2_id},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Chat already exists"
