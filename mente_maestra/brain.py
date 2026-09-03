"""Cerebro de Mente Maestra: 100 APIs y pensamiento en ciclo."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import cortex
from . import registry as catalog
from .client import ApiClient


class MenteMaestra:
    def __init__(self, timeout: float = 20.0):
        self.client = ApiClient(timeout=timeout)
        self.memoria: list[dict[str, Any]] = []

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
        result = self.client.fetch(api["url"], params=merged, headers=api.get("headers"))
        result["api"] = {"id": api["id"], "name": api["name"], "category": api["category"]}
        return result

    def pulso(self, limit: int = 100) -> dict[str, Any]:
        results, ok = [], 0
        for api in catalog.APIS[:limit]:
            hit = self.llamar(api["id"])
            alive = bool(hit.get("ok"))
            ok += int(alive)
            results.append({"id": api["id"], "name": api["name"], "category": api["category"], "ok": alive, "status": hit.get("status")})
        return {"vivas": ok, "total": len(results), "ratio": round(ok / max(len(results), 1), 3), "detalle": results}

    def geocodificar(self, lugar: str) -> dict[str, Any]:
        hit = self.llamar(100, {"name": lugar, "count": 1})
        data = hit.get("data") or {}
        results = data.get("results") if isinstance(data, dict) else None
        if results:
            item = results[0]
            return {"ok": True, "lugar": item.get("name"), "lat": item.get("latitude"), "lon": item.get("longitude")}
        hit = self.llamar(6, {"q": lugar, "format": "json", "limit": 1})
        data = hit.get("data") or []
        if isinstance(data, list) and data:
            item = data[0]
            return {"ok": True, "lugar": item.get("display_name"), "lat": float(item["lat"]), "lon": float(item["lon"])}
        return {"ok": False, "lugar": lugar, "lat": 29.7604, "lon": -95.3698}

    def pronostico(self, lugar: str = "Houston, Texas") -> dict[str, Any]:
        geo = self.geocodificar(lugar)
        lat = geo.get("lat") or 29.7604
        lon = geo.get("lon") or -95.3698
        clima = self.llamar(1, {"latitude": lat, "longitude": lon, "current_weather": True, "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max", "forecast_days": 7, "timezone": "auto"})
        aire = self.llamar(2, {"latitude": lat, "longitude": lon, "current": "pm10,pm2_5,us_aqi"})
        alertas = self.llamar(54, {"point": f"{lat},{lon}"})
        return {
            "generado": datetime.now(timezone.utc).isoformat(),
            "lugar": geo,
            "clima": clima.get("data"),
            "aire": aire.get("data"),
            "alertas_nws": _n_features(alertas.get("data")),
            "sismos_mes": _resumen_sismos(self.llamar(5).get("data")),
            "lectura": _leer_clima(clima.get("data"), geo),
        }

    def mercado(self) -> dict[str, Any]:
        fx = self.llamar(13, {"from": "USD", "to": "EUR,MXN,COP,GBP"})
        crypto = self.llamar(15, {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd", "include_24hr_change": "true"})
        fear = self.llamar(72, {"limit": 1})
        fees = self.llamar(71)
        pib = self.llamar(11, {"format": "json", "per_page": 3})
        return {
            "generado": datetime.now(timezone.utc).isoformat(),
            "fx_usd": fx.get("data"),
            "crypto": crypto.get("data"),
            "miedo_codicia": fear.get("data"),
            "fees_btc": fees.get("data"),
            "pib_usa": pib.get("data"),
            "lectura": _leer_mercado(fx.get("data"), crypto.get("data"), fear.get("data")),
        }

    def energia(self) -> dict[str, Any]:
        carbon = self.llamar(55)
        return {"carbon_uk": carbon.get("data"), "lectura": _leer_carbon(carbon.get("data"))}

    def salud(self, tema: str = "diabetes") -> dict[str, Any]:
        trials = self.llamar(62, {"query.term": tema, "pageSize": 3})
        return {"trials": trials.get("data"), "lectura": f"Ensayos clínicos abiertos ligados a '{tema}' (ClinicalTrials.gov)."}

    def transito(self, lat: float = 29.76, lon: float = -95.37) -> dict[str, Any]:
        sky = self.llamar(57, {"lamin": lat - 0.5, "lomin": lon - 0.6, "lamax": lat + 0.5, "lomax": lon + 0.6})
        data = sky.get("data") or {}
        n = len((data.get("states") or [])) if isinstance(data, dict) else 0
        return {"aviones_zona": n, "lectura": f"OpenSky ve {n} aeronaves cerca del punto."}

    def conocimiento(self, tema: str) -> dict[str, Any]:
        wiki = self.client.fetch(f"https://en.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}")
        papers = self.llamar(20, {"search": tema, "per_page": 3})
        models = self.llamar(87, {"search": tema, "limit": 3, "sort": "downloads"})
        lexico = self.llamar(39, {"ml": tema, "max": 8})
        return {
            "tema": tema,
            "wikipedia": wiki.get("data"),
            "papers_openalex": papers.get("data"),
            "modelos_hf": models.get("data"),
            "palabras_relacionadas": lexico.get("data"),
        }

    def ciencia(self) -> dict[str, Any]:
        iss = self.llamar(69)
        launches = self.llamar(68, {"limit": 3})
        sismos = self.llamar(5)
        return {"iss": iss.get("data"), "lanzamientos": launches.get("data"), "sismos_mes": _resumen_sismos(sismos.get("data"))}

    def media_rmp(self) -> dict[str, Any]:
        itunes = self.llamar(79, {"term": "reggaeton", "entity": "song", "limit": 3})
        return {"itunes": itunes.get("data"), "lectura": "Señal iTunes de reggaeton para el universo R.M.P."}

    def pensar(self, texto: str) -> dict[str, Any]:
        percepcion = cortex.percibir(texto)
        plan = cortex.planear(percepcion)
        evidencia: dict[str, Any] = {"pasos_hechos": []}
        traza = [{"fase": "percibir", "dato": percepcion}, {"fase": "planear", "dato": plan}]
        lugar = percepcion.get("lugar") or "Houston, Texas"
        tema = texto.strip() or "artificial intelligence"
        geo = None
        for item in plan:
            paso = item["paso"]
            if paso == "pronostico":
                evidencia["pronostico"] = self.pronostico(lugar)
                geo = evidencia["pronostico"].get("lugar")
            elif paso == "mercado":
                evidencia["mercado"] = self.mercado()
            elif paso == "energia":
                evidencia["energia"] = self.energia()
            elif paso == "salud":
                evidencia["salud"] = self.salud(tema)
            elif paso == "transito":
                lat = (geo or {}).get("lat") or 29.76
                lon = (geo or {}).get("lon") or -95.37
                evidencia["transito"] = self.transito(lat, lon)
            elif paso == "ciencia":
                evidencia["ciencia"] = self.ciencia()
            elif paso == "media":
                evidencia["media"] = self.media_rmp()
            elif paso == "conocimiento":
                evidencia["conocimiento"] = self.conocimiento(tema)
            elif paso == "juzgar":
                continue
            evidencia["pasos_hechos"].append(paso)
            traza.append({"fase": "actuar", "paso": paso, "por_que": item.get("por_que")})
        reflexion = cortex.reflexionar(evidencia)
        juicio = cortex.juzgar(percepcion, evidencia, reflexion)
        out = {
            "pregunta": texto,
            "respuesta": juicio["respuesta"],
            "tesis": juicio["tesis"],
            "confianza": reflexion["confianza"],
            "intenciones": percepcion["intenciones"],
            "plan": plan,
            "traza": traza + [{"fase": "reflexionar", "dato": reflexion}],
            "huecos": reflexion["huecos"],
            "cadena": juicio["cadena"],
            "fuentes": len(catalog.APIS),
        }
        self.memoria.append({"cuando": datetime.now(timezone.utc).isoformat(), "pregunta": texto, "tesis": juicio["tesis"], "confianza": reflexion["confianza"]})
        out["memoria_n"] = len(self.memoria)
        return out

    def consultar(self, texto: str) -> dict[str, Any]:
        return {"ruta": "pensar", "resultado": self.pensar(texto)}

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _n_features(data: Any) -> int:
    if isinstance(data, dict):
        return len(data.get("features") or [])
    return 0


def _resumen_sismos(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"count": 0}
    features = data.get("features") or []
    tops = [{"lugar": (f.get("properties") or {}).get("place"), "mag": (f.get("properties") or {}).get("mag")} for f in features[:5]]
    return {"count": len(features), "destacados": tops}


def _leer_clima(data: Any, geo: dict) -> str:
    if not isinstance(data, dict):
        return "No se pudo leer el clima."
    current = data.get("current_weather") or {}
    daily = data.get("daily") or {}
    maxs = daily.get("temperature_2m_max") or []
    mins = daily.get("temperature_2m_min") or []
    rain = daily.get("precipitation_sum") or []
    extra = ""
    if maxs and mins:
        extra = f" Máxima 7d {max(maxs)}C / mínima {min(mins)}C."
    if rain:
        extra += f" Pico de lluvia {max(rain)} mm."
    return f"Pronóstico para {geo.get('lugar')}: ahora {current.get('temperature')}C, viento {current.get('windspeed')} km/h.{extra}"


def _leer_mercado(fx: Any, crypto: Any, fear: Any) -> str:
    parts = []
    if isinstance(fx, dict) and fx.get("rates"):
        parts.append("USD-> " + ", ".join(f"{k} {v}" for k, v in list(fx["rates"].items())[:4]))
    if isinstance(crypto, dict):
        for coin, info in list(crypto.items())[:3]:
            usd = (info or {}).get("usd")
            chg = (info or {}).get("usd_24h_change")
            if usd is not None:
                flag = "" if chg is None else f" ({chg:.2f}% 24h)"
                parts.append(f"{coin} ${usd}{flag}")
    if isinstance(fear, dict):
        rows = fear.get("data") or []
        if rows:
            parts.append(f"miedo/codicia {rows[0].get('value_classification')} ({rows[0].get('value')})")
    return " | ".join(parts) or "Mercado no disponible."


def _leer_carbon(data: Any) -> str:
    if isinstance(data, dict):
        block = data.get("data") or {}
        if isinstance(block, list) and block:
            block = block[0]
        intensity = (block.get("intensity") or {}) if isinstance(block, dict) else {}
        if intensity:
            return f"Intensidad carbono UK {intensity.get('actual') or intensity.get('forecast')} gCO2/kWh ({intensity.get('index')})."
    return "Sin lectura de red eléctrica."
