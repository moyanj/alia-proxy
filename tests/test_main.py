import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tortoise import Tortoise
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
async def db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"app": "AI Proxy Service"}


@pytest.mark.asyncio
async def test_list_models():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_chat_completions_no_model():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/v1/chat/completions", json={"messages": []})
    assert response.status_code == 400
    assert "Missing 'model' field" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_chat_completions_invalid_format():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/v1/chat/completions", json={"model": "invalid-format"}
        )
    assert response.status_code == 400
    assert "Invalid model field format" in response.json()["error"]["message"]
