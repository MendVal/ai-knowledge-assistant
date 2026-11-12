import json

import pytest

from app.services.agent_service import AgentExecutionError, AgentService
from app.tools.registry import execute_tool, tool_definitions


class ScriptedProvider:
    """LLM falso: devuelve respuestas predefinidas en orden."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def complete_with_tools(self, messages, tools, **kwargs):
        self.calls.append([dict(m) for m in messages])
        return self.responses.pop(0)


def tool_call(name, args, call_id="call_1"):
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)},
    }


def test_catalogo_tiene_tres_herramientas():
    names = [t["function"]["name"] for t in tool_definitions()]
    assert names == [
        "lookup_ai_concept",
        "calculate_study_hours",
        "estimate_learning_effort",
        "create_study_task",
    ]


def test_calcular_horas():
    r = execute_tool(
        "calculate_study_hours",
        '{"hours_per_day": 2, "days": 5}',
        confirm_actions=False,
    )
    assert r == {"ok": True, "data": {"total_hours": 10.0}}


def test_herramienta_desconocida():
    r = execute_tool("borrar_todo", "{}", confirm_actions=True)
    assert r == {"ok": False, "error": "unknown_tool"}


def test_argumentos_invalidos():
    r = execute_tool(
        "calculate_study_hours",
        '{"hours_per_day": 99, "days": 5}',
        confirm_actions=False,
    )
    assert r == {"ok": False, "error": "invalid_arguments"}


def test_argumento_extra_se_rechaza():
    r = execute_tool(
        "calculate_study_hours",
        '{"hours_per_day": 2, "days": 5, "extra": 1}',
        confirm_actions=False,
    )
    assert r["error"] == "invalid_arguments"


def test_escritura_requiere_confirmacion():
    args = '{"title": "Repasar FastAPI", "estimated_hours": 2}'
    assert execute_tool("create_study_task", args, False) == {
        "ok": False,
        "error": "confirmation_required",
    }
    assert execute_tool("create_study_task", args, True)["ok"] is True


async def test_agente_usa_herramienta_y_responde():
    provider = ScriptedProvider([
        {
            "content": None,
            "tool_calls": [
                tool_call("calculate_study_hours", {"hours_per_day": 2, "days": 5})
            ],
        },
        {"content": "Estudiarás 10 horas."},
    ])
    result = await AgentService(provider).ask("¿Cuántas horas?")

    assert result.answer == "Estudiarás 10 horas."
    assert result.tools_used == ["calculate_study_hours"]
    # 2ª llamada al LLM incluye el resultado como role="tool"
    assert provider.calls[1][-1]["role"] == "tool"
    assert '"total_hours": 10.0' in provider.calls[1][-1]["content"]


async def test_agente_sin_herramientas():
    provider = ScriptedProvider([{"content": "Hola"}])
    result = await AgentService(provider).ask("Hola")
    assert result.tools_used == []


async def test_limite_de_rondas():
    loop = {
        "content": None,
        "tool_calls": [
            tool_call("calculate_study_hours", {"hours_per_day": 1, "days": 1})
        ],
    }
    provider = ScriptedProvider([loop, loop])
    with pytest.raises(AgentExecutionError, match="Límite"):
        await AgentService(provider).ask("x", max_steps=2)
