"""Cliente HTTP compartido: timeout, reintentos y User-Agent ético."""

from __future__ import annotations

import time
from typing import Any

import httpx

DEFAULT_HEADERS = {
    "User-Agent": "MenteMaestra/1.0 (+https://github.com/rmpsorva/mente-maestra)",
    "Accept": "application/json, text/plain, */*",
}


class ApiClient:
    def __init__(self, timeout: float = 20.0, retries: int = 2, pause: float = 0.4):
        self.timeout = timeout
        self.retries = retries
        self.pause = pause
        self.http = httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS)

    def fetch(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict[str, Any]:
        last_error = None
        merged = {**DEFAULT_HEADERS, **(headers or {})}
        for attempt in range(self.retries + 1):
            try:
                response = self.http.get(url, params=params, headers=merged)
                content_type = response.headers.get("content-type", "")
                payload: Any
                if "json" in content_type or response.text[:1] in "{[" :
                    try:
                        payload = response.json()
                    except Exception:
                        payload = response.text[:4000]
                elif response.text.startswith("<?xml") or "<feed" in response.text[:200]:
                    payload = {"xml": response.text[:8000]}
                else:
                    payload = response.text[:4000]
                return {
                    "ok": response.is_success,
                    "status": response.status_code,
                    "url": str(response.url),
                    "data": payload,
                }
            except Exception as exc:  # noqa: BLE001 — se reporta al cerebro
                last_error = str(exc)
                time.sleep(self.pause * (attempt + 1))
        return {"ok": False, "status": 0, "url": url, "error": last_error, "data": None}

    def close(self) -> None:
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
