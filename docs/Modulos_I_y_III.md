# AI Knowledge Assistant — Módulos I y III

API educativa con FastAPI que se conecta a un LLM mediante OpenRouter.

## Endpoints
| Método | Ruta | Módulo | Qué hace |
|---|---|---|---|
| GET | `/health` | base | Estado del servicio |
| GET | `/api/v1/info` | base | Nombre, versión y `llm_enabled` (true: hay LLM integrado) |
| POST | `/api/v1/chat` | I | Pregunta → respuesta del LLM |
| POST | `/api/v1/agent/chat` | III | Pregunta → el LLM puede usar herramientas |

## Estructura
```
app/
├── main.py                  # arranca FastAPI y conecta routers
├── core/config.py           # lee el .env
├── api/routes/              # chat.py, agent.py, health.py, info.py
├── schemas/                 # chat.py, agent.py (Pydantic)
├── services/                # assistant_service.py, agent_service.py
├── providers/               # base.py (contratos), openrouter.py, fake.py
└── tools/                   # schemas.py, functions.py, registry.py
```
Flujo: **routes → schemas → services → providers → OpenRouter**. El agente agrega **tools** entre el service y el LLM.

## Módulo I — Chat con LLM
Body: `{"question": "¿Qué es FastAPI?", "temperature": 0.3, "top_p": 1.0, "max_tokens": 300}`
Respuesta: `{"answer": "...", "model": "..."}`. Errores: 422 (datos inválidos), 502 (falla del LLM).

## Módulo III — Agente con herramientas
Herramientas: `lookup_ai_concept`, `calculate_study_hours`, `estimate_learning_effort`, `create_study_task` (esta última requiere `confirm_actions: true`).
Campos extra: `confirm_actions` (bool) y `max_steps` (1–5). Respuesta agrega `tools_used`.

Flujo: el LLM **pide** una herramienta → `registry.py` valida los argumentos y la ejecuta → el resultado vuelve al LLM como `role: tool` → el LLM redacta la respuesta final.
Diagrama de secuencia: `docs/Modulo_III/secuencia.png`.

## Configuración
Copia `env.example` a `.env` y completa `OPENROUTER_API_KEY` (nunca subas `.env`).
```
pip install -e ".[dev]"
fastapi dev          # http://127.0.0.1:8000/docs
pytest -q
python scripts/run_labs.py mod3   # prueba real del agente (necesita API key y cuota)
```
