# AI Knowledge Assistant

API asíncrona construida con **FastAPI** que recibe una pregunta y responde con un **LLM real** (a través de OpenRouter). En el Módulo III el asistente además puede **usar herramientas** (tool calling) para calcular, consultar y crear tareas de estudio.

El proyecto evoluciona por módulos:

| Módulo | Qué se construyó |
|--------|------------------|
| **0 – Bootstrap** | API base con FastAPI, validación con Pydantic, capas, AsyncIO/HTTPX, pruebas y flujo de Git. Asistente local sin LLM. |
| **I – Integración con LLM** | Proveedor OpenRouter, configuración con `.env`, parámetros de generación, manejo de errores (502) y laboratorio de experimentación. |
| **III – Tool calling** | Agente que decide qué herramienta usar, un registro de herramientas con validación, confirmación para acciones de escritura y la herramienta `estimate_learning_effort`. |

---

## Tabla de contenido

1. [Tecnologías](#tecnologías)
2. [Endpoints](#endpoints)
3. [Arquitectura y flujo](#arquitectura-y-flujo)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Instalación y configuración](#instalación-y-configuración)
6. [Ejecución](#ejecución)
7. [Pruebas](#pruebas)
8. [Laboratorios y documentación](#laboratorios-y-documentación)
9. [Scripts](#scripts)
10. [Flujo de trabajo con Git](#flujo-de-trabajo-con-git)
11. [Límites conocidos](#límites-conocidos)

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3.12+ | Lenguaje base |
| FastAPI | Framework para construir la API |
| Pydantic | Validación y serialización de datos (también de los argumentos de las herramientas) |
| AsyncIO / HTTPX | Programación asíncrona y cliente HTTP hacia OpenRouter |
| OpenRouter | Acceso al LLM (modelo configurable) |
| python-dotenv | Lee la configuración desde `.env` |
| pytest + pytest-asyncio | Pruebas unitarias y de integración |
| Git / GitHub | Control de versiones y Pull Requests |

---

## Endpoints

| Método | Ruta | Módulo | Descripción | Respuestas |
|--------|------|--------|-------------|------------|
| `GET` | `/health` | 0 | Estado del servicio | `200` |
| `GET` | `/api/v1/info` | 0 | Información básica (`llm_enabled = true`) | `200` |
| `POST` | `/api/v1/chat` | I | Pregunta → respuesta del LLM | `200`, `422`, `502` |
| `POST` | `/api/v1/agent/chat` | III | Pregunta → el LLM puede usar herramientas | `200`, `422`, `502` |
| `GET` | `/docs` | 0 | Documentación interactiva (Swagger UI) | `200` |

### `POST /api/v1/chat`

Request (solo `question` es obligatorio):

```json
{
  "question": "¿Qué es FastAPI?",
  "temperature": 0.3,
  "top_p": 1.0,
  "max_tokens": 300
}
```

| Campo | Regla | Por defecto |
|-------|-------|-------------|
| `question` | 3 a 2000 caracteres (se recortan espacios) | — |
| `temperature` | 0 a 1.5 | 0.3 |
| `top_p` | mayor que 0 y hasta 1 | 1.0 |
| `max_tokens` | 1 a 2000 | 300 |

Response `200`:

```json
{
  "answer": "FastAPI es un framework de Python para construir APIs...",
  "model": "dots-studio/dots-3-note-preview:free"
}
```

Errores: **422** si los datos no cumplen las reglas (el LLM ni se llama) y **502** si el LLM falla (tiempo agotado, cuota, respuesta vacía o formato inválido).

### `POST /api/v1/agent/chat`

Acepta los mismos campos que `/chat` y agrega:

| Campo | Regla | Por defecto |
|-------|-------|-------------|
| `confirm_actions` | `true` permite herramientas de escritura | `false` |
| `max_steps` | 1 a 5 rondas con el LLM | 3 |

Ejemplo (herramienta `estimate_learning_effort`):

```json
{
  "question": "Debo estudiar 5 temas de dificultad intermedia y tengo 5 horas por semana. ¿Cuántas horas y semanas necesito, qué nivel de esfuerzo es y cómo se calculó?",
  "max_tokens": 400
}
```

Response `200`:

```json
{
  "answer": "Horas totales: 20. Semanas necesarias: 4. Nivel de esfuerzo: medio. ...",
  "model": "dots-studio/dots-3-note-preview:free",
  "tools_used": ["estimate_learning_effort"]
}
```

### Herramientas disponibles

| Herramienta | Qué hace | Escritura |
|-------------|----------|-----------|
| `lookup_ai_concept` | Define un concepto de IA (RAG, embedding, function calling, fastapi) | No |
| `calculate_study_hours` | Horas totales = horas por día × días | No |
| `estimate_learning_effort` | Estima horas, semanas y nivel de esfuerzo según dificultad, número de temas y horas por semana | No |
| `create_study_task` | Crea una tarea de estudio | **Sí** (requiere `confirm_actions: true`) |

`estimate_learning_effort` usa 2 h por tema (básico), 4 h (intermedio) y 6 h (avanzado). Semanas = horas totales ÷ horas semanales, redondeado hacia arriba. Nivel de esfuerzo: hasta 10 h **bajo**, hasta 30 h **medio**, más de 30 h **alto** (umbrales definidos en `app/tools/functions.py`).

---

## Arquitectura y flujo

```
Cliente → routes → schemas → services → providers → OpenRouter (LLM)
                                  └──→ tools (solo el agente)
```

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| Router | `app/api/routes/` | Recibe la petición HTTP, inyecta el servicio con `Depends` y traduce errores a códigos HTTP |
| Schemas | `app/schemas/` | Modelos Pydantic: definen y validan entrada y salida (422 si no cumplen) |
| Servicio | `app/services/` | Lógica: arma los `messages`, y en el agente ejecuta el bucle LLM ↔ herramientas |
| Provider | `app/providers/` | Contratos (`LLMProvider`, `ToolCallingProvider`) y el adaptador `OpenRouterProvider` |
| Tools | `app/tools/` | Argumentos validados (`schemas.py`), funciones puras (`functions.py`) y catálogo/ejecución (`registry.py`) |
| Core | `app/core/` | Configuración desde variables de entorno |

### Flujo del chat (Módulo I)

`JSON → ChatRequest → messages [system, user] → payload HTTP (con API key) → texto del LLM → ChatResponse → JSON`

### Flujo del agente (Módulo III)

1. El router valida `AgentChatRequest` y crea el `AgentService`.
2. El servicio envía `messages` y el catálogo de herramientas al LLM.
3. Si el LLM responde un `tool_call`, el `registry` valida los argumentos con Pydantic, ejecuta la función y devuelve `{"ok": true, "data": ...}` (o `ok: false` con `unknown_tool`, `invalid_arguments` o `confirmation_required`).
4. El resultado vuelve al LLM como mensaje `role: tool` y el ciclo se repite (máximo `max_steps`).
5. Cuando el LLM responde texto, sale `AgentChatResponse` con `answer`, `model` y `tools_used`.

El LLM **decide**, nuestro código **ejecuta**. Diagrama de secuencia por archivo: `docs/Modulo_III/secuencia.png`.

### Manejo de errores

| Situación | Resultado |
|-----------|-----------|
| Datos inválidos (Pydantic) | `422` |
| Falla del LLM, cuota agotada, respuesta vacía | `502` |
| Agente sin respuesta final o con límite de rondas superado | `502` |
| Herramienta desconocida, argumentos inválidos o falta confirmación | No es error HTTP: el resultado `ok: false` vuelve al LLM |

---

## Estructura del proyecto

```
ai-knowledge-assistant/
├── app/
│   ├── main.py                        # Crea la app y registra los routers
│   ├── core/
│   │   └── config.py                  # Lee OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL
│   ├── api/routes/
│   │   ├── chat.py                    # POST /api/v1/chat
│   │   ├── agent.py                   # POST /api/v1/agent/chat
│   │   ├── health.py                  # GET /health
│   │   └── info.py                    # GET /api/v1/info
│   ├── schemas/
│   │   ├── chat.py                    # ChatRequest, ChatResponse
│   │   ├── agent.py                   # AgentChatRequest, AgentChatResponse
│   │   ├── health.py
│   │   └── info.py
│   ├── services/
│   │   ├── assistant_service.py       # Prompt de sistema + llamada al proveedor
│   │   └── agent_service.py           # Bucle del agente
│   ├── providers/
│   │   ├── base.py                    # LLMProvider y ToolCallingProvider (contratos)
│   │   ├── openrouter.py              # Adaptador real (HTTP, timeout 30 s, errores)
│   │   └── fake.py                    # Proveedor falso para pruebas
│   └── tools/
│       ├── schemas.py                 # Contratos Pydantic de los argumentos
│       ├── functions.py               # Funciones Python puras
│       └── registry.py                # REGISTRY, tool_definitions(), execute_tool()
├── scripts/
│   ├── asyncio_demo.py                # Secuencial vs concurrente
│   ├── httpx_demo.py                  # Cliente HTTP asíncrono
│   └── run_labs.py                    # Ejecuta laboratorios contra la API local
├── tests/
│   ├── conftest.py                    # Simula OpenRouter con httpx.MockTransport
│   ├── unit/
│   └── integration/
├── docs/
│   ├── Bitacora/                      # Bitácoras de los experimentos, respuestas y esquemas
│   ├── Modulo_III/                    # Diagrama de secuencia y guía de Swagger
│   └── Modulos_I_y_III.md             # Resumen técnico de los módulos
├── env.example                        # Plantilla de configuración (sin secretos)
├── pyproject.toml
└── README.md
```

---

## Instalación y configuración

Requisitos: Python **3.12+** y Git.

```powershell
git clone https://github.com/MendVal/ai-knowledge-assistant.git
cd ai-knowledge-assistant
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux / macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

Configura el `.env` a partir de la plantilla:

```powershell
copy env.example .env
```

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `OPENROUTER_API_KEY` | Tu API key de OpenRouter | — (obligatoria) |
| `OPENROUTER_MODEL` | Modelo a usar | `openrouter/free` |
| `OPENROUTER_BASE_URL` | URL base de la API | `https://openrouter.ai/api/v1` |

> **Seguridad:** `.env` está en `.gitignore`; nunca lo subas. Si una key se expone, revócala en OpenRouter y crea otra.

---

## Ejecución

```powershell
fastapi dev
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

Para detener el servidor, presiona `Ctrl + C`.

---

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas **no usan la red ni consumen cuota**: simulan OpenRouter con `httpx.MockTransport` y reemplazan dependencias con `dependency_overrides`.

| Archivo | Qué cubre |
|---------|-----------|
| `tests/unit/test_assistant_service.py` | Servicio del chat con proveedor falso |
| `tests/unit/test_openrouter_provider.py` | Adaptador: éxito, errores HTTP, timeout, respuesta vacía, `complete_with_tools` |
| `tests/unit/test_tools.py` | Registro de herramientas: expuestas, cálculo, argumentos inválidos, herramienta desconocida |
| `tests/unit/test_estimate_learning_effort.py` | `estimate_learning_effort`: caso base, valores límite, argumentos válidos e inválidos, registro |
| `tests/unit/test_agent_tools.py` | Bucle del agente: uso de herramienta, límite de rondas, confirmación |
| `tests/integration/test_api.py` | `/health`, `/chat` (200, 422, 502) e `/info` |
| `tests/integration/test_agent_api.py` | `/agent/chat` de punta a punta con LLM simulado |
| `tests/integration/test_agent_endpoint.py` | Agente sin herramientas, 422 y convivencia con el chat |

Resultado esperado: todas pasan (**65 tests** en la última verificación).

---

## Laboratorios y documentación

Los experimentos del Módulo I (temperatura, `max_tokens`, modelos, alucinaciones) están documentados en `docs/Bitacora/`, con respuestas completas en `docs/Bitacora/respuestas/` y capturas en `docs/Bitacora/capturas/`. Los esquemas del flujo (cajitas, viaje de la pregunta y flujo del JSON) también están en esa carpeta.

Para el Módulo III: `docs/Modulo_III/secuencia.png` (diagrama de secuencia) y `docs/Modulo_III/Swagger_estimate_learning_effort.md` (cómo probar la herramienta en Swagger).

---

## Scripts

```powershell
python scripts/asyncio_demo.py      # secuencial (~3 s) vs concurrente (~1 s)
python scripts/httpx_demo.py        # consume /health y /api/v1/chat (API en otra terminal)
python scripts/run_labs.py mod3     # ejecuta laboratorios reales: exp1, exp2, exp4, mod3
```

`run_labs.py` guarda cada respuesta en `docs/Bitacora/respuestas/` y una tabla en `docs/Bitacora/resultados_labs.md`. Necesita la API corriendo (`fastapi dev`) y consume la cuota del modelo; si recibe un 429, se detiene.

---

## Flujo de trabajo con Git

| Rama | Propósito |
|------|-----------|
| `main` | Rama principal y estable |
| `feat/bootstrap-api` | Módulo 0 |
| `feat/module-1-llm-integration` | Módulo I y bitácoras |
| `feat/module-3-tool-calling` | Módulo III |

Los cambios llegan a `main` mediante **Pull Request**.

| Prefijo de commit | Uso |
|-------------------|-----|
| `chore:` | Configuración y mantenimiento |
| `feat:` | Nueva funcionalidad |
| `test:` | Pruebas |
| `docs:` | Documentación |

---

## Límites conocidos

- Los modelos gratuitos de OpenRouter tienen cuota (20 solicitudes por minuto y 50 por día sin créditos) y fallan de forma intermitente: pueden devolver respuesta vacía o 429, que la API reporta como `502`.
- No todos los modelos gratuitos soportan tool calling; el agente puede dar `502` con alguno de ellos.
- Las tareas creadas por `create_study_task` se guardan en memoria y se pierden al reiniciar el servidor.
- Los umbrales del nivel de esfuerzo de `estimate_learning_effort` son una decisión propia del proyecto, no vienen del enunciado.
- Fuera de alcance por ahora: RAG, bases de datos, memoria conversacional, Docker y autenticación.
