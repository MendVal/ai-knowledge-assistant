# Mini-proyecto: `estimate_learning_effort` en Swagger

## Cómo probarlo
1. `fastapi dev` y abrir http://127.0.0.1:8000/docs
2. Abrir **POST /api/v1/agent/chat** → *Try it out*.
3. Pegar este body y *Execute*:

```json
{
  "question": "Debo estudiar 5 temas de dificultad intermedia y tengo 5 horas por semana. ¿Cuántas horas y semanas necesito, qué nivel de esfuerzo es y cómo se calculó?",
  "temperature": 0.3,
  "top_p": 1.0,
  "max_tokens": 400,
  "confirm_actions": false,
  "max_steps": 3
}
```

## Cómo llega la solicitud (lo que ve el LLM)
El LLM no recibe tu JSON tal cual: recibe `messages` + `tools`, y responde un `tool_call`:

```json
{"name": "estimate_learning_effort",
 "arguments": "{\"difficulty\":\"intermedio\",\"topics\":5,\"weekly_hours\":5}"}
```

## Resultado de la herramienta (vuelve al LLM como `role: tool`)
```json
{"ok": true, "data": {
  "total_hours": 20, "weeks": 4, "effort_level": "medio",
  "explanation": "5 temas x 4 h por tema (intermedio) = 20 h. 20 h / 5 h por semana = 4.00 -> 4 semana(s). Esfuerzo medio."}}
```

## Respuesta final esperada en Swagger (200)
```json
{"answer": "<texto del LLM: 20 horas, 4 semanas, esfuerzo medio y el cálculo>",
 "model": "<modelo del .env>",
 "tools_used": ["estimate_learning_effort"]}
```
Lo importante de comprobar: `tools_used` contiene `estimate_learning_effort`.
(El texto de `answer` lo redacta el LLM, por eso varía entre llamadas.)

## Casos para mostrar
| Caso | Qué pasa |
|---|---|
| Pregunta del enunciado | 20 h, 4 semanas, esfuerzo medio |
| `weekly_hours` = 0 o `topics` = 0 | La herramienta responde `invalid_arguments`; el LLM lo explica |
| `question` de 1 letra | 422 antes de llamar al LLM |
| Sin cuota o modelo sin tool calling | 502 |

## Supuesto a confirmar
El enunciado no define los umbrales del **nivel de esfuerzo**. Usé: ≤ 10 h bajo, ≤ 30 h medio, > 30 h alto (`EFFORT_LEVELS` en `app/tools/functions.py`).
