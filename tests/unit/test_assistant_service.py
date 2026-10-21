import pytest

from app.providers.fake import FakeLLMProvider
from app.providers.openrouter import LLMProviderError
from app.services.assistant_service import (
    SYSTEM_PROMPT,
    AssistantService,
)


@pytest.mark.asyncio
async def test_ask_returns_provider_answer() -> None:
    provider = FakeLLMProvider(answer="Hola desde el fake")
    service = AssistantService(provider)

    answer = await service.ask("¿Qué es FastAPI?")

    assert answer == "Hola desde el fake"


@pytest.mark.asyncio
async def test_ask_builds_system_and_user_messages() -> None:
    provider = FakeLLMProvider()
    service = AssistantService(provider)

    await service.ask("¿Qué es FastAPI?")

    messages = provider.calls[0]["messages"]

    assert messages[0] == {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
    assert messages[1] == {
        "role": "user",
        "content": "¿Qué es FastAPI?",
    }


@pytest.mark.asyncio
async def test_ask_passes_parameters_to_provider() -> None:
    provider = FakeLLMProvider()
    service = AssistantService(provider)

    await service.ask(
        "pregunta",
        temperature=0.9,
        top_p=0.5,
        max_tokens=50,
    )

    call = provider.calls[0]

    assert call["temperature"] == 0.9
    assert call["top_p"] == 0.5
    assert call["max_tokens"] == 50


@pytest.mark.asyncio
async def test_ask_propagates_provider_error() -> None:
    provider = FakeLLMProvider(
        error=LLMProviderError("fallo simulado")
    )
    service = AssistantService(provider)

    with pytest.raises(LLMProviderError):
        await service.ask("pregunta")