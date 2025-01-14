from unittest.mock import patch

import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient, ASGITransport

from main import app
from src.auth.models import Role


@pytest.mark.asyncio
async def test_register_user(user_role: Role, override_get_db, faker):
    with patch.object(BackgroundTasks, "add_task"):
         async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "email": faker.email(),
                    "password": faker.password(),
                "username": faker.name(),
            }
                
            response = await ac.post(
                "/auth/register", json=payload
            )

            assert response.status_code == 200
            data = response.json()

            assert data["email"] == payload["email"]