import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.chat import get_assistant_service
from app.main import app
from app.providers.fake import FakeLLMProvider
from app.providers.openrouter import (
    LLMProviderError,
    OpenRouterProvider,
)
from app.services.assistant_service import AssistantService


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def use_provider(provider) -> None:
    app.dependency_overrides[get_assistant_service] = (
        lambda: AssistantService(provider)
    )


def make_client() -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


@pytest.mark.asyncio
async def test_health() -> None:
    async with make_client() as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_info() -> None:
    async with make_client() as client:
        response = await client.get("/api/v1/info")

    assert response.status_code == 200
    assert response.json()["llm_enabled"] is False


@pytest.mark.asyncio
async def test_chat_ok() -> None:
    provider = FakeLLMProvider(answer="Respuesta simulada")
    use_provider(provider)

    async with make_client() as client:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "Explícame Pydantic"},
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Respuesta simulada"
    assert "model" in response.json()


@pytest.mark.asyncio
async def test_chat_rejects_short_question() -> None:
    provider = FakeLLMProvider()
    use_provider(provider)

    async with make_client() as client:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "a"},
        )

    assert response.status_code == 422
    assert provider.calls == []


@pytest.mark.asyncio
async def test_chat_rejects_negative_temperature() -> None:
    provider = FakeLLMProvider()
    use_provider(provider)

    async with make_client() as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "question": "Explícame Pydantic",
                "temperature": -1,
            },
        )

    assert response.status_code == 422
    assert provider.calls == []


@pytest.mark.asyncio
async def test_chat_returns_502_on_provider_error() -> None:
    use_provider(
        FakeLLMProvider(
            error=LLMProviderError("OpenRouter respondió HTTP 429")
        )
    )

    async with make_client() as client:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "Explícame Pydantic"},
        )

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_502_does_not_leak_api_key(mock_openrouter) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429, json={"error": "cuerpo-sensible-del-proveedor"}
        )

    mock_openrouter(handler)

    use_provider(
        OpenRouterProvider(
            api_key="CLAVE-SECRETA-123",
            model="modelo-de-prueba",
            base_url="https://openrouter.ai/api/v1",
        )
    )

    async with make_client() as client:
        response = await client.post(
            "/api/v1/chat",
            json={"question": "Explícame Pydantic"},
        )

    assert response.status_code == 502
    assert "CLAVE-SECRETA-123" not in response.text
    assert "cuerpo-sensible-del-proveedor" not in response.text