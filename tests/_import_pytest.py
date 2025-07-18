import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.auth import router as auth_router
from fastapi import FastAPI

# src/api/test_auth.py


app = FastAPI()
app.include_router(auth_router)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_update_password_success(monkeypatch, client):
    # Arrange
    fake_token = "validtoken"
    fake_email = "user@example.com"
    fake_password = "newpassword"
    fake_hashed = "hashedpassword"
    fake_user = MagicMock()
    fake_user.email = fake_email
    fake_user.username = "testuser"

    async def fake_get_email_from_token(token):
        assert token == fake_token
        return fake_email

    class FakeUserService:
        def __init__(self, db): pass
        async def get_user_by_email(self, email):
            assert email == fake_email
            return fake_user
        async def update_password(self, email, hashed_password):
            assert email == fake_email
            assert hashed_password == fake_hashed
            fake_user.username = "testuser"
            return fake_user

    class FakeHash:
        def get_password_hash(self, password):
            assert password == fake_password
            return fake_hashed

    monkeypatch.setattr("src.api.auth.get_email_from_token", fake_get_email_from_token)
    monkeypatch.setattr("src.api.auth.UserService", FakeUserService)
    monkeypatch.setattr("src.api.auth.Hash", FakeHash)
    monkeypatch.setattr("src.api.auth.get_db", lambda: None)

    # Act
    response = client.post(
        f"/auth/reset_password/{fake_token}",
        data={"password": fake_password}
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Пароль для користувача testuser змінено"}

@pytest.mark.asyncio
async def test_update_password_user_not_found(monkeypatch, client):
    fake_token = "validtoken"
    fake_email = "user@example.com"
    fake_password = "newpassword"

    async def fake_get_email_from_token(token):
        return fake_email

    class FakeUserService:
        def __init__(self, db): pass
        async def get_user_by_email(self, email):
            return None

    monkeypatch.setattr("src.api.auth.get_email_from_token", fake_get_email_from_token)
    monkeypatch.setattr("src.api.auth.UserService", FakeUserService)
    monkeypatch.setattr("src.api.auth.Hash", lambda: None)
    monkeypatch.setattr("src.api.auth.get_db", lambda: None)

    response = client.post(
        f"/auth/reset_password/{fake_token}",
        data={"password": fake_password}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User verification error"

@pytest.mark.asyncio
async def test_update_password_invalid_token(monkeypatch, client):
    fake_token = "invalidtoken"
    fake_password = "newpassword"

    async def fake_get_email_from_token(token):
        raise Exception("Invalid token")

    monkeypatch.setattr("src.api.auth.get_email_from_token", fake_get_email_from_token)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: None)
    monkeypatch.setattr("src.api.auth.Hash", lambda: None)
    monkeypatch.setattr("src.api.auth.get_db", lambda: None)

    response = client.post(
        f"/auth/reset_password/{fake_token}",
        data={"password": fake_password}
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR or response.status_code == 422