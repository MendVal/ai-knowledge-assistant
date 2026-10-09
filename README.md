# AI Knowledge Assistant

API asíncrona con FastAPI que recibe una pregunta y responde con un asistente local de bootstrap.
No usa ningún LLM todavía; es la base para los siguientes módulos.

## Requisitos

- Python 3.12 o superior
- Git

## Instalación

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # CMD: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Ejecutar la API

```powershell
fastapi dev
```

Documentación Swagger: http://127.0.0.1:8000/docs

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /health | Estado del servicio |
| POST | /api/v1/chat | Responde una pregunta (3 a 2000 caracteres) |
| GET | /api/v1/info | Información básica del proyecto |

Ejemplo:

```json
POST /api/v1/chat
{ "question": "¿Qué es FastAPI?" }
```

## Pruebas

```powershell
python -m pytest -q
```

## Demos

```powershell
python scripts/asyncio_demo.py
python scripts/httpx_demo.py      # requiere la API corriendo en otra terminal
```

## Estructura

```
app/
  main.py
  api/routes/     # endpoints HTTP
  schemas/        # modelos Pydantic
  services/       # lógica del asistente
scripts/
tests/
  unit/
  integration/
```
