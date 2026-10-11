---
status: current
lang: es
kind: confirmatory
---

# Resultados — R13 CONFIRMATORIA

**11 de octubre de 2026 · preregistro `PREREGISTRATION_BENCH_R1X_ES.md`
sec. 2 con Enmiendas 7-12 · corrida `--confirm` con entorno bloqueado
(Python 3.11 del `.venv`), digests verificados contra el manifiesto y
servidor exclusivo · 251 preguntas**

## Cifras

251 preguntas emparejadas (simples 100, cruzadas 30, actualizadas 31,
contradicciones 30, borradas 30, sin respuesta 30; sin las 3 de N1; con el
subconjunto LongMemEval MIT congelado por SHA). 5 brazos: A0/A1/A2 (3
respondedores), A3 (3 digestores x 3 respondedores), A4 (diagonal con Γ).

| Brazo | Exactitud |
|---|---|
| A0 (sin memoria) | 0.238 |
| A1 (documento completo) | 0.316 |
| A2 (RAG crudo) | 0.608 |
| A3 (wiki) | 0.462 (digestores: qwen2.5 0.495, llama3.2 0.381, gemma2 0.510) |
| A4 (wiki + Γ) | 0.434 |

**Estadístico primario: A3 − A2 por pregunta = -0.146 [-0.186, -0.106]**
(agrupado por pregunta, 10.000 remuestreos, semilla 20261005). Por
digestor: qwen2.5 −0.113, llama3.2 −0.227, gemma2 −0.098. Por tipo:
simple −0.231, cross −0.304, updated −0.222 [−0.358, −0.082],
contradiction −0.056, deleted +0.115 [0.044, 0.189], unanswerable +0.022.

## Veredictos preregistrados (sec. 2.7)

| Hipótesis | Veredicto |
|---|---|
| R13-H1: la wiki supera al RAG crudo | **MUERE**: estimación −0.146 con CI95 enteramente negativo |
| R13-H2: la wiki gana en actualización y olvido | **no concluyente**: pierde actualización (−0.222, CI95 negativo) pero GANA olvido (+0.115 [0.044, 0.189], n=30) |
| R13-H3: piso de claims ancladas explica la utilidad | **la compuerta se retira como regla**: todas las celdas tienen 39-2400 claims ancladas (piso 5 no discrimina) y la utilidad varía sin relación con él |
| H-C1 muerte global | **NO dispara**: el RAG supera a la wiki en el total, pero la wiki GANA en olvido — falta la doble derrota en tipos 3 y 5 |

## Lectura

La confirmatoria confirma la dirección del piloto y la precisa. La wiki
anclada no compite con el RAG crudo en exactitud de pregunta-respuesta
sobre este material (R13-H1 muere), y su pérdida se concentra en
preguntas de un solo hecho y entre documentos; pero su ventaja
preregistrada en OLVIDO se confirma con n=30: cuando una fuente se olvida,
la wiki abstiene donde el RAG sigue respondiendo. La condición de muerte
global no dispara: la justificación de la wiki por su capa epistémica
—olvido controlado, trazabilidad, base de entrenamiento— sigue en pie,
mientras la justificación por exactitud se retira. Con el cierre de H-C2
(la proyección no sobrevive la regla de compensación en QA), la
arquitectura queda con sus dos pilares medidos: memoria local sostenida
(H-C1) y proyección valiosa para escritura, costosa para QA.

*Texto CC BY 4.0.*
