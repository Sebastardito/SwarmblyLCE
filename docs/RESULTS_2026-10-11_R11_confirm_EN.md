---
status: current
lang: en
kind: confirmatory
---

# Results — R11 CONFIRMATORY (the fair adapter)

**11 de octubre de 2026 · preregistro sec. 3 con Enmiendas 9 y 13 ·
confirmatoria: 26 entrenamientos (2 familias x 3 usuarios x 2 semillas x 2
repasos x 2 presupuestos + 2 de LC6), evaluación de CUATRO brazos sobre 30
tareas válidas por usuario, prueba de fuga I1 con hechos del usuario y curva
H-C10**

## Cifras (presupuesto completo, media por usuario)

| User | base | recuperación + Γ | adaptador | adaptador + retr + Γ |
|---|---|---|---|---|
| mara | 0.050 | 0.617 | 0.050 | 0.617 |
| julian | 0.133 | 0.650 | 0.133 | 0.650 |
| carmen | 0.000 | 0.633 | 0.000 | 0.633 |

**H-C6 (adaptador − recuperación+Γ):** carmen −0.633 [−0.696, −0.571],
julian −0.517 [−0.588, −0.446], mara −0.567 [−0.637, −0.492] — las tres
cotas bajo cero. **0/3 usuarios cumplen el margen.**

**Adaptador − base: +0.000 [+0.000, +0.000] (n=720)** — el adaptador justo
(lote canónico de claims entrenables, 2 épocas) es INERTE: sin colapso (el
defecto del piloto) pero sin ningún efecto medible de conducta.

**I1 (fuga de hechos del usuario): adaptador − base = +0.000** —
equivalencia perfecta dentro de ±0.10: el adaptador no filtra hechos.

**LC6:** base 0.026 = adaptador-sin-estilo 0.026 — no hay conocimiento de
estilo que olvidar en un adaptador inerte.

**H-C10:** +0.000 en ambos presupuestos con y sin repaso — sin curva de
olvido porque no hay conducta aprendida que retener.

## Verdict

La regla de muerte preregistrada dispara: **el adaptador no supera a la
recuperación por el margen preregistrado — la capa 2 se RETIRA.** La
recuperación+Γ (0.62–0.65) transporta toda la conducta del usuario; el
fine-tuning de comportamiento sobre lotes pequeños y fieles a I1 no aporta
nada medible en este régimen. Memoria local y proyección quedan intactas:
el diseño se simplifica en una capa, con un negativo publicable y limpio.

*Texto CC BY 4.0.*
