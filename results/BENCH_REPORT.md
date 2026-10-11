---
status: current
lang: es
kind: exploratory
---

# Reporte integrado de benchmarks — Swarmbly LCE

*Generado por `lce_validation/bench_report.py` desde los resultados guardados de cada benchmark (regenerable byte a byte con `run_derive`). Ningún número de este reporte proviene de simulaciones: solo de corridas reales (benchmarks) y de la corrida confirmatoria preregistrada (C1/C2).*

## 1. Estado exploratorio agregado

| Pregunta | Evidencia | Estado exploratorio |
|---|---|---|
| H-C1 a escala: ¿la memoria local mejora al modelo del usuario? | ganancia media por pregunta **+0.500** IC95 [+0.420, +0.578] sobre 60 preguntas × 5 familias | **se sostiene (descriptivo)** |
| C1 (control positivo, preregistrado) | exactitud 0.80 con memoria vs 0.00 sin ella | **se sostiene** |
| H-C2 léxico (preregistrado) | adherencia 0.667 con Γ vs 0.033 sin Γ | **se sostiene** |
| H-C17a / H-C17b (preregistrado) | reducción de homogeneidad 0.073 supera placebo; Δ acuerdo de errores 0.039 dentro de ±0.10 | **se sostiene, con matices** |
| H-C2 ρ: ¿la proyección encarece la redundancia? | Δρ por paquete +7.8% (peor, medido); por solicitud ≈+2.6% (estimación aritmética, diseño no implementado) | **con el protocolo actual (Γ en cada paquete) la proyección añade +8–8 % de ρ (mediana +7 %); la comparación con su ganancia (la condición de muerte real de H-C2) y el costo del diseño por-solicitud o con caché quedan pendientes** |
| H-C6 (adaptador real) | LoRA rank 8 en 36 s; adherencia bruta 0.62 vs 0.38 (brazos NO comparables) | **no concluyente (lote contaminado, brazos no comparables); factibilidad demostrada** |
| H-C11 (dirección, C9-lite) | circuito de adopción por utilidad ejercitado; identidad 1+1 es la misma respuesta dos veces | **señal insuficiente (violaciones totales < 5)** |
| R13 (piloto): ¿la wiki anclada supera a un RAG crudo? | A3 − A2 = **−0.256** [−0.317, −0.194] sobre 126 preguntas, tres digestores × tres respondedores | **el RAG crudo gana en exactitud; la pérdida está en la cobertura de la digestión** |
| R11 (piloto): adaptador justo | conclusiones retiradas (E6: adaptador colapsado, tareas inválidas, sin Γ en el brazo de recuperación) | **sin evidencia; rediseño en la siguiente fase** |
| R12 (exploratorio): plano social | 0/40 por construcción; utilidad implementada como novedad; sin F_ST (E7) | **compatible con la I4, no la mide** |
| C2-bis: ¿la Γ reduce homogeneidad más que un placebo igualado? | reducción Γ − placebo **+0.065** [+0.056, +0.074] (100 celdas) | **se sostiene** |
| Cierre H-C2: ¿la proyección paga su ρ en QA? | ganancia media +0.016; Δρ mediana 41 %; fracción (ganancia>0 y Δρ≤10 %) 0.00 | **la proyección NO sobrevive (regla de compensación)** |
| R11 confirmatoria: adaptador justo vs recuperación+Γ | adaptador − base = +0.000 (n=720, inerte); H-C6: 0/3 usuarios (−0.52 a −0.63); I1 +0.000 | **la capa 2 se retira** |

## 2. Detalle por benchmark


### 2.1 H-C1 a escala (memoria local, 5 familias × 5 usuarios)

**Cifra central.** 60 preguntas (12 por usuario: 5 factuales, 4 de léxico, 3 de procedimiento, con preguntas entre documentos), 5 familias por pregunta. Ganancia media por PREGUNTA **+0.500** con IC95 [+0.420, +0.578] (agrupado por pregunta; por celda: +0.500 [+0.439, +0.561]). Las estadísticas de la wiki por familia y usuario están guardadas en el resultado.

**Por familia:**

- `llama3.2:3b`: ganancia media +0.317 (n=60); afirmaciones ancladas por usuario 24–47 (media 36.2), tasa de anclaje 0.90–1.00
- `qwen2.5:3b`: ganancia media +0.700 (n=60); afirmaciones ancladas por usuario 47–64 (media 54.6), tasa de anclaje 0.98–1.00
- `gemma2:2b`: ganancia media +0.717 (n=60); afirmaciones ancladas por usuario 53–84 (media 63.8), tasa de anclaje 0.98–1.00
- `phi3.5:3.8b`: ganancia media +0.083 (n=24); afirmaciones ancladas por usuario 7–8 (media 7.5), tasa de anclaje 1.00–1.00
- `granite3.1-dense:2b`: ganancia media +0.433 (n=60); afirmaciones ancladas por usuario 30–44 (media 38.4), tasa de anclaje 0.58–0.85

