import json
from typing import Any

from pydantic import ValidationError

from app.tools.functions import (
    calculate_study_hours,
    create_study_task,
    estimate_learning_effort,
    lookup_ai_concept,
)
from app.tools.schemas import ConceptArgs, EffortArgs, HoursArgs, TaskArgs


# nombre -> (schema de argumentos, función, ¿escribe datos?, descripción)
REGISTRY = {
    "lookup_ai_concept": (
        ConceptArgs,
        lookup_ai_concept,
        False,
        "Consulta la definición de un concepto educativo de IA.",
    ),
    "calculate_study_hours": (
        HoursArgs,
        calculate_study_hours,
        False,
        "Calcula las horas totales de estudio.",
    ),
    "estimate_learning_effort": (
        EffortArgs,
        estimate_learning_effort,
        False,
        (
            "Estima el esfuerzo para completar una actividad formativa. "
            "Recibe la dificultad (basico, intermedio o avanzado), la cantidad "
            "de temas y las horas de estudio disponibles por semana. "
            "Devuelve horas totales, semanas necesarias, nivel de esfuerzo "
            "(bajo, medio o alto) y una explicación del cálculo."
        ),
    ),
    "create_study_task": (
        TaskArgs,
        create_study_task,
        True,
        "Crea una tarea de estudio. Requiere confirmación explícita.",
    ),
}


def tool_definitions() -> list[dict[str, Any]]:
    """Catálogo que se le envía al LLM (formato OpenAI/OpenRouter)."""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": model.model_json_schema(),
            },
        }
        for name, (model, _func, _write, description) in REGISTRY.items()
    ]


def execute_tool(
    name: str,
    raw_arguments: str,
    confirm_actions: bool,
) -> dict[str, Any]:
    """Valida y ejecuta la herramienta que pidió el LLM."""
    entry = REGISTRY.get(name)

    if entry is None:
        return {"ok": False, "error": "unknown_tool"}

    model, function, is_write, _description = entry

    if is_write and not confirm_actions:
        return {"ok": False, "error": "confirmation_required"}

    try:
        parsed = json.loads(raw_arguments)
        args = model.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError, ValueError):
        return {"ok": False, "error": "invalid_arguments"}

    return {"ok": True, "data": function(args)}
