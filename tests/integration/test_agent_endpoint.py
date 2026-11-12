"""Endpoint del agente sin herramientas y validación (adaptado del repo del profe)."""
from fastapi.testclient import TestClient

from app.api.routes.agent import get_agent_service
from app.main import app
from app.services.agent_service import AgentService

client = TestClient(app)


class FakeProvider:
    async def complete_with_tools(self, messages, tools, **kwargs):
        return {"content": "Respuesta educativa"}


def teardown_function():
    app.dependency_overrides.clear()


def test_agent_endpoint_sin_herramientas():
    app.dependency_overrides[get_agent_service] = lambda: AgentService(FakeProvider())
    r = client.post("/api/v1/agent/chat", json={"question": "¿Qué es RAG?"})
    assert r.status_code == 200
    assert r.json()["answer"] == "Respuesta educativa"
    assert r.json()["tools_used"] == []


def test_agent_rejects_invalid():
    r = client.post("/api/v1/agent/chat", json={"question": "x", "max_steps": 6})
    assert r.status_code == 422


def test_agent_chat_y_agent_conviven_con_el_chat_original():
    # El Módulo I no se rompió: /health sigue vivo y /chat valida igual
    assert client.get("/health").status_code == 200
    assert client.post("/api/v1/chat", json={"question": "x"}).status_code == 422