**Por usuario:**

- `andres`: ganancia media +0.533 (n=60)
- `carmen`: ganancia media +0.500 (n=48)
- `julian`: ganancia media +0.417 (n=48)
- `luisa`: ganancia media +0.583 (n=48)
- `mara`: ganancia media +0.467 (n=60)

**Explicación.** La memoria convierte en recuperables preguntas que ningún modelo base puede responder (hechos del usuario, umbrales de su protocolo, términos preferidos). La variación entre familias mezcla dos cosas —la familia digiere Y responde— y la atribución al digestor requiere el diseño cruzado de la siguiente fase. Solo phi3.5 se separa por el tamaño de su wiki (muchas menos afirmaciones ancladas); entre las otras cuatro, ni el número de afirmaciones ancladas ni la tasa de anclaje ordenan la ganancia. Una compuerta de calidad del digestor, si se adopta, sería un piso de afirmaciones ancladas, no un umbral derivado de estos datos.

**Ajuste propuesto.** Añadir el brazo «memoria + proyección Γ», un usuario real y el diseño cruzado digestor/respuesta.

### 2.2 ρ de la proyección (camino de despacho real)

**Cifra central.** Sobre el documento de procedimientos de cada usuario (19-32 oraciones, 391-718 tokens de material), fragmentado con P9 (L=10, F=2), con el PROYECTOR real de la LCE: la proyección sube ρ **+7.0%** (mediana) y **+7.8%** (peor) con el protocolo actual (Γ replicado en cada paquete).

**Explicación.** Δρ es estructural: ≈ tamaño de Γ / tamaño de cada paquete, y no se diluye con documentos más largos.

**Qué NO concluye.** La condición de muerte real de H-C2 («muere si el aumento de ρ supera la ganancia») exige comparar este costo con la ganancia de adherencia; esa comparación y los diseños por-solicitud o con caché quedan pendientes.

**Estimación, no medición.** Si Γ se inyectara una sola vez por solicitud, la misma aritmética sobre estos conteos de tokens daría +1.5% a +2.6% (mediana +2.3%). Ese diseño no existe en el protocolo y la cifra no está medida; una caché de Γ por usuario en el nodo podría acercarla a cero, lo que es una hipótesis.

### 2.3 C9-lite social (5 nodos reales)

**Cifras.** Masa de colas post: utilidad 0.00 vs prevalencia 0.00 (la del brazo de utilidad sale del diseño: nadie conocía los términos y todos copian la glosa del contexto). Identidad: 2+2 — la sonda no recibe las cápsulas, así que es la misma respuesta dos veces. Estado: **señal insuficiente (violaciones totales < 5)**.

**Alcance y desviaciones.** términos canarios SIN verificar: descriptivo del mecanismo, no evidencia sobre los términos. Dos desviaciones post-corrida están declaradas en el encabezado de `bench_social.py`.

**Ajuste propuesto.** La versión justa (siguiente fase): sonda con cápsulas en contexto, prevalencia que adopta la variante mayoritaria aunque sea errónea, utilidad juzgada por beneficio posterior, cápsulas con el conocimiento del nodo fuente, varias rondas, y el canario verificado por hablantes nativos.

### 2.4 Adaptador real (factibilidad, MLX LoRA)

**Cifras.** LoRA rank 8 entrenado en 36 s (200 iters, 13 pares) sobre Qwen2.5-3B-Instruct. Adherencia bruta: base 0.12, recuperación 0.38, adaptador 0.62. Facticidad: base 0.90 vs adaptador 0.80.

**Qué NO concluye.** La adherencia no compara brazos justos (el lote contamina las tareas; la recuperación solo recibió el documento de estilo; sin intervalo de confianza): **no concluyente (lote contaminado, brazos no comparables); factibilidad demostrada**. Los pesos no se distribuyen (licencia qwen-research del modelo base); el manifiesto con su SHA-256 y la receta están en el resultado. Reentrenar con la receta da un adaptador funcionalmente equivalente, no necesariamente idéntico bit a bit (MLX no garantiza determinismo); el manifiesto permite comprobarlo.

**Alcance.** exploratorio de FACTIBILIDAD: lote sintético de un usuario, 200 iters, Qwen2.5-3B-Instruct; la adherencia bruta no compara brazos justos (ver límites en bench_adapter.py).

**Ajuste propuesto (siguiente fase).** Tareas separadas del lote con otra redacción, lote solo de afirmaciones entrenables (I1) con ExampleBuilder, repaso y prueba nueva, ≥30 tareas con IC, y una segunda familia base de licencia permisiva.

### 2.5 R13 (piloto exploratorio, cifras vigentes)

