---
status: current
lang: es+en
---
# Publicación de Swarmbly LCE v0.1 · Publication checklist

Este repositorio se publica en dos depósitos de Zenodo, igual que Swarmbly v2: el **artículo** (whitepaper, depósito manual) y el **software** (repositorio, por la integración de Zenodo con GitHub). La versión 0.1 contiene diseño, especificación, código y arnés, **sin resultados**; las corridas reales irán en la 0.2.

*Two Zenodo records, as for Swarmbly v2: the paper (manual upload) and the software (GitHub integration). Version 0.1 ships design, specification, code and harness, with no results.*

## 1. Antes de publicar · Before publishing

- [ ] Leer los PDF `docs/WHITEPAPER_LCE_EN.pdf` y `docs/WHITEPAPER_LCE_ES.pdf` de principio a fin (la versión inglesa es una traducción nueva).
- [ ] Revisar las tres entradas ⚠️ de `docs/REFERENCES_LCE.md` ([37], [59], [61]); cada una tiene un solo campo sin confirmar.
- [ ] Decidir si la nota de Swarmbly `FINDING_2026-10-04_correlated_errors_across_families` (pendiente de commit en `Swarmbly-AI_Clean`) se publica antes o junto con la LCE, porque el whitepaper la cita.
- [ ] `python -m pytest` y `python -m lce_validation.run_all` en verde en el Mac.
- [ ] Si se cambia cualquier `.md` de los whitepapers, regenerar los PDF: `python scripts/build_pdfs.py` (requiere pandoc, playwright con Chromium y pypdf).

## 2. Depósito del artículo · Paper record (manual)

- [ ] Zenodo → *New upload*. Archivos: `WHITEPAPER_LCE_EN.pdf`, `WHITEPAPER_LCE_ES.pdf`, `WHITEPAPER_LCE_EN.md`, `WHITEPAPER_LCE_ES.md`, `REFERENCES_LCE.md`.
- [ ] Metadatos: copiar de `publication/zenodo_whitepaper.json` (tipo *Publication → Preprint*, licencia CC BY 4.0, ORCID, palabras clave, relación *references* con 10.5281/zenodo.23031305).
- [x] Publicar y anotar el DOI del artículo: `10.5281/zenodo.23150478`.

## 3. Repositorio en GitHub · GitHub repository

- [ ] Crear el repositorio vacío `Sebastardito/SwarmblyLCE` en GitHub (sin README ni licencia, para no crear un primer commit en conflicto).
- [ ] En zenodo.org → *GitHub*, activar el interruptor de `SwarmblyLCE` **antes** de crear la release.
- [x] Añadir el DOI del artículo a `.zenodo.json` (`related_identifiers`, relación `isSupplementTo`, `resource_type: publication-preprint`) y a `CITATION.cff` (`preferred-citation.doi`); commit con `git commit -s`.
- [ ] `git push -u origin main` (el remoto `origin` ya está configurado).
- [ ] Comprobar que el workflow `tests` pasa en GitHub Actions (Python 3.10–3.13).
- [ ] Crear la release `v0.1.0` (*Swarmbly LCE v0.1.0 — draft, no results*). Zenodo crea el depósito de software y su DOI a partir de `.zenodo.json`.

## 4. Después · After

- [ ] Anotar el DOI del software en `CITATION.cff` (`doi`) y en el README; añadir la insignia de DOI.
- [ ] En el depósito del artículo, añadir la relación *isSupplementedBy* con el DOI del software (nueva versión de metadatos, sin cambiar archivos).
- [ ] Actualizar `docs/STATUS.md` y `PROJECT_CONTEXT.md` con ambos DOI.

## 5. Hacia la versión 0.2 · Towards v0.2

- [x] Preregistro de C1/C2 confirmado antes de cualquier corrida real (`docs/PREREGISTRATION_C1_C2_ES.md` / `_EN.md`), con las reglas de decisión como código (`lce_validation/decide.py`).
- [x] Corridas confirmatorias en el Mac: la 1 falló por proyección vacía (`docs/RESULTS_2026-10-05_C1_C2_run1_*`); la 2, tras las enmiendas 2 y 3, decidió H-C2 (léxico), H-C17a y H-C17b (`docs/RESULTS_2026-10-05_C1_C2_run2_*`).
- [ ] Verificación del conjunto canario por tres o más hablantes nativos (`lce_validation/data/canary_verification/`), y `python -m lce_validation.canary_verify verificador_*.csv`.
- [ ] Issue de discusión del SWIP en Swarmbly-AI con el texto de `publication/SWIP_ISSUE_Swarmbly-AI.md`; después renombrar el SWIP con el número del issue.
- [ ] Opcional: probar `MLXLoRATrainer` (extra `mlx`) en Apple Silicon.
- [ ] Whitepaper v0.2 con los veredictos (incluidos los negativos) y las correcciones del arnés declaradas.
