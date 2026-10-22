# Experimento 1 · Temperatura

**Módulo I · Laboratorio con LLM**

| Campo | Información |
|---|---|
| Nombre | Valentina Mendivil Correa |
| Fecha | 21/10/2026 (llamadas entre las 18:55 y las 19:16, hora de Bogotá) |
| Repositorio | https://github.com/MendVal/ai-knowledge-assistant |
| Rama | `feat/module-1-llm-integration` |
| Herramienta | Thunder Client (VS Code) contra `http://127.0.0.1:8000/api/v1/chat` |

## 1. Hipótesis y condiciones

**Hipótesis:** con temperatura alta puede aumentar la variación de las respuestas. No se exige que una ejecución concreta sea más creativa o más precisa.

| Condición | Valor |
|---|---|
| Pregunta fija | Explica el concepto de IA usando una analogía comprensible para un aprendiz de software. |
| Modelo fijo | `dots-studio/dots-3-note-preview:free` (campo `model` de cada respuesta) |
| top_p / max_tokens | 1.0 / 300 |
| Prompt de sistema | Eres AI Knowledge Assistant, un asistente educativo especializado en tecnología. Responde en español claro. Explica los conceptos con ejemplos sencillos. Si no tienes suficiente información, indícalo. No inventes referencias ni datos. |
| Temperaturas | 0.1, 0.5 y 1.0 (la guía pide 5 respuestas por cada una) |

**Definición de "respuesta claramente distinta"** (escrita antes de evaluar): una respuesta es claramente distinta de otra si su **analogía principal** es diferente. Cambios de redacción, de saludo o de formato con la misma analogía no cuentan.

## 2. Bitácora de llamadas

| ID | Modelo exacto | T | Top-p | Max | Status | Seg. | Observaciones |
|---|---|---|---|---|---|---|---|
| 0.1-P | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | **800** | 200 | 12.72 | 256 bytes. Llamada de prueba con max_tokens 800, **fuera de las condiciones del experimento**, no cuenta. Cortada en "La IA como un". |
| 0.1-A | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | 300 | 200 | 6.78 | 204 bytes. Cortada antes de llegar a la analogía: "...una analogía que cualquier aprendiz de software puede entender." |
| 0.1-B | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | 300 | 200 | 6.38 | 127 bytes. Cortada en "una analogía que conect". Sin analogía visible. |
| 0.1-C | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | 300 | 200 | 6.48 | 311 bytes. Analogía: "Un Robot de Fábrica vs. Un Aprendiz de Programador" (programa tradicional frente a un sistema que "aprende"). |
| 0.1-D | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | 300 | 502 | 6.31 | 93 bytes. `Respuesta vacía`. |
| 0.1-E | `dots-studio/dots-3-note-preview:free` | 0.1 | 1.0 | 300 | 502 | 6.55 | 93 bytes. `Respuesta vacía`. |
| 0.5-A | `dots-studio/dots-3-note-preview:free` | 0.5 | 1.0 | 300 | 200 | 5.49 | 334 bytes. Analogía: la IA como "un aprendiz en lugar de un seguidor" de instrucciones. Cortada en "un seguidor". |
| 0.5-B | `dots-studio/dots-3-note-preview:free` | 0.5 | 1.0 | 300 | 200 | 6.06 | 314 bytes. Analogía: una función de software que "aprende" en lugar de ser escrita línea por línea. Cortada en "ser escrita línea". |
| 0.5-C | `dots-studio/dots-3-note-preview:free` | 0.5 | 1.0 | 300 | 200 | 5.98 | 301 bytes. Analogía: "Receta de Cocina vs. Aprendiz de Chef" (escribir un programa tradicional frente a entrenar un modelo de IA). |
| 0.5-D | `dots-studio/dots-3-note-preview:free` | 0.5 | 1.0 | 300 | 200 | 6.40 | 185 bytes. Cortada antes de la analogía: "...una analogía que un aprendiz de software entenderá perfectamente, ya que se basa". |
| 0.5-E | `dots-studio/dots-3-note-preview:free` | 0.5 | 1.0 | 300 | 200 | 6.13 | 275 bytes. Analogía: "Un Compañero de Trabajo que Aprende con el Tiempo". |
| 1.0-A | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 200 | 6.33 | 303 bytes. Analogía: "Un Aprendiz de Software Muy Especial", donde el lector es el jefe de un equipo. Cortada en "jefe de un equipo". |
| 1.0-B | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 502 | 6.24 | 93 bytes. `Respuesta vacía` (ver captura). |
| 1.0-C | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 200 | 6.23 | 241 bytes. Analogía: "Un Chef Programador vs. Un Chef Trad(icional)". Cortada en "Chef Trad". |
| 1.0-D | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 200 | 6.63 | 236 bytes. Analogía: "Un Chef vs. Un..." (cortada, misma imagen del chef). |
| 1.0-E | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 502 | 6.61 | 93 bytes. `Respuesta vacía`. |
| 1.0-F | `dots-studio/dots-3-note-preview:free` | 1.0 | 1.0 | 300 | 502 | 6.62 | 93 bytes. `Respuesta vacía`. |