**Cifra central.** A3 − A2 = **−0.256** [−0.317, −0.194] por pregunta (126 preguntas; bootstrap agrupado por pregunta). Por digestor: `qwen2.5:3b` −0.212 [−0.288, −0.138]; `llama3.2:3b` −0.442 [−0.529, −0.354]; `gemma2:2b` −0.114 [−0.183, −0.045].

**Por tipo:** `simple` −0.257 [−0.329, −0.186] (n=83); `cross` −0.508 [−0.603, −0.405] (n=14); `updated` −0.341 [−0.563, −0.135] (n=14); `contradiction` −0.044 [−0.400, +0.267] (n=5); `deleted` +0.156 [−0.067, +0.378] (n=5); `unanswerable` +0.089 [−0.067, +0.333] (n=5).

**Memoria frente a nada (preguntas con respuesta):** A3 − A0 = +0.479 [+0.420, +0.537]; A2 − A0 = +0.767 [+0.704, +0.828].

**Dónde pierde la wiki.** Clave presente en el contexto (preguntas con respuesta): A2 0.983; A3|qwen2.5:3b 0.810; A3|llama3.2:3b 0.345; A3|gemma2:2b 0.836. La diferencia está en la cobertura de la digestión.

**Qué NO concluye.** `deleted` no mide olvido (ningún brazo vio la fuente borrada) y la abstención premia al brazo que recupera menos; la prueba de olvido real es F-forget (Enmienda 6). Sin las tres claves superadas (N1): −0.260 [−0.323, −0.198].

### 2.6 F-forget (olvido real, Enmienda 6 c)

**Estructura.** Tres wikis por celda (W_full con todas las fuentes, W_forget tras `forget_source` de `borrada.md`, W_never digerida sin ella). Residuo S2 = 0 y daño colateral S3 = 0 en las celdas válidas y en los 116 olvidos del barrido; 0 celdas rechazadas por S1 (la wiki no tenía claims de esa fuente). S2 y S3 verifican la implementación sobre wikis reales: `forget_source` borra por anclaje, así que cero es lo esperado. **Veredicto estructural: se sostiene.**

**Equivalencia con no haber digerido nunca.** W_forget coincide con la W_never de la misma corrida en 8/15 wikis, pero con la wiki de R13 digerida sin la fuente en otra corrida en 0/15; las diferencias vienen de la W_never de esta corrida (0/15 frente a R13), es decir, del no determinismo de la digestión que mide AA2, no del olvido (análisis posterior a los datos).

**Conducta (sin las celdas rechazadas, como pide el preregistro).** Abstención en las 5 preguntas sobre la fuente borrada: W_full 0.289, W_forget 0.778, W_never 0.756; forget − full = +0.489 [+0.333, +0.644], forget − never = +0.022. B1 y B2 se cumplen. Son 5 preguntas: la potencia es baja y el resultado es de mecanismo.

### 2.7 A/A de reproducibilidad (R14, Enmienda 6 c)

AA1 generación a T = 0: 98.4 % de 369 respuestas idénticas, Δ exactitud +0.0027 (falla). AA2 digestión: 8/15 wikis idénticas, Jaccard medio 0.961 (falla). AA3 semilla a T = 0.7: endpoint nativo 100 % idénticas, compatible con OpenAI 80 %. AA4 homogeneidad: Δ −0.001 [−0.007, +0.005] (pasa).

**El criterio de re-corrida de R14 NO queda cerrado:** la generación es reproducible, la digestión no siempre. Cerrarlo requiere una digestión determinista (endpoint nativo con semilla, que AA3 muestra efectivo, o canonicalización de claims), por enmienda.

## 3. Cierre

La LCE tiene ahora: memoria local medida a escala con fuentes limpias (F1a) y en el piloto R13 (A3 − A0 y A2 − A0), la comparación de la wiki con un RAG crudo (R13: el RAG gana en exactitud; la pérdida está en la cobertura de la digestión), el olvido de una fuente verificado en estructura y en conducta (F-forget), la generación reproducible a temperatura 0 pero no siempre la digestión (A/A), el costo de ρ de la proyección medido con el camino de despacho real (F1b) y la factibilidad del adaptador en hardware de consumo (F1c). R11 y R12 no aportan evidencia todavía (E6, E7). Las cifras preregistradas de la corrida 2 siguen siendo el único resultado confirmatorio.


### 2.8 C2-bis (placebo igualado en instrucción, H-C17a)

5 usuarios x 20 temas x 3 semillas, escritura nativa determinista, Γ completa (21-45 tokens) y placebo de la MISMA cantidad de tokens. Reducción Γ − placebo = **+0.065** [+0.056, +0.074] (100 celdas usuario×tema). **se sostiene.**


### 2.9 Cierre H-C2 (ρ frente a ganancia, preregistro 2.9)

251 tareas de la confirmatoria: ganancia media +0.016, Δρ mediana 41 %, fracción (ganancia > 0 y Δρ ≤ 10 %) 0.00. **la proyección NO sobrevive (regla de compensación).**
