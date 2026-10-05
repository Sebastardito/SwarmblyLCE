---
status: current
lang: es
kind: exploratory
---

# Reporte integrado de benchmarks — Swarmbly LCE

*Generado el 2026-10-05 por `lce_validation/bench_report.py` desde los resultados guardados de cada benchmark. Ningún número de este reporte proviene de simulaciones: solo de corridas reales (benchmarks) y de la corrida confirmatoria preregistrada (C1/C2).*

## 1. Estado exploratorio agregado

| Pregunta | Evidencia | Estado exploratorio |
|---|---|---|
| H-C1 a escala: ¿la memoria local mejora al modelo del usuario? | ganancia media por pregunta **+0.477** IC95 [+0.407, +0.543] sobre 60 preguntas × 5 familias | **se sostiene (descriptivo)** |
| C1 (control positivo, preregistrado) | exactitud 0.80 con memoria vs 0.00 sin ella | **se sostiene** |
| H-C2 léxico (preregistrado) | adherencia 0.667 con Γ vs 0.033 sin Γ | **se sostiene** |
| H-C17a / H-C17b (preregistrado) | reducción de homogeneidad 0.073 supera placebo; Δ acuerdo de errores 0.039 dentro de ±0.10 | **se sostiene, con matices** |
| H-C2 ρ: ¿la proyección encarece la redundancia? | Δρ por paquete +7.8% (peor, medido); por solicitud ≈+2.6% (estimación aritmética, diseño no implementado) | **con el protocolo actual (Γ en cada paquete) la proyección añade +8 % de ρ (peor; mediana +7 %); la comparación con su ganancia (la condición de muerte real de H-C2) y el costo del diseño por-solicitud o con caché quedan pendientes** |
| H-C6 (adaptador real) | LoRA rank 8 en 36 s; adherencia bruta 0.62 vs 0.38 (brazos NO comparables) | **no concluyente (lote contaminado, brazos no comparables); factibilidad demostrada** |
| H-C11 (dirección, C9-lite) | circuito de adopción por utilidad ejercitado; identidad 1+1 es la misma respuesta dos veces | **no concluyente por diseño (sonda sin cápsulas: 1+1 es la misma respuesta dos veces; desviaciones declaradas en el script)** |

## 2. Detalle por benchmark


### 2.1 H-C1 a escala (memoria local, 5 familias × 5 usuarios)

**Cifra central.** 60 preguntas (12 por usuario: 5 factuales, 4 de léxico, 3 de procedimiento, con preguntas entre documentos), 5 familias por pregunta. Ganancia media por PREGUNTA **+0.477** con IC95 [+0.407, +0.543] (agrupado por pregunta; por celda: +0.477 [+0.417, +0.533]). Las estadísticas de la wiki por familia y usuario están guardadas en el resultado.

**Por familia:**

- `llama3.2:3b`: ganancia media +0.400 (n=60); afirmaciones ancladas por usuario 23–58 (media 40.6), tasa de anclaje 0.68–1.00
- `qwen2.5:3b`: ganancia media +0.667 (n=60); afirmaciones ancladas por usuario 30–47 (media 36.0), tasa de anclaje 1.00–1.00
- `gemma2:2b`: ganancia media +0.650 (n=60); afirmaciones ancladas por usuario 30–65 (media 43.8), tasa de anclaje 0.89–1.00
- `phi3.5:3.8b`: ganancia media +0.133 (n=60); afirmaciones ancladas por usuario 6–18 (media 11.4), tasa de anclaje 0.73–1.00
- `granite3.1-dense:2b`: ganancia media +0.533 (n=60); afirmaciones ancladas por usuario 34–48 (media 42.2), tasa de anclaje 0.57–0.81

**Por usuario:**

- `andres`: ganancia media +0.617 (n=60)
- `carmen`: ganancia media +0.483 (n=60)
- `julian`: ganancia media +0.317 (n=60)
- `luisa`: ganancia media +0.550 (n=60)
- `mara`: ganancia media +0.417 (n=60)

**Explicación.** La memoria convierte en recuperables preguntas que ningún modelo base puede responder (hechos del usuario, umbrales de su protocolo, términos preferidos). La variación entre familias mezcla dos cosas —la familia digiere Y responde— y la atribución al digestor requiere el diseño cruzado de la siguiente fase. Solo phi3.5 se separa por el tamaño de su wiki (muchas menos afirmaciones ancladas); entre las otras cuatro, ni el número de afirmaciones ancladas ni la tasa de anclaje ordenan la ganancia. Una compuerta de calidad del digestor, si se adopta, sería un piso de afirmaciones ancladas, no un umbral derivado de estos datos.