Nota: el texto está transcrito de las capturas de Thunder Client. De 5 intentos con temperatura 0.1, 3 devolvieron respuesta y 2 dieron 502. Con temperatura 1.0 hay evidencia de 6 intentos: 3 devolvieron respuesta y 3 dieron 502 (hubo más intentos fallidos sin captura, que no se cuentan). Con 0.5 se registraron 5 respuestas válidas. Con 0.1 (3) y 1.0 (3) faltan respuestas para llegar a 5, por eso la tabla de resultados queda incompleta en esas dos temperaturas.

### Respuestas íntegras recibidas

**0.1-A (6.78 s):**
> ¡Claro! Aquí tienes una explicación del concepto de IA usando una analogía que cualquier aprendiz de software puede entender. ---

**0.1-B (6.38 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que conect

**0.1-C (6.48 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que seguramente ya conoces: **la diferencia entre un programa tradicional y un sistema que "aprende"**. --- ### 🤖 La Analogía: Un Robot de Fábrica vs. Un Aprendiz de Programador

**0.5-A (5.49 s):**
> ¡Claro! Como aprendiz de software, estás familiarizado con la idea de que un programa sigue un conjunto de instrucciones definidas por un desarrollador. La IA es como tomar ese concepto y darle un giro radical. Piensa en ella como **un aprendiz en lugar de un seguidor

**0.5-B (6.06 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que relaciona conceptos de IA con ideas que ya conoces de la programación software. --- ### **Analogía: La IA es como una función de software que "aprende" en lugar de ser escrita línea

**0.5-C (5.98 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que ya conoces bien: **la diferencia entre escribir un programa tradicional y entrenar un modelo de IA**. --- ### 🔍 Analogía: Receta de Cocina vs. Aprendiz de Chef

**0.5-D (6.40 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que un aprendiz de software entenderá perfectamente, ya que se basa

**0.5-E (6.13 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que seguramente te resultará familiar si estás aprendiendo software. --- ### **Analogía: Un "Compañero de Trabajo" que Aprende con el Tiempo**

**1.0-C (6.23 s):**
> ¡Claro! Vamos a explicar la IA con una analogía que conecta perfectamente con lo que ya sabes sobre programación. ### Analogía: Un "Chef Programador" vs. Un "Chef Trad

**1.0-D (6.63 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que seguramente te resultará familiar si estás aprendiendo software. --- ### **La Analogía: Un "Chef" vs. Un

**1.0-A (6.33 s):**
> ¡Claro! Vamos a explicar la IA usando una analogía que seguramente te resultará familiar si estás aprendiendo software. --- ### **La Analogía: Un "Aprendiz de Software" Muy Especial** Imagina que eres el **jefe de un equipo

### Fallos observados

| Situación | Qué pasó |
|---|---|
| 502 por `Respuesta vacía` (varias veces; 2 de 5 intentos con 0.1) | El modelo devolvió el campo `content` vacío. El adaptador lanzó `ValueError("Respuesta vacía")` (`app/providers/openrouter.py`, línea 80) y el router lo convirtió en 502: "No fue posible obtener una respuesta del LLM: Formato de respuesta LLM inválido". Con 0.5 se resolvió reintentando; con 1.0 hubo 3 fallos capturados frente a 3 respuestas válidas. |
| Respuestas truncadas | Todas las respuestas válidas se cortan a mitad de frase (256 a 334 bytes), con max_tokens 300 y también con 800. Entonces el límite configurado no es la causa; probablemente el modelo gasta parte de la generación en razonamiento interno, aunque la API no lo confirma. |

### Capturas

| Llamada | Captura |
|---|---|
| 0.1-P (max_tokens 800, no válida) | ![0.1 prueba](capturas/exp1_t0.1_max800_prueba_no_valida.png) |
| 0.1-A, 200 | ![0.1 A](capturas/exp1_t0.1_llamada_A_200.png) |
| 0.1-B, 200 | ![0.1 B](capturas/exp1_t0.1_llamada_B_200.png) |
| 0.1-C, 200 | ![0.1 C](capturas/exp1_t0.1_llamada_C_200.png) |
| 0.1-D, 502 | ![0.1 D](capturas/exp1_t0.1_502_D.png) |
| 0.1-E, 502 | ![0.1 E](capturas/exp1_t0.1_502_E.png) |
| 0.5-A, 200 | ![0.5 A](capturas/exp1_t0.5_llamada_A_200.png) |
| 0.5-B, 200 | ![0.5 B](capturas/exp1_t0.5_llamada_B_200.png) |
| 0.5-C, 200 | ![0.5 C](capturas/exp1_t0.5_llamada_C_200.png) |
| 0.5-D, 200 | ![0.5 D](capturas/exp1_t0.5_llamada_D_200.png) |
| 0.5-E, 200 | ![0.5 E](capturas/exp1_t0.5_llamada_E_200.png) |
| 1.0-A, 200 | ![1.0 A](capturas/exp1_t1.0_200.png) |
| 1.0-B, 502 | ![1.0 502](capturas/exp1_t1.0_502_respuesta_vacia.png) |
| 1.0-C, 200 | ![1.0 C](capturas/exp1_t1.0_llamada_C_200.png) |
| 1.0-D, 200 | ![1.0 D](capturas/exp1_t1.0_llamada_D_200.png) |
| 1.0-E, 502 | ![1.0 E](capturas/exp1_t1.0_502_E.png) |
| 1.0-F, 502 | ![1.0 F](capturas/exp1_t1.0_502_F.png) |

## 3. Tabla de resultados

| Temp. | Respuestas válidas con evidencia | N.º de respuestas claramente distintas | Hallazgo principal |
|---|---|---|---|
| 0.1 | 3 de 5 intentos (2 fallaron con 502) | No evaluable: solo 1 de las 3 llega a mostrar una analogía | Dos respuestas se cortaron antes de la analogía (127 y 204 bytes); la tercera usó "Robot de Fábrica vs. Aprendiz de Programador". |
| 0.5 | 5 (completa) | 4 de las 4 que muestran analogía (aprendiz vs. seguidor; función que aprende; receta vs. chef; compañero de trabajo). La quinta se cortó antes de la analogía. | Cuatro imágenes distintas, aunque todas giran alrededor de la misma idea de fondo: un programa que aprende frente a uno que solo sigue instrucciones. |
| 1.0 | 3 (con 3 fallos 502 capturados) | 2 imágenes distintas en 3 respuestas: "jefe de un equipo" y "chef" (aparece en dos respuestas) | Hubo una imagen repetida (el chef) y una distinta, pero la mitad de los intentos con evidencia falló con respuesta vacía. |

## 4. Preguntas del análisis (Experimento 1)

**1. ¿Qué variable provocó las diferencias más visibles y cómo lo comprobaste?**

Cambié solo la temperatura (0.1, 0.5 y 1.0) y dejé igual la pregunta, el top_p, el max_tokens, el prompt de sistema y el modelo (lo confirmé en el campo `model` de cada respuesta). Con lo que tengo, la diferencia más visible apareció con 0.5, la única tanda completa (5 respuestas válidas): las 4 respuestas que alcanzaron a mostrar analogía usaron imágenes distintas ("aprendiz en lugar de un seguidor", "función que aprende", "receta de cocina vs. aprendiz de chef" y "compañero de trabajo que aprende"). Con 1.0 hay 3 respuestas: una con "jefe de un equipo" y dos con la imagen del "chef" (programador vs. tradicional), es decir 2 imágenes distintas y una repetida. Con 0.1 solo una respuesta mostró analogía ("robot de fábrica vs. aprendiz de programador"), así que esa tanda no se puede comparar. Tampoco puedo decir que la mayor variedad se deba a la temperatura: hay pocas respuestas, varias salieron cortadas antes de la analogía y el modelo falló con frecuencia (2 de 5 intentos con 0.1 dieron respuesta vacía y con 1.0 hay 3 fallos capturados contra 3 respuestas válidas). Lo único que sé comprobar es que cambié solo la temperatura y mantuve igual lo demás, y que en 0.5 hubo variedad de analogías.

**2. ¿Por qué una mayor temperatura no demuestra automáticamente mayor calidad?**

La temperatura solo cambia el azar con el que el modelo elige el siguiente token: sube la variación, pero no la exactitud ni la claridad. Una respuesta distinta no es mejor por ser distinta. En mi caso, la analogía del "jefe de un equipo" no es más correcta que la del "aprendiz en lugar de un seguidor". Además, más temperatura puede dar respuestas menos coherentes o con más riesgo de errores. Y en este experimento, con 1.0 hubo muchos fallos y una imagen repetida (el chef), no respuestas claramente mejores. Para juzgar calidad hay que revisar la exactitud, la claridad y el cumplimiento de la instrucción, no solo qué tan variada es.

## 5. Conclusiones y límites

La hipótesis solo se puede apoyar de forma débil. Con 0.5 aparecieron 4 analogías distintas en 4 respuestas visibles, con 1.0 hubo 2 imágenes distintas en 3 respuestas (el chef se repite) y con 0.1 solo hay una analogía visible, así que no se puede comparar la variación entre temperaturas. Todas las analogías comparten la misma idea de fondo (programa que aprende frente a uno que solo sigue instrucciones), lo que indica que el modelo conserva el mismo enfoque aunque cambie la imagen. No es concluyente. Las respuestas de este modelo salen truncadas, así que solo se compara el inicio y la analogía elegida, no la extensión ni la corrección completa. Además, el modelo `dots-3-note-preview:free` es inestable: devuelve contenido vacío con frecuencia, y un 200 no garantiza una respuesta útil.

**Límites del experimento:** faltan respuestas válidas para completar 5 en 0.1 (hay 3) y en 1.0 (hay 3); 0.5 está completa; el modelo es un "preview" gratuito que trunca su salida y falla de forma intermitente; la API no informa el motivo de finalización de la respuesta; y 5 repeticiones por temperatura no son una prueba estadística concluyente.
