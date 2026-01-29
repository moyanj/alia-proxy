import pytest
from httpx import AsyncClient, ASGITransport
from aiprox.main import app
from aiprox.config import settings
from tortoise import Tortoise
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
async def db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["aiprox.models"]},
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


@pytest.mark.asyncio
async def test_list_models_with_mapping():
    # Setup mapping in settings
    original_mapping = settings.mapping
    settings.mapping = {
        "gpt-4-custom": "openai/gpt-4o",
        "claude-custom": ["anthropic/claude-3-opus", "anthropic/claude-3-sonnet"],
    }

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/v1/models")

        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert isinstance(data["data"], list)

        # Check if mapped models are present
        model_ids = [m["id"] for m in data["data"]]
        assert "gpt-4-custom" in model_ids
        assert "claude-custom" in model_ids

        # Verify structure of mapped model
        mapped_model = next(m for m in data["data"] if m["id"] == "gpt-4-custom")
        assert mapped_model["owned_by"] == "system-mapping"
        assert mapped_model["root"] == "gpt-4-custom"

    finally:
        # Restore original mapping
        settings.mapping = original_mapping
