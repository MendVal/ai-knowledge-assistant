"""Pruebas del registro de herramientas (adaptadas del repo del profe)."""
import json

from app.tools.registry import execute_tool, tool_definitions


def test_tools_exposed():
    names = {t["function"]["name"] for t in tool_definitions()}
    assert names == {
        "lookup_ai_concept",
        "calculate_study_hours",
        "estimate_learning_effort",
        "create_study_task",
    }


def test_calculation_con_decimales():
    result = execute_tool(
        "calculate_study_hours",
        json.dumps({"hours_per_day": 1.5, "days": 4}),
        False,
    )
    assert result["data"]["total_hours"] == 6


def test_invalid_args_fuera_de_rango_y_json_malo():
    fuera = execute_tool(
        "calculate_study_hours",
        json.dumps({"hours_per_day": 50, "days": 2}),
        False,
    )
    assert fuera["error"] == "invalid_arguments"

    json_malo = execute_tool("calculate_study_hours", "not-json", False)
    assert json_malo["error"] == "invalid_arguments"


def test_unknown_tool_no_ejecuta_nada():
    result = execute_tool("run_shell", "{}", True)
    assert result["error"] == "unknown_tool"


def test_lookup_ai_concept_conocido_y_desconocido():
    ok = execute_tool("lookup_ai_concept", json.dumps({"concept": "RAG"}), False)
    assert ok["data"]["found"] is True

    no = execute_tool("lookup_ai_concept", json.dumps({"concept": "xyz123"}), False)
    assert no["ok"] is True and no["data"]["found"] is False
