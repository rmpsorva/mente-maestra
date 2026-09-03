"""Registro único: núcleo 1-50 + oleada 51-100."""

from .catalog import APIS as CORE
from .catalog_plus import EXTRA

APIS = list(CORE) + list(EXTRA)
CATEGORIES = sorted({a["category"] for a in APIS})


def get(api_id: int) -> dict:
    for api in APIS:
        if api["id"] == api_id:
            return api
    raise KeyError(f"API id {api_id} no existe")


def by_category(category: str) -> list:
    return [a for a in APIS if a["category"] == category]
