---
status: current
lang: es
kind: exploratory
---

# Resultados — piloto exploratorio de R13 (la pregunta decisiva de H-C1)

**9 de octubre de 2026 · preregistro `PREREGISTRATION_BENCH_R1X_ES.md` con
Enmienda 1 · corrida PILOTO EXPLORATORIA: no emite veredictos preregistrados**

**Qué dice el piloto en una línea.** La tubería de los cinco brazos funciona
de punta a punta y la rúbrica por tipo se comporta (abstención en
sin-respuesta ≈ 0.95). La comparación decisiva todavía NO es justa: los
brazos corrieron con presupuestos desiguales (A1 913 tokens, A2 206, A3 111)
y la wiki perdió frente al RAG crudo en casi todo — pero su eficiencia POR
TOKEN es igual a la del RAG (0.380 vs 0.375 por 100 tokens), lo que apunta a
la política de recuperación de la wiki, no a la representación, como el
defecto a corregir.

Modelos: digestores y respondedores qwen2.5:3b, llama3.2:3b, gemma2:2b.
Salidas crudas en `results/bench_r13/results.json` (SHA en el commit).

## 1. Cifras

Exactitud por brazo (91 preguntas × 3 respondedores; A3/A4 con cruzado):

| Brazo | Exactitud | Tokens medios |
|---|---|---|
| A0 sin memoria | 0.117 | 47 |
| A1 documento completo | **0.813** | 913 |
| A2 RAG crudo | 0.773 | 206 |
| A3 wiki | 0.454 | 111 |
| A4 wiki + Γ | 0.476 | 138 |

Por tipo de pregunta (A1 / A2 / A3):

| Tipo | A1 | A2 | A3 | Lectura |
|---|---|---|---|---|
| simple | 0.88 | 0.78 | 0.42 | la wiki pierde en hechos simples |
| cross | 0.67 | **0.80** | 0.20 | el RAG combina mejor dos fuentes |
| updated | 0.73 | **1.00** | 0.22 | el RAG es perfecto en hechos actualizados; la wiki recupera la claim antigua |
| contradiction | 0.33 | 0.20 | 0.22 | todos bajos |
| deleted | 0.53 | 0.80 | 0.56 | el RAG se abstiene más que la wiki |
| unanswerable | 0.93 | 0.93 | 0.98 | todos se abstienen bien |

Cruzado: A3 diagonal 0.458 vs A3 cruzado 0.421 — el digestor ajeno cuesta
~4 puntos; efecto pequeño, requiere la corrida confirmatoria para decidir la
compuerta del digestor.

## 2. Lectura honesta (qué prueba y qué no)

**Lo que el piloto prueba.** La tubería completa (digestión → anclaje → wiki
→ recuperación → los cinco brazos → rúbrica por tipo → contabilidad de
tokens) corre sin errores, la abstención funciona, y las diferencias entre
brazos son grandes y estables.

**Lo que NO prueba (confundidos identificados, todos corregibles antes de la
confirmatoria):**

1. **Presupuestos desiguales.** A3 recibió 111 tokens de contexto frente a
   206 (A2) y 913 (A1). El preregistro exige el mismo presupuesto; el piloto
   no lo igualó y la ordenación A1 > A2 > A3 correlaciona con el tamaño del
   contexto. La eficiencia por token (A3 0.380 ≈ A2 0.375) sugiere que a
   presupuesto igual la brecha se cierra en buena parte.
2. **La política de recuperación de la wiki es el defecto.** En `updated`, la
   wiki tiene DOS claims (la antigua y la nueva) y el BM25 sin criterio de
   vigencia recupera la antigua (0.22 vs 1.00 del RAG). La capa epistémica
   (maturidad, versionado) existe pero el piloto no la usó al recuperar.
   Corrección: recuperación con preferencia por la claim más reciente o de
   mayor madurez, y presupuesto igualado al RAG.
3. **A4 (wiki+Γ) empeora los tipos factuales** (updated 0.20, contradiction
   0.13) — consistente con el costo de exactitud de Γ medido en la corrida 2;
   con el presupuesto igualado y la recuperación corregida se re-mide.

## 3. Consecuencia para el plan

El piloto NO dispara la condición de muerte (es exploratorio y con
presupuestos desiguales), pero deja claro que la confirmatoria sin las dos
correcciones la dispararía por la razón equivocada. La Enmienda 2 congela:
(a) presupuesto de contexto igual para todos los brazos (200 tokens, el del
RAG del piloto); (b) recuperación de la wiki con preferencia de vigencia
(claim más reciente del mismo hecho primero, luego madurez); (c) re-piloto
rápido con las wikis ya cacheadas antes de la confirmatoria de ≥250.

*Texto CC BY 4.0.*
