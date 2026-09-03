"""Hay una sola Mente Maestra.

No se instancian cerebros en paralelo. Chat, CLI y API
piden la misma instancia y la misma memoria en disco.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

NOMBRE = "Mente Maestra"
IDENTIDAD = "R.M.P"
ID = "mente-maestra-unica"
MEMORIA_PATH = Path(__file__).resolve().parent.parent / "data" / "memoria.json"

_lock = Lock()
_unica = None


def get_mente():
    """La única instancia. Crear otra es un error de diseño."""
    global _unica
    with _lock:
        if _unica is None:
            from .brain import MenteMaestra

            _unica = MenteMaestra()
            _unica.identidad = {"id": ID, "nombre": NOMBRE, "marca": IDENTIDAD}
            _unica.memoria = _cargar()
        return _unica


def _cargar() -> list[dict[str, Any]]:
    if not MEMORIA_PATH.exists():
        return []
    try:
        data = json.loads(MEMORIA_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def guardar(memoria: list[dict[str, Any]]) -> None:
    MEMORIA_PATH.parent.mkdir(parents=True, exist_ok=True)
    recorte = memoria[-80:]
    MEMORIA_PATH.write_text(json.dumps(recorte, ensure_ascii=False, indent=2), encoding="utf-8")
