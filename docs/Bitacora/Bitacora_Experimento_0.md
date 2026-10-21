# Experimento 0 · Línea base y validación

**Módulo I · Laboratorio con LLM**

| Campo | Información |
|---|---|
| Nombre | Valentina Mendivil Correa |
| Fecha | 21/10/2026 |
| Repositorio | https://github.com/MendVal/ai-knowledge-assistant |
| Rama | `feat/module-1-llm-integration` |
| Herramienta | Thunder Client (VS Code) contra `http://127.0.0.1:8000/api/v1/chat` |

## 1. Objetivo y condiciones

Comprobar que los datos de partida son válidos y distinguir un error interno de la API (422, rechazado por Pydantic) de una respuesta del modelo.

| Condición | Valor |
|---|---|
| Ruta / método | `POST /api/v1/chat` |
| Pregunta (línea base) | Explica qué es una API REST con un ejemplo educativo. |
| temperature / top_p | 0.3 / 1.0 |
| max_tokens | 300 |
| Modelo configurado | `openrouter/free` (enrutador gratuito; el modelo real que responde puede variar) |
| Prompt de sistema | Eres AI Knowledge Assistant, un asistente educativo especializado en tecnología. Responde en español claro. Explica los conceptos con ejemplos sencillos. Si no tienes suficiente información, indícalo. No inventes referencias ni datos. |

## 2. Resultados

| Prueba | HTTP esperado | HTTP observado | Evidencia / interpretación |
|---|---|---|---|
| Línea base | 200 | 200 | La API devolvió `answer` y `model`. Duración 8.05 s, tamaño 414 bytes. Respuesta en [`respuestas/01.txt`](respuestas/01.txt). |
| `question = "A"` | 422 | 422 | Pydantic rechazó la petición: `string_too_short` en `body.question`, "String should have at least 3 characters" (`min_length: 3`). Duración 0.377 s. Respuesta en [`respuestas/02.txt`](respuestas/02.txt). |
| `temperature = -1` | 422 | 422 | Pydantic rechazó la petición: `greater_than_equal` en `body.temperature`, "Input should be greater than or equal to 0" (`ge: 0.0`). Duración 0.119 s. Respuesta en [`respuestas/03.txt`](respuestas/03.txt). |

## 3. Bitácora

| ID | Modelo exacto | T | Top-p | Max | Status | Seg. | Archivo | Observaciones |
|---|---|---|---|---|---|---|---|---|
| 01 | `openrouter/free` | 0.3 | 1.0 | 300 | 200 | 8.05 | [`01.txt`](respuestas/01.txt) | Respuesta cortada en "Es el intermediario". |
| 02 | No se ejecutó | 0.3 | 1.0 | 300 | 422 | 0.377 | [`02.txt`](respuestas/02.txt) | `question = "A"`. Rechazada antes de llamar al LLM. |
| 03 | No se ejecutó | -1 | 1.0 | 300 | 422 | 0.119 | [`03.txt`](respuestas/03.txt) | Pregunta válida con `temperature = -1`. Rechazada antes de llamar al LLM. |

> Nota: el texto de las respuestas está transcrito de las capturas de Thunder Client; su tamaño coincide con el reportado (414, 150 y 150 bytes). La hora de cada ejecución no se registró.

## 4. Conclusiones del Experimento 0

Las dos peticiones inválidas devolvieron 422 en 0.377 s y 0.119 s, mientras la línea base tardó 8.05 s. Esa diferencia indica que el LLM no se ejecutó en los casos inválidos: Pydantic, en la capa de schemas, rechazó la petición antes de llegar al servicio y al proveedor. El mensaje de error nombra el campo exacto (`question` o `temperature`) y la regla incumplida (`min_length=3` y `ge=0`).

En la línea base, la respuesta terminó cortada ("Es el intermediario"). La causa más probable es el límite `max_tokens=300`, que puede haberse consumido en parte si el modelo enrutado razona antes de responder. No se puede confirmar, porque la API no devuelve el motivo de finalización ni el modelo que respondió.

**Límites del experimento:** la línea base se ejecutó una sola vez y con `openrouter/free`, que puede enrutar a modelos distintos, así que no sirve como prueba estadística.
