---
status: current
lang: es
---

# Preregistro consolidado — benchmarks R14, R13 y R11 de la Swarmbly LCE

**5 de octubre de 2026 · escrito ANTES de cualquier corrida real de estos benchmarks**

Este documento congela los diseños de las tres fases siguientes del plan de
validación de la LCE, con sus hipótesis, rúbricas, márgenes, presupuestos y
condiciones de rechazo, antes de que exista un solo dato. Se refiere al
whitepaper LCE v0.1 (secciones 11.1–11.5) y a los resultados ya publicados
(corrida confirmatoria 2; benchmarks exploratorios F1a–F1d con su alcance
declarado). Todo cambio posterior se registra como enmienda numerada en la
sección 7; un cambio silencioso no cuenta.

**Qué cubre:** R14 (reproducibilidad — el entorno que todo lo demás usa),
R13 (la pregunta decisiva de H-C1: ¿una wiki anclada supera a una memoria
simple?), R11 (el adaptador justo: H-C6, H-C10 y el olvido por regeneración),
y el cierre de H-C2 (ρ frente a su ganancia), plegado en R13. **R12 (plano
social) se preregistra por separado** cuando el conjunto canario esté
verificado por hablantes nativos, porque su bloqueante es de calendario, no
de cómputo.

English: `PREREGISTRATION_BENCH_R1X_EN.md`.

---

## 1. R14 — Reproducibilidad (se aplica a todo lo demás)

### 1.1 Entorno fijado

1. El repositorio congelará un archivo de bloqueo de dependencias con las
   versiones exactas y la versión de Python (3.11).
2. Los digests de los modelos de Ollama (las cinco familias y
   `nomic-embed-text`) pasan de ser registrados a ser una COMPROBACIÓN: la
   corrida se DETIENE si un modelo no coincide con el preregistrado, y el
   rechazo se registra como fallo de infraestructura, no como resultado.

### 1.2 Muestreo

1. **Temperatura 0** para toda medida que no dependa de la diversidad:
   preguntas de opción múltiple, respuestas de H-C1 y R13, adherencia de
   léxico, sondas de identidad.
2. Para las medidas que SÍ dependen de la diversidad (homogeneidad entre
   usuarios), se guardan las muestras crudas y el análisis no asume
   apareamiento por semilla (bootstrap por tema, como en la corrida 2).
3. La adopción de un servidor con semilla efectiva (candidato: llama.cpp)
   requiere antes un **test A/A preregistrado**: la diferencia media entre
   dos corridas idénticas debe ser ≤ 0.01 en las medidas estocásticas. Solo
   si pasa se adopta, y se registra como enmienda.

### 1.3 Regeneración y anclaje de cifras

1. Un solo comando (`python -m lce_validation.run_derive`, a construir)
   regenera TODAS las tablas de los documentos RESULTS desde las salidas
   crudas guardadas, sin modelos, y termina con código distinto de cero si
   una cifra no coincide.
2. Los bloques de cifras de los documentos RESULTS pasan a ser GENERADOS
   desde el JSON (nunca editados a mano), y una prueba de CI compara cada
   cifra publicada con su JSON (patrón de `test_published_figures_recompute`
   de Swarmbly).
3. Un ayudante `provenance()` común registra en cada benchmark: versión de
   Ollama, digests de modelos, commit de git y SHA-256 de este preregistro.
4. **Criterio de cierre de R14:** un clon nuevo reproduce las tablas byte a
   byte desde las salidas crudas; al re-ejecutar, los brazos deterministas
   salen idénticos y los estocásticos quedan dentro del ruido A/A (±0.01).

### 1.4 Publicación

Release v0.1.1 en GitHub y depósito en Zenodo (DOI de software), con las
salidas crudas incluidas y el preregistro citado.

---

## 2. R13 — H-C1 decisivo: ¿la wiki anclada supera a una memoria simple?

### 2.1 La pregunta

«¿La memoria ayuda?» ya está respondida (F1a: +0.477 por pregunta, IC95
[+0.407, +0.543]). La pregunta nueva es: **¿una wiki anclada, tipada y
versionada supera a las alternativas simples —documento completo en el
contexto y RAG de fragmentos crudos—, y en qué tipos de pregunta?**

### 2.2 Brazos (misma presupuesto de tokens T por pregunta; T se reporta)

| Brazo | Qué recibe el modelo que responde |
|---|---|
| A0 — sin memoria | solo la pregunta |
| A1 — documento completo | las fuentes del usuario completas, truncadas al presupuesto |
| A2 — RAG crudo | los k fragmentos más cercanos por embeddings (mismos embeddings que la wiki) |
| A3 — wiki LCE | claims ancladas recuperadas de la wiki (BM25), con su tipo y madurez |
| A4 — wiki + Γ | A3 más la proyección en el contrato (el producto completo de la LCE) |

