"""Cliente HTTP: rápido, no se queda colgado, cachea 429."""

from __future__ import annotations

import time
from typing import Any

import httpx

DEFAULT_HEADERS = {
    "User-Agent": "MenteMaestra/1.3 (+https://github.com/rmpsorva/mente-maestra)",
    "Accept": "application/json, text/plain, */*",
}


class ApiClient:
    def __init__(self, timeout: float = 8.0, retries: int = 0, pause: float = 0.15):
        self.timeout = timeout
        self.retries = retries
        self.pause = pause
        self.http = httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS)
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._cool: dict[str, float] = {}

    def fetch(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | None = None,
        ttl: float = 90.0,
    ) -> dict[str, Any]:
        key = url + "?" + repr(sorted((params or {}).items()))
        now = time.time()
        hit = self._cache.get(key)
        if hit and hit[0] > now:
            cached = dict(hit[1])
            cached["cache"] = True
            return cached
        if self._cool.get(url, 0) > now:
            return {"ok": False, "status": 429, "url": url, "error": "cooldown", "data": None, "cache": False}

        last_error = None
        merged = {**DEFAULT_HEADERS, **(headers or {})}
        budget = timeout or self.timeout
        attempts = 1 + (0 if budget <= 4 else self.retries)
        for attempt in range(attempts):
            try:
                response = self.http.get(url, params=params, headers=merged, timeout=budget)
                payload = _parse(response)
                if response.status_code == 429:
                    self._cool[url] = now + 45
                    return {"ok": False, "status": 429, "url": str(response.url), "error": "rate_limit", "data": payload}
                out = {
                    "ok": response.is_success,
                    "status": response.status_code,
                    "url": str(response.url),
                    "data": payload,
                }
                if out["ok"]:
                    self._cache[key] = (now + ttl, out)
                return out
            except httpx.TimeoutException as exc:
                last_error = f"timeout {budget}s"
                break
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                time.sleep(self.pause)
        return {"ok": False, "status": 0, "url": url, "error": last_error, "data": None}

    def close(self) -> None:
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _parse(response: httpx.Response) -> Any:
    text = response.text or ""
    ctype = response.headers.get("content-type", "")
    if "json" in ctype or text[:1] in "{[":
        try:
            return response.json()
        except Exception:
            return text[:4000]
    if text.startswith("<?xml") or "<feed" in text[:200]:
        return {"xml": text[:8000]}
    return text[:4000]
