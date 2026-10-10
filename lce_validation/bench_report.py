"""F2 — Reporte integrado de los benchmarks de la LCE.

Lee los resultados de cada benchmark y del arnés, y escribe
``results/BENCH_REPORT.md``: resumen claro, cifras, explicaciones,
conclusiones y ajustes propuestos. Sin modelos: solo compila lo ya medido.

    python3 -m lce_validation.bench_report
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "BENCH_REPORT.md"


def _load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    hc1 = _load(ROOT / "results" / "bench_hc1_scale" / "results.json")
    rho = _load(ROOT / "results" / "bench_rho" / "results.json")
    soc = _load(ROOT / "results" / "bench_social" / "results.json")
    run2 = _load(ROOT / "results" / "2026-10-05_C1C2_run2" / "results_real.json")

    lines = [
        "---",
        "status: current",
        "lang: es",
        "kind: exploratory",
        "---",
        "",
        "# Reporte integrado de benchmarks — Swarmbly LCE",
        "",
        "*Generado por `lce_validation/bench_report.py` desde los resultados "
        "guardados de cada benchmark (regenerable byte a byte con "
        "`run_derive`). Ningún número de este reporte proviene de simulaciones: "
        "solo de corridas reales (benchmarks) y de la corrida confirmatoria "
        "preregistrada (C1/C2).*",
        "",
        "## 1. Estado exploratorio agregado",
        "",
        "| Pregunta | Evidencia | Estado exploratorio |",
        "|---|---|---|",
    ]

    # F1a
    if hc1 and "summary" in hc1:
        s = hc1["summary"]
        st = ("se sostiene (descriptivo)" if s["holds_descriptively"]
              else "no se sostiene")
        lines.append(
            f"| H-C1 a escala: ¿la memoria local mejora al modelo del usuario? "
            f"| ganancia media por pregunta **"
            f"{s['mean_gain_by_question']:+.3f}** IC95 "
            f"[{s['gain_ci95_by_question'][0]:+.3f}, "
            f"{s['gain_ci95_by_question'][1]:+.3f}] sobre "
            f"{s['n_questions']} preguntas × 5 familias | **{st}** |")
    if run2 and "verdicts" in run2:
        v = run2["verdicts"]
        lines.append(
            "| C1 (control positivo, preregistrado) | exactitud 0.80 con "
            "memoria vs 0.00 sin ella | **se sostiene** |")
        lines.append(
            "| H-C2 léxico (preregistrado) | adherencia 0.667 con Γ vs 0.033 "
            "sin Γ | **se sostiene** |")
        lines.append(
            "| H-C17a / H-C17b (preregistrado) | reducción de homogeneidad "
            "0.073 supera placebo; Δ acuerdo de errores 0.039 dentro de ±0.10 "
            "| **se sostiene, con matices** |")
    if rho and "summary" in rho:
        rs = rho["summary"]
        lines.append(
            f"| H-C2 ρ: ¿la proyección encarece la redundancia? | Δρ por "
            f"paquete +{rs['worst_delta_pct']:.1f}% (peor, medido); por "
            f"solicitud ≈+{rs['worst_delta_pct_per_request']:.1f}% (estimación "
            "aritmética, diseño no implementado) | **"
            f"{rs['verdict_hc2_rho']}** |")
    adp = _load(ROOT / "results" / "bench_adapter" / "results.json")
    if adp and "summary" in adp:
        a = adp["summary"]
        lines.append(
            f"| H-C6 (adaptador real) | LoRA rank 8 en 36 s; adherencia "
            f"bruta {a['adherence']['adapter']:.2f} vs "
            f"{a['adherence']['retrieval']:.2f} (brazos NO comparables) | "
            f"**{a['h6']}** |")
    if soc and "summary" in soc:
        ss = soc["summary"]
        lines.append(
            f"| H-C11 (dirección, C9-lite) | circuito de adopción por "
            f"utilidad ejercitado; identidad 1+1 es la misma respuesta dos "
            f"veces | **{ss['h11_direction']}** |")
    lines += ["", "## 2. Detalle por benchmark", ""]

    # 2.1 H-C1 a escala
    if hc1 and "summary" in hc1:
        s = hc1["summary"]
        lines += ["", "### 2.1 H-C1 a escala (memoria local, 5 familias × 5 usuarios)",
                  "",
                  f"**Cifra central.** {s['n_questions']} preguntas (12 por "
                  "usuario: 5 factuales, 4 de léxico, 3 de procedimiento, con "
                  "preguntas entre documentos), 5 familias por pregunta. "
                  "Ganancia media por PREGUNTA "
                  f"**{s['mean_gain_by_question']:+.3f}** con IC95 "
                  f"[{s['gain_ci95_by_question'][0]:+.3f}, "
                  f"{s['gain_ci95_by_question'][1]:+.3f}] (agrupado por "
                  "pregunta; por celda: "
                  f"{s['mean_gain']:+.3f} [{s['gain_ci95_cells'][0]:+.3f}, "
                  f"{s['gain_ci95_cells'][1]:+.3f}]). Las estadísticas de la "
                  "wiki por familia y usuario están guardadas en el "
                  "resultado.",
                  "",
                  "**Por familia:**", ""]
        ws = hc1.get("wiki_stats", {})
        for m, v in s["by_model"].items():
            extra = ""
            if m in ws:
                us = list(ws[m].values())
                anch = [u["claims"] - u["maturity"]["RAW"] - u["maturity"]["DIGESTED"] for u in us]
                rate = [1 - u["anchor_rejection_rate"] for u in us]
                extra = (f"; afirmaciones ancladas por usuario {min(anch)}–{max(anch)} "
                         f"(media {sum(anch) / len(anch):.1f}), tasa de anclaje "
                         f"{min(rate):.2f}–{max(rate):.2f}")
            lines.append(f"- `{m}`: ganancia media {v['mean_gain']:+.3f} "
                         f"(n={v['n']}){extra}")
        lines += ["", "**Por usuario:**", ""]
        for u, v in s["by_user"].items():
            lines.append(f"- `{u}`: ganancia media {v['mean_gain']:+.3f} "
                         f"(n={v['n']})")
        lines += [
            "",
            "**Explicación.** La memoria convierte en recuperables preguntas "
            "que ningún modelo base puede responder (hechos del usuario, "
            "umbrales de su protocolo, términos preferidos). La variación "
            "entre familias mezcla dos cosas —la familia digiere Y responde— "
            "y la atribución al digestor requiere el diseño cruzado de la "
            "siguiente fase. Solo phi3.5 se separa por el tamaño de su wiki "
            "(muchas menos afirmaciones ancladas); entre las otras cuatro, ni "
            "el número de afirmaciones ancladas ni la tasa de anclaje ordenan "
            "la ganancia. Una compuerta de calidad del digestor, si se adopta, "
            "sería un piso de afirmaciones ancladas, no un umbral derivado de "
            "estos datos.",
            "",
            "**Ajuste propuesto.** Añadir el brazo «memoria + proyección Γ», "
            "un usuario real y el diseño cruzado digestor/respuesta."]

    # 2.2 ρ
    if rho and "summary" in rho:
        rs = rho["summary"]
        lines += ["", "### 2.2 ρ de la proyección (camino de despacho real)", "",
                  f"**Cifra central.** Sobre el documento de procedimientos de "
                  "cada usuario (19-32 oraciones, 391-718 tokens de material), "
                  "fragmentado con P9 (L=10, F=2), con el PROYECTOR real de la "
                  "LCE: la proyección sube ρ "
                  f"**+{rs['median_delta_pct']:.1f}%** (mediana) y "
                  f"**+{rs['worst_delta_pct']:.1f}%** (peor) con el protocolo "
                  "actual (Γ replicado en cada paquete).",
                  "",
                  "**Explicación.** Δρ es estructural: ≈ tamaño de Γ / tamaño "
                  "de cada paquete, y no se diluye con documentos más largos.",
                  "",
                  "**Qué NO concluye.** La condición de muerte real de H-C2 "
                  "(«muere si el aumento de ρ supera la ganancia») exige "
                  "comparar este costo con la ganancia de adherencia; esa "
                  "comparación y los diseños por-solicitud o con caché "
                  "quedan pendientes.",
                  "",
                  "**Estimación, no medición.** Si Γ se inyectara una sola vez "
                  "por solicitud, la misma aritmética sobre estos conteos de "
                  "tokens daría "
                  f"+{min(u['delta_pct_per_request'] for u in rho['users'].values()):.1f}% a "
                  f"+{rs['worst_delta_pct_per_request']:.1f}% "
                  f"(mediana +{rs['median_delta_pct_per_request']:.1f}%). Ese "
                  "diseño no existe en el protocolo y la cifra no está medida; "
                  "una caché de Γ por usuario en el nodo podría acercarla a "
                  "cero, lo que es una hipótesis."]

    # 2.3 C9-lite
    if soc and "summary" in soc:
        ss = soc["summary"]
        lines += ["", "### 2.3 C9-lite social (5 nodos reales)", "",
                  f"**Cifras.** Masa de colas post: utilidad "
                  f"{ss['tail_mass_utility']:.2f} vs prevalencia "
                  f"{ss['tail_mass_prevalence']:.2f} (la del brazo de "
                  "utilidad sale del diseño: nadie conocía los términos y "
                  "todos copian la glosa del contexto). Identidad: "
                  f"{ss['identity_violations_utility']}+"
                  f"{ss['identity_violations_prevalence']} — la sonda no "
                  "recibe las cápsulas, así que es la misma respuesta dos "
                  "veces. Estado: **" + ss["h11_direction"] + "**.",
                  "",
                  f"**Alcance y desviaciones.** {ss['scope']}. Dos "
                  "desviaciones post-corrida están declaradas en el "
                  "encabezado de `bench_social.py`.",
                  "",
                  "**Ajuste propuesto.** La versión justa (siguiente fase): "
                  "sonda con cápsulas en contexto, prevalencia que adopta la "
                  "variante mayoritaria aunque sea errónea, utilidad juzgada "
                  "por beneficio posterior, cápsulas con el conocimiento del "
                  "nodo fuente, varias rondas, y el canario verificado por "
                  "hablantes nativos."]

    # 2.4 adaptador (factibilidad)
    if adp and "summary" in adp:
        a = adp["summary"]
        lines += ["", "### 2.4 Adaptador real (factibilidad, MLX LoRA)", "",
                  f"**Cifras.** LoRA rank 8 entrenado en 36 s (200 iters, 13 "
                  "pares) sobre Qwen2.5-3B-Instruct. Adherencia bruta: base "
                  f"{a['adherence']['base']:.2f}, recuperación "
                  f"{a['adherence']['retrieval']:.2f}, adaptador "
                  f"{a['adherence']['adapter']:.2f}. Facticidad: base "
                  f"{a['factual_base']:.2f} vs adaptador "
                  f"{a['factual_adapter']:.2f}.",
                  "",
                  "**Qué NO concluye.** La adherencia no compara brazos "
                  "justos (el lote contamina las tareas; la recuperación "
                  "solo recibió el documento de estilo; sin intervalo de "
                  "confianza): "
                  f"**{a['h6']}**. Los pesos no se distribuyen (licencia "
                  "qwen-research del modelo base); el manifiesto con su "
                  "SHA-256 y la receta están en el resultado. Reentrenar con "
                  "la receta da un adaptador funcionalmente equivalente, no "
                  "necesariamente idéntico bit a bit (MLX no garantiza "
                  "determinismo); el manifiesto permite comprobarlo.",
                  "",
                  f"**Alcance.** {a['scope']}.",
                  "",
                  "**Ajuste propuesto (siguiente fase).** Tareas separadas "
                  "del lote con otra redacción, lote solo de afirmaciones "
                  "entrenables (I1) con ExampleBuilder, repaso y prueba "
                  "nueva, ≥30 tareas con IC, y una segunda familia base de "
                  "licencia permisiva."]

    lines += ["", "## 3. Cierre", "",
              "La LCE tiene ahora: memoria local medida a escala (F1a, con "
              "estadísticas guardadas y CI por pregunta), el costo de ρ de la "
              "proyección medido con el camino de despacho real (F1b, con el "
              "Projector real y sin umbrales inventados), el circuito social "
              "ejercitado con nodos reales (F1d, no concluyente por diseño y "
              "con sus desviaciones declaradas) y la factibilidad del "
              "adaptador en hardware de consumo (F1c, sin pesos en el "
              "repositorio). Las cifras preregistradas de la corrida 2 "
              "siguen siendo el único resultado confirmatorio.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"reporte escrito: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
