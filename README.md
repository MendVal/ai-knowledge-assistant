# AI Knowledge Assistant

API asíncrona construida con **FastAPI** que recibe una pregunta y responde con un asistente local de *bootstrap*.
Es el primer incremento funcional del proyecto **AI Knowledge Assistant**, pensado para evolucionar en módulos posteriores hacia un sistema de IA real.

> **Alcance del Módulo 0:** esta versión **no** integra ningún LLM. El objetivo es establecer una base de software confiable: contratos HTTP claros, validación, separación de responsabilidades, procesamiento asíncrono, pruebas automatizadas y un flujo profesional de Git.

---

## Tabla de contenido

1. [Tecnologías](#tecnologías)
2. [Endpoints](#endpoints)
3. [Arquitectura](#arquitectura)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Requisitos](#requisitos)
6. [Instalación](#instalación)
7. [Ejecución](#ejecución)
8. [Pruebas](#pruebas)
9. [Scripts de demostración](#scripts-de-demostración)
10. [Flujo de trabajo con Git](#flujo-de-trabajo-con-git)
11. [Alcance y próximos pasos](#alcance-y-próximos-pasos)

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3.12+ | Lenguaje base |
| FastAPI | Framework para construir la API |
| Pydantic | Validación y serialización de datos |
| AsyncIO | Programación asíncrona (`async` / `await`) |
| HTTPX | Cliente HTTP asíncrono |
| pytest + pytest-asyncio | Pruebas unitarias y de integración |
| Git / GitHub | Control de versiones y Pull Requests |

---

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|--------|------|-------------|------------|
| `GET` | `/health` | Estado del servicio | `200` |
| `POST` | `/api/v1/chat` | Responde una pregunta | `200`, `422` |
| `GET` | `/api/v1/info` | Información básica del proyecto | `200` |
| `GET` | `/docs` | Documentación interactiva (Swagger UI) | `200` |

### `POST /api/v1/chat`

Reglas de validación: la pregunta debe tener entre **3 y 2000 caracteres** (se recortan los espacios al inicio y al final). Si no las cumple, la API responde **422**.

Request:

```json
{
  "question": "¿Qué es FastAPI?"
}
```

Response `200`:

```json
{
  "answer": "FastAPI es un framework de Python para construir APIs basado en type hints y ASGI.",
  "provider": "bootstrap-local"
}
```

El valor `bootstrap-local` indica que la respuesta proviene del asistente local y **no** de un LLM real.

El asistente reconoce estas palabras clave: `fastapi`, `pydantic`, `asyncio`, `httpx` y `pytest`. Si la pregunta no contiene ninguna, devuelve un mensaje genérico indicando que la API está operativa.

### `GET /api/v1/info`

```json
{
  "name": "AI Knowledge Assistant",
  "version": "0.1.0",
  "environment": "development",
  "llm_enabled": false
}
```

### `GET /health`

```json
{
  "status": "ok",
  "service": "ai-knowledge-assistant",
  "version": "0.1.0"
}
```

---

## Arquitectura

El proyecto separa la capa HTTP, los modelos de datos y la lógica de negocio:

```
Cliente → FastAPI → Pydantic → Router → Servicio → Respuesta
```

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| Router | `app/api/routes/` | Recibe la petición HTTP y llama al servicio. No contiene lógica. |
| Schemas | `app/schemas/` | Modelos Pydantic: definen y validan los datos de entrada y salida. |
| Servicio | `app/services/` | Contiene la lógica del asistente. |

Esta separación permite que, en el próximo módulo, solo cambie el servicio (para conectar un LLM) mientras los contratos HTTP permanecen estables.

---

## Estructura del proyecto

```
ai-knowledge-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                       # Crea la app y registra los routers
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py               # POST /api/v1/chat
│   │       ├── health.py             # GET /health
│   │       └── info.py               # GET /api/v1/info
│   ├── schemas/
│   │   ├── chat.py                   # ChatRequest, ChatResponse
│   │   ├── health.py                 # HealthResponse
│   │   └── info.py                   # InfoResponse
│   └── services/
│       └── assistance_service.py     # Lógica del asistente local
├── scripts/
│   ├── asyncio_demo.py               # Ejecución secuencial vs concurrente
│   └── httpx_demo.py                 # Cliente HTTP asíncrono
├── tests/
│   ├── unit/
│   │   └── test_assistant_service.py
│   └── integration/
│       └── test_api.py
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Requisitos

- Python **3.12** o superior
- Git

Verifica tu versión de Python:

```powershell
python --version
```

---

## Instalación

1. Clona el repositorio:

```powershell
git clone https://github.com/MendVal/ai-knowledge-assistant.git
cd ai-knowledge-assistant
```

2. Crea el entorno virtual:

```powershell
python -m venv .venv
```

3. Actívalo:

```powershell
# PowerShell
.venv\Scripts\Activate.ps1

# CMD
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

4. Instala el proyecto con las dependencias de desarrollo:

```powershell
pip install -e ".[dev]"
```

---

## Ejecución

```powershell
fastapi dev
```

- API: http://127.0.0.1:8000
- Documentación Swagger: http://127.0.0.1:8000/docs

Para detener el servidor, presiona `Ctrl + C`.

---

## Pruebas

```powershell
python -m pytest -q
```

Resultado esperado: **5 passed**.

| ID | Tipo | Qué verifica |
|----|------|--------------|
| T-01 | Unitaria | El servicio responde correctamente a una pregunta conocida |
| T-02 | Integración | `GET /health` retorna `200` |
| T-03 | Integración | `POST /api/v1/chat` con pregunta válida retorna `200` |
| T-04 | Integración | `POST /api/v1/chat` con pregunta demasiado corta retorna `422` |
| T-05 | Integración | `GET /api/v1/info` retorna `200` y `llm_enabled = false` |

Las pruebas de integración usan `ASGITransport`, por lo que **no necesitan un servidor en ejecución**.

---

## Scripts de demostración

**AsyncIO: ejecución secuencial vs concurrente**

```powershell
python scripts/asyncio_demo.py
```

Simula tres llamadas de 1 segundo. En forma secuencial tardan ~3 s; con `asyncio.gather` tardan ~1 s.

**HTTPX: cliente HTTP asíncrono**

```powershell
python scripts/httpx_demo.py
```

Consume `/health` y `/api/v1/chat`. Requiere que la API esté corriendo en otra terminal (`fastapi dev`).

---

## Flujo de trabajo con Git

### Ramas

| Rama | Propósito |
|------|-----------|
| `main` | Rama principal y estable |
| `feat/bootstrap-api` | Desarrollo del primer incremento funcional |

Los cambios llegan a `main` mediante un **Pull Request** desde `feat/bootstrap-api`.

### Convención de commits

| Prefijo | Uso |
|---------|-----|
| `chore:` | Configuración y mantenimiento del proyecto |
| `feat:` | Nueva funcionalidad |
| `test:` | Pruebas |
| `docs:` | Documentación |

Historial de la rama de trabajo:

```
docs: improve README with project structure and workflow
test: add bootstrap API test suite
feat: add asyncio and httpx demos
feat: register routers in FastAPI app
feat: add application info endpoint
feat: add bootstrap chat endpoint
feat: add health endpoint
chore: initialize AI knowledge assistant project
```

---

## Alcance y próximos pasos

**Incluido en este módulo:** API asíncrona con FastAPI, validación con Pydantic, separación en capas, demostraciones con AsyncIO y HTTPX, pruebas unitarias y de integración, y flujo profesional de Git.

**Fuera de alcance por ahora:** proveedores LLM (OpenAI, Anthropic, Gemini, Ollama), LangChain / LangGraph, PostgreSQL / Redis / bases vectoriales, Docker, RAG, agentes y memoria conversacional.

