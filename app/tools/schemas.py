import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictArgs(BaseModel):
    """Rechaza argumentos que no estén definidos."""

    model_config = ConfigDict(extra="forbid")


class ConceptArgs(StrictArgs):
    concept: str = Field(min_length=2, max_length=80)


class HoursArgs(StrictArgs):
    hours_per_day: float = Field(gt=0, le=12)
    days: int = Field(ge=1, le=31)


class TaskArgs(StrictArgs):
    title: str = Field(min_length=3, max_length=120)
    estimated_hours: float = Field(gt=0, le=40)


class EffortArgs(StrictArgs):
    """Argumentos de estimate_learning_effort."""

    difficulty: Literal["basico", "intermedio", "avanzado"]
    topics: int = Field(ge=1, le=20)
    weekly_hours: float = Field(gt=0, le=40)

    @field_validator("difficulty", mode="before")
    @classmethod
    def normalizar_dificultad(cls, value):
        # Acepta "Básico", " INTERMEDIO ", etc.
        if isinstance(value, str):
            texto = unicodedata.normalize("NFD", value.strip().lower())
            return "".join(c for c in texto if unicodedata.category(c) != "Mn")
        return value
