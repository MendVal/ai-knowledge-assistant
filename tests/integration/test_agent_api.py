import json

import httpx
from fastapi.testclient import TestClient

from app.api.routes.agent import get_agent_service
from app.main import app
from app.services.agent_service import AgentService
from tests.unit.test_agent_tools import ScriptedProvider, tool_call


client = TestClient(app)


def use(provider):
    app.dependency_overrides[get_agent_service] = lambda: AgentService(provider)


def teardown_function():
    app.dependency_overrides.clear()


def test_agent_chat_200_con_tools_used():
    use(ScriptedProvider([
        {"content": None, "tool_calls": [
            tool_call("calculate_study_hours", {"hours_per_day": 2, "days": 5})
        ]},
        {"content": "Estudiarás un total de 10 horas."},
    ]))
    r = client.post("/api/v1/agent/chat", json={
        "question": "Si estudio 2 horas diarias durante 5 días, ¿cuántas horas?"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["tools_used"] == ["calculate_study_hours"]
    assert "10" in body["answer"]


def test_agent_chat_422_pregunta_corta():
    r = client.post("/api/v1/agent/chat", json={"question": "a"})
    assert r.status_code == 422


def test_agent_chat_422_max_steps_fuera_de_rango():
    r = client.post("/api/v1/agent/chat", json={
        "question": "hola mundo", "max_steps": 99
    })
    assert r.status_code == 422


def test_agent_chat_502_si_el_llm_no_responde():
    use(ScriptedProvider([{"content": ""}]))
    r = client.post("/api/v1/agent/chat", json={"question": "hola mundo"})
    assert r.status_code == 502


def test_agent_chat_estimate_learning_effort_de_punta_a_punta():
    prov = ScriptedProvider([
        {"content": None, "tool_calls": [tool_call(
            "estimate_learning_effort",
            {"difficulty": "intermedio", "topics": 5, "weekly_hours": 5},
        )]},
        {"content": "Necesitas 20 horas, es decir 4 semanas (esfuerzo medio)."},
    ])
    use(prov)
    r = client.post("/api/v1/agent/chat", json={
        "question": "Debo estudiar 5 temas de dificultad intermedia y tengo 5 horas por semana."
    })
    assert r.status_code == 200
    assert r.json()["tools_used"] == ["estimate_learning_effort"]
    # el resultado de la herramienta volvió al LLM como role="tool"
    ultimo = prov.calls[1][-1]
    assert ultimo["role"] == "tool" and '"weeks": 4' in ultimo["content"]