Los tokens enviados se reportan por brazo y por pregunta: son exposición y ρ.

### 2.3 Tipos de pregunta (fijados antes de correr)

1. **Hecho simple** — una clave en una fuente.
2. **Entre documentos** — la respuesta exige combinar dos fuentes.
3. **Hecho actualizado** — una fuente nueva corrige a una antigua; correcto
   = el valor vigente.
4. **Contradicción** — dos fuentes vigentes discrepan; correcto = la versión
   vigente o señalar explícitamente el desacuerdo.
5. **Fuente borrada** — el usuario olvidó la fuente; correcto = ABSTENERSE
   (responder con el hecho borrado = error, peor que equivocarse).
6. **Sin respuesta en memoria** — la pregunta no tiene respuesta en las
   fuentes; correcto = ABSTENERSE.

Rúbrica por tipo en la tabla 2.3-R (parte normativa de este documento):

| Tipo | Correcto | Incorrecto |
|---|---|---|
| 1, 2 | clave de oro presente | ausente o errónea |
| 3 | valor vigente | valor antiguo |
| 4 | versión vigente O desacuerdo señalado | versión antigua sin señalarlo |
| 5, 6 | abstención (o «no está en mis fuentes») | cualquier respuesta con contenido |

### 2.4 Datos

1. **Usuarios propios congelados**: los cinco usuarios del corpus del
   benchmark (SHA congelado), extendidos con una versión 2 por usuario que
   añade: una fuente actualizada, una contradicción, una fuente borrada y
   una pregunta sin respuesta. El generador se congela en el commit de datos.
2. **Subconjunto público**: LongMemEval o LoCoMo, elegido tras verificar su
   licencia; la elección, el SHA-256 del subconjunto y su licencia se fijan
   en la Enmienda 1, antes de correr. Sirve para responder a la crítica de
   que los usuarios sintéticos los escribe el autor.

### 2.5 Diseño cruzado

- **3 digestores** × **3 respondedores** (qwen2.5:3b, llama3.2:3b, gemma2:2b
  — las tres familias con mayor ganancia en F1a) para el brazo A3: separa la
  calidad del digestor de la capacidad de responder y decide la compuerta
  del digestor con datos, no con correlaciones confundidas.
- Los brazos A0–A2 usan los 3 respondedores. A4 usa el cruzado de A3 más Γ.

### 2.6 Tamaño y estadística

- **≥250 preguntas emparejadas** (todas las preguntas pasan por todos los
  brazos), con **≥30 por tipo** para intervalos por tipo.
- Estadístico primario: diferencia emparejada **A3 − A2** (wiki − RAG crudo)
  por pregunta, con bootstrap agrupado por pregunta (10.000 remuestreos,
  semilla 20261005). Secundarios: A3 − A1, A4 − A3, y el desglose por tipo.
- Potencia declarada: con pares discordantes ≈ 30 %, n = 250 detecta una
  diferencia de 0.10 con margen holgado.

### 2.7 Reglas de decisión

| Hipótesis | Se sostiene | Muere | Si no |
|---|---|---|---|
| R13-H1: la wiki supera al RAG crudo | CI95 de A3−A2 > 0 en el total | estimación puntual ≤ 0 | no concluyente |
| R13-H2: la wiki gana en actualización y olvido | CI95 > 0 en los tipos 3 y 5 | punto ≤ 0 en ambos | no concluyente |
| R13-H3 (compuerta del digestor): un piso de claims ancladas explica la utilidad | la utilidad cae bajo el piso propuesto en el cruzado | sin relación monotónica incluso en el cruzado | la compuerta se retira como regla |
| H-C1 muerte global | — | RAG crudo ≥ wiki en el total Y la wiki no gana en 3 ni 5 | el diseño se simplifica (resultado publicable) |

### 2.8 C2-bis (misma corrida)

Placebo igualado en CANTIDAD de instrucción (no solo en forma) y ≥5 usuarios
que difieren en ≥2 rasgos. H-C17a se sostiene si la reducción de homogeneidad
por proyección supera al placebo con CI95 > 0. Cierra el matiz principal de
la corrida 2.

### 2.9 Cierre de H-C2: ρ frente a su ganancia (misma corrida)

Con las wikis digeridas en R13 y el camino de despacho de Swarmbly
(planificador + packer reales, ruta parametrizable), se mide por tarea el par
**(ganancia de adherencia con Γ, Δρ)**. Regla de compensación preregistrada:
**la proyección sobrevive si la fracción de tareas con ganancia > 0 Y
Δρ ≤ 10 % es ≥ 0.8**; se reporta el diagrama completo por tarea. Sin
umbrales adicionales.

### 2.10 Rechazos

