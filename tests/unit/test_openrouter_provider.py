import httpx
import pytest

from app.providers.openrouter import (
    LLMProviderError,
    OpenRouterProvider,
)

MESSAGES = [{"role": "user", "content": "hola"}]


def make_provider(api_key: str = "clave-de-prueba"):
    return OpenRouterProvider(
        api_key=api_key,
        model="modelo-de-prueba",
        base_url="https://openrouter.ai/api/v1",
    )


@pytest.mark.asyncio
async def test_generate_returns_content(mock_openrouter) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "respuesta"}}
                ]
            },
        )

    mock_openrouter(handler)

    result = await make_provider().generate(MESSAGES)

    assert result == "respuesta"


@pytest.mark.asyncio
async def test_generate_without_api_key() -> None:
    with pytest.raises(LLMProviderError):
        await make_provider(api_key="").generate(MESSAGES)


@pytest.mark.asyncio
async def test_generate_timeout(mock_openrouter) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("simulado")

    mock_openrouter(handler)

    with pytest.raises(LLMProviderError) as error:
        await make_provider().generate(MESSAGES)

    assert "Tiempo de espera" in str(error.value)


@pytest.mark.asyncio
async def test_generate_http_429(mock_openrouter) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "limite"})

    mock_openrouter(handler)

    with pytest.raises(LLMProviderError) as error:
        await make_provider().generate(MESSAGES)

    assert "429" in str(error.value)


@pytest.mark.asyncio
async def test_generate_response_without_choices(
    mock_openrouter,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "sin-choices"})

    mock_openrouter(handler)

    with pytest.raises(LLMProviderError) as error:
        await make_provider().generate(MESSAGES)

    assert "inválido" in str(error.value)

async def test_complete_with_tools_envia_tools_y_devuelve_mensaje(mock_openrouter):
    import json

    import httpx

    from app.providers.openrouter import OpenRouterProvider

    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["payload"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {
            "content": None,
            "tool_calls": [{"id": "c1", "type": "function",
                            "function": {"name": "x", "arguments": "{}"}}],
        }}]})

    mock_openrouter(handler)
    provider = OpenRouterProvider("k", "m", "https://example.test/api/v1")
    msg = await provider.complete_with_tools(
        messages=[{"role": "user", "content": "hola"}],
        tools=[{"type": "function", "function": {"name": "x"}}],
    )

    assert seen["payload"]["tool_choice"] == "auto"
    assert seen["payload"]["tools"][0]["function"]["name"] == "x"
    assert msg["tool_calls"][0]["id"] == "c1"


async def test_generate_conserva_su_contrato_con_el_refactor(mock_openrouter):
    import httpx

    from app.providers.openrouter import OpenRouterProvider

    mock_openrouter(lambda request: httpx.Response(
        200, json={"choices": [{"message": {"content": "respuesta del modelo"}}]}
    ))
    provider = OpenRouterProvider("k", "m", "https://example.test/api/v1")
    answer = await provider.generate([{"role": "user", "content": "Hola"}])
    assert answer == "respuesta del modelo"
