import math
from uuid import uuid4

from app.tools.schemas import ConceptArgs, EffortArgs, HoursArgs, TaskArgs


CONCEPTS = {
    "rag": (
        "RAG combina recuperación de información "
        "con generación de texto."
    ),
    "embedding": (
        "Un embedding representa información "
        "mediante un vector numérico."
    ),
    "function calling": (
        "Function Calling permite al modelo "
        "solicitar la ejecución de funciones externas."
    ),
    "fastapi": (
        "FastAPI es un framework de Python "
        "para construir APIs con tipado y validación."
    ),
}

# Almacenamiento temporal para el laboratorio.
# Se pierde al reiniciar el proceso.
TASKS: list[dict] = []


def lookup_ai_concept(args: ConceptArgs) -> dict:
    key = args.concept.strip().lower()
    definition = CONCEPTS.get(key)
    return {
        "found": definition is not None,
        "concept": key,
        "definition": definition,
    }


def calculate_study_hours(args: HoursArgs) -> dict:
    total = args.hours_per_day * args.days
    return {"total_hours": round(total, 2)}


def create_study_task(args: TaskArgs) -> dict:
    item = {
        "id": str(uuid4()),
        "title": args.title,
        "estimated_hours": args.estimated_hours,
    }
    TASKS.append(item)
    return {"created": True, "task": item}


# Horas estimadas por tema según la dificultad (tabla del laboratorio).
HOURS_PER_TOPIC = {"basico": 2, "intermedio": 4, "avanzado": 6}

# SUPUESTO: el enunciado no trae los umbrales del nivel de esfuerzo.
# Ajusta estos valores si el profesor define otros.
EFFORT_LEVELS = [(10, "bajo"), (30, "medio")]  # <=10 h bajo, <=30 h medio
EFFORT_MAX = "alto"


def estimate_learning_effort(args: EffortArgs) -> dict:
    """Pura: no depende de OpenRouter, FastAPI ni de la red."""
    per_topic = HOURS_PER_TOPIC[args.difficulty]
    total = args.topics * per_topic
    weeks = math.ceil(round(total / args.weekly_hours, 6))

    level = EFFORT_MAX
    for limit, name in EFFORT_LEVELS:
        if total <= limit:
            level = name
            break

    return {
        "total_hours": total,
        "weeks": weeks,
        "effort_level": level,
        "explanation": (
            f"{args.topics} temas x {per_topic} h por tema "
            f"({args.difficulty}) = {total} h. "
            f"{total} h / {args.weekly_hours:g} h por semana = "
            f"{total / args.weekly_hours:.2f} -> {weeks} semana(s). "
            f"Esfuerzo {level}."
        ),
    }