Se niega si: un modelo no coincide con su digest; menos de 3 respondedores
responden; alguna wiki tiene < 5 claims ancladas; hay < 200 preguntas
analizables; más del 10 % de las respuestas no se pueden calificar.

---

## 3. R11 — El adaptador justo (H-C6, H-C10, LC6)

Corre DESPUÉS de R13: el lote sale de las afirmaciones entrenables de una
wiki ya validada.

### 3.1 Lote y tareas

1. El lote se construye SOLO con `ExampleBuilder` a partir de afirmaciones
   TRAINABLE (preferencia, estilo, procedimiento) — nunca hechos (I1) — y con
   repaso entremezclado.
2. Las tareas de prueba están redactadas de otra forma y no se cruzan con el
   lote: **≥30 por usuario × 3 usuarios** (los tres primeros del corpus), con
   intervalo de confianza.
3. El sub-brazo **sin repaso** (H-C10) entrena el mismo lote sin los
   ejemplos de repaso: una configuración extra por adaptador.

### 3.2 Familias base y semillas

- Dos familias: **qwen2.5-3b** (pesos no distribuidos; licencia
  qwen-research) y **granite-3.1-2b** (Apache-2.0; verificar antes de
  congelar — enmienda).
- **2 semillas de entrenamiento** por adaptador; la tercera se corre solo si
  las dos primeras discrepan en más de 0.05 (MLX no es determinista; la
  varianza entre semillas se reporta).
- Presupuesto declarado: 2 familias × 3 usuarios × 2 semillas × 2 (repaso)
  = **24 entrenamientos** de ≤ 500 iteraciones.

### 3.3 Brazos (misma información por brazo)

base · recuperación + Γ (BM25 sobre la wiki completa del usuario) ·
adaptador · adaptador + recuperación.

### 3.4 Reglas de decisión

| Hipótesis | Se sostiene | Muere |
|---|---|---|
| H-C6 | la diferencia adaptador − recuperación tiene cota inferior del IC > 0 y media ≥ +0.10 en ≥2 de 3 usuarios | cota ≤ 0 en 2 de 3 → la capa 2 se retira (condición de muerte del roadmap) |
| H-C10 (repaso) | el brazo sin repaso olvida ANTES el material consolidado que el brazo con repaso (punto de cruce posterior con repaso) | sin diferencia → la homología CLS vuelve a vocabulario |
| LC6 (olvido) | tras `forget` de una fuente y regeneración, el hecho olvidado vuelve al nivel del base (equivalencia ±0.10) y la adherencia de estilo persiste | el hecho persiste en el adaptador → «olvido verificable» se retira |
| I1 (fuga) | SIN recuperación, el adaptador no responde hechos del usuario mejor que el base (equivalencia ±0.10) | el adaptador supera al base en hechos → I1 violada y el lote se reconstruye |

### 3.5 Opción pública

Un subconjunto de LaMP (el benchmark de personalización de OPPU [5]) si su
licencia lo permite y sus temas no se solapan con las wikis; se fija por
enmienda con SHA. Hace el resultado comparable con la literatura.

### 3.6 Instrumentos que se prueban en simulación ANTES de medir

El calificador de abstención (tipos 5–6 de R13), el calificador de
contradicción (tipo 4), el procedimiento de equivalencia de I1/LC6 (debe
detectar una fuga inyectada), el test A/A del muestreador, y el anclaje de
cifras generadas (1.3.2). Ninguno decide nada antes de pasar su simulación.

---

## 4. Qué NO cubre este preregistro

R12 (plano social) — requiere el canario verificado; se preregistra aparte.
La selección del subconjunto público (R13) y de la segunda familia base
(R11) — pendientes de licencia; entran por enmienda antes de correr. El
juicio de modelos sobre la calidad de redacción queda fuera: la calificación
es determinista cuando el oro lo permite, y un juez LLM solo se usará como
medida secundaria con auditoría humana de una muestra, y con una familia
distinta de las respondedoras.

---

## 5. Orden de ejecución

R14 (entorno y regeneración) → R13 (corrida decisiva + C2-bis + ρ) → R11
(adaptador, con los lotes de las wikis de R13) → R12 (aparte). Cada corrida
confirmatoria exige el árbol limpio, los digests verificados y este
preregistro confirmado, como en la corrida 2.

---

## 6. Referencias

[W] Whitepaper LCE v0.1, secciones 11.1–11.5. [5] Tan et al. 2024 (OPPU).
[LaMP] Salemi et al. 2024. [LongMemEval / LoCoMo] a confirmar con licencia
(enmienda). [Swarmbly] whitepaper v2, secciones 5 y 15, para la ruta de
despacho y la definición de ρ.

---

## 7. Enmiendas

