"""Cerebro de Mente Maestra: orquesta 50 APIs, pronostica y responde."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import catalog
from .client import ApiClient


class MenteMaestra:
    """Inteligencia ligera que se alimenta de APIs públicas gratuitas."""

    def __init__(self, timeout: float = 20.0):
        self.client = ApiClient(timeout=timeout)

    def listar(self, category: str | None = None) -> list[dict]:
        apis = catalog.by_category(category) if category else catalog.APIS
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "category": a["category"],
                "auth": a["auth"],
                "docs": a["docs"],
                "uso": a["uso"],
            }
            for a in apis
        ]

    def llamar(self, api_id: int, params: dict | None = None) -> dict[str, Any]:
        api = catalog.get(api_id)
        merged = {**api.get("params", {}), **(params or {})}
        headers = api.get("headers")
        result = self.client.fetch(api["url"], params=merged, headers=headers)
        result["api"] = {"id": api["id"], "name": api["name"], "category": api["category"]}
        return result

    def pulso(self, limit: int = 50) -> dict[str, Any]:
        """Chequea salud de las APIs del catálogo."""
        results = []
        ok = 0
        for api in catalog.APIS[:limit]:
            hit = self.llamar(api["id"])
            alive = bool(hit.get("ok"))
            ok += int(alive)
            results.append(
                {
                    "id": api["id"],
                    "name": api["name"],
                    "category": api["category"],
                    "ok": alive,
                    "status": hit.get("status"),
                }
            )
        return {
            "vivas": ok,
            "total": len(results),
            "ratio": round(ok / max(len(results), 1), 3),
            "detalle": results,
        }

    def geocodificar(self, lugar: str) -> dict[str, Any]:
        hit = self.llamar(6, {"q": lugar, "format": "json", "limit": 1})
        data = hit.get("data") or []
        if isinstance(data, list) and data:
            item = data[0]
            return {
                "ok": True,
                "lugar": item.get("display_name"),
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
            }
        return {"ok": False, "lugar": lugar, "lat": None, "lon": None, "raw": hit}

    def pronostico(self, lugar: str = "Houston, Texas") -> dict[str, Any]:
        """Pronóstico 7 días + calidad de aire + amanecer + sismos."""
        geo = self.geocodificar(lugar)
        lat = geo.get("lat") or 29.7604
        lon = geo.get("lon") or -95.3698
        clima = self.llamar(
            1,
            {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
                "forecast_days": 7,
                "timezone": "auto",
            },
        )
        aire = self.llamar(2, {"latitude": lat, "longitude": lon, "current": "pm10,pm2_5,us_aqi"})
        sol = self.llamar(4, {"lat": lat, "lng": lon, "formatted": 0})
        sismos = self.llamar(5)
        return {
            "generado": datetime.now(timezone.utc).isoformat(),
            "lugar": geo,
            "clima": clima.get("data"),
            "aire": aire.get("data"),
            "sol": sol.get("data"),
            "sismos_mes": _resumen_sismos(sismos.get("data")),
            "lectura": _leer_clima(clima.get("data"), geo),
        }

    def mercado(self) -> dict[str, Any]:
        """Señales de FX + crypto + macro USA."""
        fx = self.llamar(13, {"from": "USD", "to": "EUR,MXN,COP,GBP"})
        crypto = self.llamar(
            15,
            {
                "ids": "bitcoin,ethereum,solana",
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
        )
        pib = self.llamar(11, {"format": "json", "per_page": 3})
        return {
            "generado": datetime.now(timezone.utc).isoformat(),
            "fx_usd": fx.get("data"),
            "crypto": crypto.get("data"),
            "pib_usa": pib.get("data"),
            "lectura": _leer_mercado(fx.get("data"), crypto.get("data")),
        }

    def conocimiento(self, tema: str) -> dict[str, Any]:
        """Papers + wiki + léxico para desarrollar IA sobre un tema."""
        wiki = self.client.fetch(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}"
        )
        papers = self.llamar(20, {"search": tema, "per_page": 3})
        lexico = self.llamar(39, {"ml": tema, "max": 8})
        repos = self.llamar(
            33,
            {"q": f"{tema} language:python stars:>50", "sort": "stars", "per_page": 3},
        )
        return {
            "tema": tema,
            "wikipedia": wiki.get("data"),
            "papers_openalex": papers.get("data"),
            "palabras_relacionadas": lexico.get("data"),
            "repos_github": repos.get("data"),
        }

    def consultar(self, texto: str) -> dict[str, Any]:
        """Enruta una pregunta en lenguaje natural a la capa útil."""
        q = (texto or "").strip().lower()
        if any(w in q for w in ("clima", "tiempo", "lluvia", "pronostic", "weather", "aire")):
            lugar = _extraer_lugar(texto) or "Houston, Texas"
            return {"ruta": "pronostico", "resultado": self.pronostico(lugar)}
        if any(w in q for w in ("bitcoin", "crypto", "dolar", "dólar", "tipo de cambio", "fx", "mercado", "pib")):
            return {"ruta": "mercado", "resultado": self.mercado()}
        if any(w in q for w in ("paper", "investig", "arxiv", "ia", "ai", "modelo", "forecast")):
            tema = texto.strip() or "time series forecasting"
            return {"ruta": "conocimiento", "resultado": self.conocimiento(tema)}
        if q.startswith("api ") or q.startswith("llama "):
            try:
                api_id = int("".join(ch for ch in q if ch.isdigit()) or "1")
                return {"ruta": "llamar", "resultado": self.llamar(api_id)}
            except Exception:
                pass
        return {
            "ruta": "conocimiento",
            "resultado": self.conocimiento(texto or "artificial intelligence"),
        }

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _resumen_sismos(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"count": 0}
    features = data.get("features") or []
    tops = []
    for feat in features[:5]:
        props = feat.get("properties") or {}
        tops.append(
            {
                "lugar": props.get("place"),
                "mag": props.get("mag"),
                "url": props.get("url"),
            }
        )
    return {"count": len(features), "destacados": tops}


def _leer_clima(data: Any, geo: dict) -> str:
    if not isinstance(data, dict):
        return "No se pudo leer el clima."
    current = data.get("current_weather") or {}
    daily = data.get("daily") or {}
    temp = current.get("temperature")
    wind = current.get("windspeed")
    maxs = daily.get("temperature_2m_max") or []
    mins = daily.get("temperature_2m_min") or []
    rain = daily.get("precipitation_sum") or []
    lugar = geo.get("lugar") or "ubicación"
    extra = ""
    if maxs and mins:
        extra = f" Máxima 7d {max(maxs)}C / mínima {min(mins)}C."
    if rain:
        extra += f" Lluvia acumulada pico {max(rain)} mm."
    return (
        f"Pronóstico para {lugar}: ahora {temp}C, viento {wind} km/h.{extra} "
        "Fuente Open-Meteo (sin clave)."
    )


def _leer_mercado(fx: Any, crypto: Any) -> str:
    parts = []
    if isinstance(fx, dict) and fx.get("rates"):
        rates = fx["rates"]
        parts.append(
            "USD-> "
            + ", ".join(f"{k} {v}" for k, v in list(rates.items())[:4])
        )
    if isinstance(crypto, dict):
        for coin, info in list(crypto.items())[:3]:
            usd = info.get("usd")
            chg = info.get("usd_24h_change")
            if usd is not None:
                flag = "" if chg is None else f" ({chg:.2f}% 24h)"
                parts.append(f"{coin} ${usd}{flag}")
    return " | ".join(parts) or "Mercado no disponible en este instante."


def _extraer_lugar(texto: str) -> str | None:
    lower = texto.lower()
    for token in ("en ", "para ", "de "):
        if token in lower:
            return texto[lower.index(token) + len(token) :].strip(" ?!.") or None
    return None