**Ajuste propuesto.** Añadir el brazo «memoria + proyección Γ», un usuario real y el diseño cruzado digestor/respuesta.

### 2.2 ρ de la proyección (camino de despacho real)

**Cifra central.** Sobre el documento de procedimientos de cada usuario (19-32 oraciones, 391-718 tokens de material), fragmentado con P9 (L=10, F=2), con el PROYECTOR real de la LCE: la proyección sube ρ **+7.0%** (mediana) y **+7.8%** (peor) con el protocolo actual (Γ replicado en cada paquete).

**Explicación.** Δρ es estructural: ≈ tamaño de Γ / tamaño de cada paquete, y no se diluye con documentos más largos.

**Qué NO concluye.** La condición de muerte real de H-C2 («muere si el aumento de ρ supera la ganancia») exige comparar este costo con la ganancia de adherencia; esa comparación y los diseños por-solicitud o con caché quedan pendientes.

**Estimación, no medición.** Si Γ se inyectara una sola vez por solicitud, la misma aritmética sobre estos conteos de tokens daría +1.1% a +2.6% (mediana +2.3%). Ese diseño no existe en el protocolo y la cifra no está medida; una caché de Γ por usuario en el nodo podría acercarla a cero, lo que es una hipótesis.

### 2.3 C9-lite social (5 nodos reales)

**Cifras.** Masa de colas post: utilidad 0.80 vs prevalencia 0.00 (la del brazo de utilidad sale del diseño: nadie conocía los términos y todos copian la glosa del contexto). Identidad: 1+1 — la sonda no recibe las cápsulas, así que es la misma respuesta dos veces. Estado: **no concluyente por diseño (sonda sin cápsulas: 1+1 es la misma respuesta dos veces; desviaciones declaradas en el script)**.

**Alcance y desviaciones.** términos canarios SIN verificar y diseño no concluyente: descriptivo del circuito de adopción, no evidencia sobre H-C11 ni sobre los términos. Dos desviaciones post-corrida están declaradas en el encabezado de `bench_social.py`.

**Ajuste propuesto.** La versión justa (siguiente fase): sonda con cápsulas en contexto, prevalencia que adopta la variante mayoritaria aunque sea errónea, utilidad juzgada por beneficio posterior, cápsulas con el conocimiento del nodo fuente, varias rondas, y el canario verificado por hablantes nativos.

### 2.4 Adaptador real (factibilidad, MLX LoRA)

**Cifras.** LoRA rank 8 entrenado en 36 s (200 iters, 13 pares) sobre Qwen2.5-3B-Instruct. Adherencia bruta: base 0.12, recuperación 0.38, adaptador 0.62. Facticidad: base 0.90 vs adaptador 0.80.

**Qué NO concluye.** La adherencia no compara brazos justos (el lote contamina las tareas; la recuperación solo recibió el documento de estilo; sin intervalo de confianza): **no concluyente (lote contaminado, brazos no comparables); factibilidad demostrada**. Los pesos no se distribuyen (licencia qwen-research del modelo base); el manifiesto con su SHA-256 y la receta están en el resultado. Reentrenar con la receta da un adaptador funcionalmente equivalente, no necesariamente idéntico bit a bit (MLX no garantiza determinismo); el manifiesto permite comprobarlo.

**Alcance.** exploratorio de FACTIBILIDAD: lote sintético de un usuario, 200 iters, Qwen2.5-3B-Instruct; la adherencia bruta no compara brazos justos (ver límites en bench_adapter.py).

**Ajuste propuesto (siguiente fase).** Tareas separadas del lote con otra redacción, lote solo de afirmaciones entrenables (I1) con ExampleBuilder, repaso y prueba nueva, ≥30 tareas con IC, y una segunda familia base de licencia permisiva.

## 3. Cierre

La LCE tiene ahora: memoria local medida a escala (F1a, con estadísticas guardadas y CI por pregunta), el costo de ρ de la proyección medido con el camino de despacho real (F1b, con el Projector real y sin umbrales inventados), el circuito social ejercitado con nodos reales (F1d, no concluyente por diseño y con sus desviaciones declaradas) y la factibilidad del adaptador en hardware de consumo (F1c, sin pesos en el repositorio). Las cifras preregistradas de la corrida 2 siguen siendo el único resultado confirmatorio.
