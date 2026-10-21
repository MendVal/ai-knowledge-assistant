import httpx
import pytest

from app.providers import openrouter

REAL_CLIENT = httpx.AsyncClient


@pytest.fixture
def mock_openrouter(monkeypatch):
    """Simula el servidor de OpenRouter sin usar la red."""

    def install(handler):
        def factory(*args, **kwargs):
            if "transport" not in kwargs:
                kwargs["transport"] = httpx.MockTransport(
                    handler
                )
            return REAL_CLIENT(*args, **kwargs)

        monkeypatch.setattr(
            openrouter.httpx, "AsyncClient", factory
        )

    return install