**Enmienda 1 — 9 de octubre de 2026, antes de correr.** La primera corrida de
R13 es un PILOTO EXPLORATORIO sobre los usuarios propios v1+v2 (91 preguntas:
60 de F1a + 31 etiquetadas por tipo), con los cinco brazos, el cruzado 3×3 y
la rúbrica por tipo. No emite veredictos preregistrados: su función es
validar la tubería y calibrar costos. La corrida CONFIRMATORIA de ≥250
preguntas queda condicionada a las enmiendas 2 (corpus ampliado a ≥30 por
tipo, con SHA) y 3 (subconjunto público con licencia verificada — LongMemEval
es MIT y es el candidato; LoCoMo tiene términos propios sin licencia estándar
y queda descartada salvo revisión legal). El presupuesto de tokens del brazo
A1 (documento completo) se fija en 2.400 palabras truncadas para el piloto y
se reporta por pregunta. Cualquier cambio se registra aquí con fecha y razón antes
de correr; un cambio silencioso no cuenta.*

**Enmienda 2 — 9 de octubre de 2026, después del piloto y antes del
re-piloto.** El piloto identificó dos confundidos; se corrigen así:
(a) presupuesto de contexto IGUAL para todos los brazos: 200 tokens (el del
RAG del piloto), incluido A1 que se trunca a las primeras 200 palabras;
(b) recuperación de la wiki POR VIGENCIA: entre las 10 claims más cercanas
por BM25 se ordena por la fecha explícita más tardía de su fuente (las
fuentes con fecha van antes de las que no la tienen), luego por madurez y
luego por score. El re-piloto re-corre solo los brazos A1, A3 y A4 (A0 y A2
no cambian y sus celdas se heredan del piloto) con las wikis ya cacheadas.
La Enmienda 3 (subconjunto público) sigue pendiente antes de la
confirmatoria.

**Enmienda 3 — 9 de octubre de 2026, después del re-piloto y antes del
re-piloto de verificación.** El re-piloto (Enmienda 2) midió A3−A2 = −0.322
a presupuesto igual y localizó dos defectos de implementación y un régimen
ausente. Se reparan antes de juzgar: (a) ATOMICIDAD — el digestor procesa
sub-pasajes de 3 oraciones y el prompt prohíbe fundir hechos de oraciones
distintas (el piloto midió una claim con ambos valores de una actualización,
contra el principio atómico del propio whitepaper); (b) RECUPERACIÓN POR
HECHO — entre las claims recuperadas, si una claim fechada comparte ≥2
palabras de contenido con otra, la anterior se descarta (la actualización
sustituye a la antigua); (c) CORPUS LARGO — cada usuario gana un documento
de 193–408 palabras con 7 preguntas cuyas respuestas están más allá del
presupuesto de 200 palabras de A1 (el régimen donde la compresión puede
pagar; los documentos multi-mil palabras entran en la ampliación de la
confirmatoria). El re-piloto de verificación re-digiere las wikis (el
digestor cambió) y re-corre los cinco brazos sobre las 126 preguntas.

**Enmienda 4 — 9 de octubre de 2026, después del re-piloto de
verificación y antes de la re-medición limpia.** Se encontró CONTAMINACIÓN
de fuentes: el espacio de fuentes escaneaba todo el directorio del usuario e
ingirió los archivos de preguntas del benchmark (`questions*.json`, con sus
claves de oro) como fuentes de la wiki — la wiki contenía respuestas
filtradas y la comparación no era limpia. Se corrige: las fuentes del
usuario son SOLO documentos `.md` (`build_wiki(suffixes={".md"})`). La
misma contaminación afecta al benchmark F1a (mismo `build_wiki`): su cifra
central (+0.477) queda SUPERSEDIDA hasta la re-medición limpia, que se
relanza junto con el re-piloto de R13. `bench_rho` usó las mismas wikis pero
mide TAMAÑO de proyección (aritmética), no contenido: su veredicto se
mantiene y se re-ejecuta por limpieza. Además: la abstención de los brazos
de wiki exige ahora que el contexto contenga la respuesta EXACTA (apunta al
tipo `deleted`, donde la wiki respondía con la claim vigente relacionada).

**Enmienda 5 — 9 de octubre de 2026, antes del piloto R11.** La segunda
familia base es granite-3.1-2b-instruct, licencia **Apache-2.0** (verificada
en la ficha del modelo). LC6 (olvido por regeneración) se difiere a la
confirmatoria de R11: requiere el flujo de olvido completo (`forget` +
regeneración) y se declara aquí en lugar de improvisarlo. El piloto R11
cubre H-C6 (cuatro brazos), H-C10 (repaso sí/no) y la prueba de fuga I1
(equivalencia ±0.10, instrumento probado en simulación).

*Texto CC BY 4.0; código AGPL-3.0-or-later.*
