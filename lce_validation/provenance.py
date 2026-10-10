"""Provenance común de los benchmarks (preregistro R14, §1.3.3).

Cada benchmark real registra con esto: commit de git, SHA-256 del
preregistro, versión de Ollama y digests de los modelos usados. La
comprobación dura (rechazo si un modelo no coincide con el preregistrado)
la hace ``check_digests``; sin ella no hay corrida confirmatoria.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout.strip()


def _ollama(url: str, path: str) -> dict:
    base = url.rstrip("/").removesuffix("/v1")
    with urllib.request.urlopen(f"{base}{path}", timeout=30) as r:
        return json.loads(r.read())


def record(prereg: Path, models: list[str], url: str = "http://localhost:11434/v1",
           extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Metadatos de procedencia de una corrida."""
    info = _ollama(url, "/api/version")
    digests: dict[str, str] = {}
    for m in models:
        try:
            req = urllib.request.Request(f"{url.rstrip('/').removesuffix('/v1')}/api/show",
                                         data=json.dumps({"name": m}).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                digests[m] = json.loads(r.read()).get("details", {}).get(
                    "parent_model", "") or "n/d"
        except Exception:
            digests[m] = "n/d"
    out: dict[str, Any] = {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain", "--", "swarmbly_lce",
                               "lce_validation", "docs")),
        "prereg": str(prereg),
        "prereg_sha256": _sha(prereg),
        "ollama_version": info.get("version", "n/d"),
        "models": digests,
        "python": sys.version.split()[0],
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if extra:
        out.update(extra)
    return out


def _sha(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def check_digests(prov: dict, expected: dict[str, str]) -> list[str]:
    """Lista de modelos cuyo digest no coincide con el esperado."""
    problems = []
    for m, want in expected.items():
        got = prov.get("models", {}).get(m)
        if got is None or got == "n/d":
            problems.append(f"{m}: sin digest")
        elif got != want:
            problems.append(f"{m}: {got[:12]}… != {want[:12]}…")
    return problems
