import pytest
from pydantic import ValidationError

from app.tools.functions import estimate_learning_effort
from app.tools.registry import execute_tool, tool_definitions
from app.tools.schemas import EffortArgs


def run(difficulty, topics, weekly_hours):
    return estimate_learning_effort(
        EffortArgs(difficulty=difficulty, topics=topics, weekly_hours=weekly_hours)
    )


# ---------- función pura ----------
def test_caso_del_enunciado():
    r = run("intermedio", 5, 5)
    assert r["total_hours"] == 20
    assert r["weeks"] == 4
    assert r["effort_level"] == "medio"
    assert "5 temas x 4 h" in r["explanation"]


@pytest.mark.parametrize("difficulty,horas", [("basico", 2), ("intermedio", 4), ("avanzado", 6)])
def test_horas_por_dificultad(difficulty, horas):
    assert run(difficulty, 1, 40)["total_hours"] == horas


def test_semanas_se_redondean_hacia_arriba():
    assert run("basico", 1, 5)["weeks"] == 1       # 0.4 -> 1
    assert run("intermedio", 5, 6)["weeks"] == 4   # 3.33 -> 4


@pytest.mark.parametrize("topics,difficulty,nivel", [
    (5, "basico", "bajo"),        # 10 h  (límite superior de bajo)
    (3, "intermedio", "medio"),   # 12 h
    (5, "avanzado", "medio"),     # 30 h  (límite superior de medio)
    (6, "avanzado", "alto"),      # 36 h
])
def test_niveles_de_esfuerzo(topics, difficulty, nivel):
    assert run(difficulty, topics, 10)["effort_level"] == nivel


# ---------- contrato Pydantic: válidos y valores límite ----------
@pytest.mark.parametrize("topics", [1, 20])
def test_topics_limites_validos(topics):
    EffortArgs(difficulty="basico", topics=topics, weekly_hours=5)


@pytest.mark.parametrize("weekly", [0.5, 40])
def test_weekly_hours_limites_validos(weekly):
    EffortArgs(difficulty="basico", topics=1, weekly_hours=weekly)


def test_dificultad_con_tilde_y_mayusculas():
    assert EffortArgs(difficulty=" Básico ", topics=1, weekly_hours=5).difficulty == "basico"


# ---------- inválidos ----------
@pytest.mark.parametrize("datos", [
    {"difficulty": "facil", "topics": 5, "weekly_hours": 5},        # dificultad desconocida
    {"difficulty": "basico", "topics": 0, "weekly_hours": 5},       # topics bajo el mínimo
    {"difficulty": "basico", "topics": 21, "weekly_hours": 5},      # topics sobre el máximo
    {"difficulty": "basico", "topics": 2.5, "weekly_hours": 5},     # topics no entero
    {"difficulty": "basico", "topics": 5, "weekly_hours": 0},       # horas = 0
    {"difficulty": "basico", "topics": 5, "weekly_hours": -1},      # horas negativas
    {"difficulty": "basico", "topics": 5, "weekly_hours": 40.1},    # sobre el máximo
    {"difficulty": "basico", "topics": 5},                          # falta un campo
    {"difficulty": "basico", "topics": 5, "weekly_hours": 5, "x": 1},  # campo extra
])
def test_argumentos_invalidos(datos):
    with pytest.raises(ValidationError):
        EffortArgs(**datos)


# ---------- registro y ejecución por el registry ----------
def test_esta_registrada_y_describe_sus_parametros():
    tool = next(t for t in tool_definitions()
                if t["function"]["name"] == "estimate_learning_effort")
    assert "dificultad" in tool["function"]["description"]
    props = tool["function"]["parameters"]["properties"]
    assert set(props) == {"difficulty", "topics", "weekly_hours"}
    assert props["difficulty"]["enum"] == ["basico", "intermedio", "avanzado"]


def test_registry_ejecuta_y_valida():
    ok = execute_tool("estimate_learning_effort",
                      '{"difficulty":"intermedio","topics":5,"weekly_hours":5}', False)
    assert ok["ok"] is True and ok["data"]["weeks"] == 4

    mal = execute_tool("estimate_learning_effort",
                       '{"difficulty":"intermedio","topics":0,"weekly_hours":5}', False)
    assert mal == {"ok": False, "error": "invalid_arguments"}
