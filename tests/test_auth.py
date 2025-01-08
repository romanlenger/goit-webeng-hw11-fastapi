from unittest.mock import patch

import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from main import app
from src.auth.models import Role


@pytest.mark.asyncio
async def test_register_user(user_role: Role, override_get_db, faker, monkeypatch: pytest.MonkeyPatch):

    with patch.object("src.auth.services", "get_user_by_email") as mock_get_user_by_email:
        mock_get_user_by_email.return_value = None

        with patch.object("src.auth.services", "create_user") as mock_create_user:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                payload = {
                    "email": faker.email(),
                    "password": faker.password(),
                    "username": faker.name(),
                }
                response = await ac.post("/auth/register", json=payload)

                assert response.status_code == 201
                data = response.json()
                
                assert data["email"] == payload["email"]