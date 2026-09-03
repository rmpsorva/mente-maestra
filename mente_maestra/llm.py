"""Backends locales de voz. Uno vivo basta.

Orden: Ollama → LM Studio → llama.cpp → vLLM → LocalAI → Jan → Tabby → OpenAI-compatible genérico.
No exige clave. Si ninguno responde, la voz local redacta igual.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

BACKENDS = [
    {"id": "ollama", "kind": "ollama", "url": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"), "model": os.environ.get("OLLAMA_MODEL", "")},
    {"id": "lmstudio", "kind": "openai", "url": os.environ.get("LMS_HOST", "http://127.0.0.1:1234/v1"), "model": os.environ.get("LMS_MODEL", "local")},
    {"id": "llamacpp", "kind": "openai", "url": os.environ.get("LLAMACPP_HOST", "http://127.0.0.1:8080/v1"), "model": os.environ.get("LLAMACPP_MODEL", "local")},
    {"id": "vllm", "kind": "openai", "url": os.environ.get("VLLM_HOST", "http://127.0.0.1:8008/v1"), "model": os.environ.get("VLLM_MODEL", "local")},
    {"id": "localai", "kind": "openai", "url": os.environ.get("LOCALAI_HOST", "http://127.0.0.1:8081/v1"), "model": os.environ.get("LOCALAI_MODEL", "local")},
    {"id": "jan", "kind": "openai", "url": os.environ.get("JAN_HOST", "http://127.0.0.1:1337/v1"), "model": os.environ.get("JAN_MODEL", "local")},
    {"id": "tabby", "kind": "openai", "url": os.environ.get("TABBY_HOST", "http://127.0.0.1:5000/v1"), "model": os.environ.get("TABBY_MODEL", "local")},
]

SISTEMA = (
    "Eres Mente Maestra, una sola mente R.M.P. Hablas español claro, de persona, "
    "sin listas de 'intenciones' ni tono de reporte. Usas solo la evidencia que te pasan. "
    "No inventes números. Si falta dato, dilo en una frase. Máximo 8 frases. Tú."
)

_alive: dict[str, Any] | None = None


def hablar(notas: str, timeout: float = 12.0) -> dict[str, Any]:
    motor = descubrir(timeout=2.5)
    if not motor:
        return {"ok": False, "motor": None, "texto": None}
    try:
        if motor["kind"] == "ollama":
            texto = _ollama(motor, notas, timeout)
        else:
            texto = _openai(motor, notas, timeout)
        if texto and len(texto.strip()) > 20:
            return {"ok": True, "motor": motor["id"], "modelo": motor.get("modelo") or motor.get("model"), "texto": texto.strip()}
    except Exception:
        pass
    return {"ok": False, "motor": motor["id"], "texto": None}


def descubrir(timeout: float = 2.0) -> dict[str, Any] | None:
    global _alive
    if _alive:
        return _alive
    extra = os.environ.get("OPENAI_BASE_URL")
    stack = list(BACKENDS)
    if extra:
        stack.insert(0, {"id": "openai_compat", "kind": "openai", "url": extra.rstrip("/"), "model": os.environ.get("OPENAI_MODEL", "local")})
    with httpx.Client(timeout=timeout, follow_redirects=True) as http:
        for b in stack:
            found = _probe(http, b)
            if found:
                _alive = found
                return found
    return None


def _probe(http: httpx.Client, b: dict[str, Any]) -> dict[str, Any] | None:
    base = b["url"].rstrip("/")
    try:
        if b["kind"] == "ollama":
            r = http.get(base + "/api/tags")
            if not r.is_success:
                return None
            models = [m.get("name") for m in (r.json().get("models") or []) if m.get("name")]
            if not models:
                return None
            model = b["model"] if b["model"] in models else models[0]
            return {**b, "modelo": model}
        r = http.get(base + "/models")
        if r.is_success:
            data = r.json()
            rows = data.get("data") if isinstance(data, dict) else data
            names = [m.get("id") for m in (rows or []) if isinstance(m, dict) and m.get("id")]
            model = b["model"] if b["model"] and b["model"] != "local" else (names[0] if names else "local")
            return {**b, "modelo": model}
        # algunos servers no exponen /models pero sí chat
        if r.status_code in {401, 404}:
            return {**b, "modelo": b.get("model") or "local"}
    except Exception:
        return None
    return None


def _ollama(motor: dict[str, Any], notas: str, timeout: float) -> str:
    url = motor["url"].rstrip("/") + "/api/chat"
    body = {
        "model": motor["modelo"],
        "stream": False,
        "messages": [
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": notas},
        ],
        "options": {"temperature": 0.5, "num_predict": 280},
    }
    r = httpx.post(url, json=body, timeout=timeout)
    r.raise_for_status()
    return (r.json().get("message") or {}).get("content") or ""


def _openai(motor: dict[str, Any], notas: str, timeout: float) -> str:
    url = motor["url"].rstrip("/") + "/chat/completions"
    headers = {}
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = {
        "model": motor.get("modelo") or motor.get("model") or "local",
        "temperature": 0.5,
        "max_tokens": 280,
        "messages": [
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": notas},
        ],
    }
    r = httpx.post(url, json=body, headers=headers, timeout=timeout)
    r.raise_for_status()
    choices = r.json().get("choices") or []
    return ((choices[0].get("message") or {}).get("content") if choices else "") or ""
