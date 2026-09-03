"""Corteza: percibir, planear, reflexionar, juzgar."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

INTENTS = {
    "clima": ("clima", "tiempo", "lluvia", "weather", "aire", "calor", "frio", "frío", "tormenta", "pronostic", "inund", "huracan", "huracán"),
    "mercado": ("bitcoin", "btc", "eth", "crypto", "dolar", "dólar", "fx", "cambio", "mercado", "pib", "inflacion", "inflación", "oro", "bolsa", "miedo", "fee"),
    "energia": ("energia", "energía", "carbon", "electric", "kwh", "solar", "red electr"),
    "salud": ("salud", "diabetes", "ensayo", "fda", "who", "oms", "medic"),
    "transito": ("vuelo", "avion", "avión", "trafico", "tráfico", "ruta", "opensky"),
    "ciencia": ("sismo", "terremoto", "nasa", "asteroide", "iss", "spacex", "espacio", "lanzamiento"),
    "media": ("reggaeton", "cancion", "canción", "itunes", "musica", "música", "letra"),
    "conocimiento": ("paper", "investig", "arxiv", "modelo", "ia", "ai", "aprender", "que es", "qué es", "como funciona", "cómo funciona", "forecast", "huggingface"),
    "lugar": ("houston", "mexico", "méxico", "bogota", "bogotá", "madrid", "miami", "texas", "ciudad"),
}


def percibir(texto: str) -> dict[str, Any]:
    q = (texto or "").strip()
    low = q.lower()
    hits = [name for name, keys in INTENTS.items() if any(k in low for k in keys)]
    if not hits:
        hits = ["conocimiento"]
    return {
        "pregunta": q,
        "intenciones": hits,
        "lugar": _lugar(q),
        "tokens": [t for t in re.findall(r"[a-záéíóúñü0-9]+", low) if len(t) > 2],
        "hora_utc": datetime.now(timezone.utc).isoformat(),
    }


def planear(percepcion: dict[str, Any]) -> list[dict[str, Any]]:
    intents = set(percepcion.get("intenciones") or [])
    plan = []
    mapa = [
        ("clima", "pronostico", "Señal ambiental y alertas NWS."),
        ("lugar", "pronostico", "Hay lugar explícito; anclar clima local."),
        ("mercado", "mercado", "FX, crypto y miedo/codicia."),
        ("energia", "energia", "Intensidad de carbono de red."),
        ("salud", "salud", "Ensayos clínicos y señal FDA/OMS."),
        ("transito", "transito", "Tráfico aéreo OpenSky."),
        ("ciencia", "ciencia", "ISS, lanzamientos y sismos."),
        ("media", "media", "Catálogo musical para R.M.P."),
        ("conocimiento", "conocimiento", "Wiki + papers + modelos HF."),
    ]
    seen = set()
    for intent, paso, why in mapa:
        if intent in intents and paso not in seen:
            plan.append({"paso": paso, "por_que": why})
            seen.add(paso)
    if not plan:
        plan.append({"paso": "conocimiento", "por_que": "Sin intención clara; anclar concepto."})
    plan.append({"paso": "juzgar", "por_que": "Cruzar evidencia y declarar confianza."})
    return plan


def _solida(bloque: Any) -> bool:
    if not isinstance(bloque, dict):
        return False
    lect = str(bloque.get("lectura") or "")
    if lect and "no disponible" not in lect.lower() and "no respondió" not in lect.lower() and "sin lectura" not in lect.lower():
        return True
    wiki = bloque.get("wikipedia") or {}
    if isinstance(wiki, dict) and wiki.get("extract"):
        return True
    if bloque.get("iss") or bloque.get("sismos_mes"):
        return True
    return False


def reflexionar(evidencia: dict[str, Any]) -> dict[str, Any]:
    huecos, peso = [], 0
    pesos = {"pronostico": 3, "mercado": 3, "conocimiento": 2, "energia": 2, "salud": 1, "transito": 1, "ciencia": 1, "media": 1}
    for key, pts in pesos.items():
        if _solida(evidencia.get(key)):
            peso += pts
        elif key in (evidencia.get("pasos_hechos") or []):
            huecos.append(f"{key} débil")
    confianza = min(0.93, 0.38 + 0.12 * peso)
    if huecos:
        confianza = max(0.28, confianza - 0.08 * len(huecos))
    return {"confianza": round(confianza, 2), "peso_evidencia": peso, "huecos": huecos, "suficiente": confianza >= 0.5}


def juzgar(percepcion: dict[str, Any], evidencia: dict[str, Any], reflexion: dict[str, Any]) -> dict[str, Any]:
    lineas = [f"Pregunta: {percepcion.get('pregunta')}", "Intenciones: " + ", ".join(percepcion.get("intenciones") or [])]
    if (evidencia.get("pronostico") or {}).get("lectura"):
        lineas.append("Ambiente: " + evidencia["pronostico"]["lectura"])
        nws = evidencia["pronostico"].get("alertas_nws") or 0
        if nws:
            lineas.append(f"Alertas NWS activas en el punto: {nws}. Prioriza riesgo oficial sobre el modelo.")
    if (evidencia.get("mercado") or {}).get("lectura"):
        lineas.append("Mercado: " + evidencia["mercado"]["lectura"])
    if (evidencia.get("energia") or {}).get("lectura"):
        lineas.append("Energía: " + evidencia["energia"]["lectura"])
    if (evidencia.get("salud") or {}).get("lectura"):
        lineas.append("Salud: " + evidencia["salud"]["lectura"])
    if (evidencia.get("transito") or {}).get("lectura"):
        lineas.append("Tránsito: " + evidencia["transito"]["lectura"])
    sci = evidencia.get("ciencia") or {}
    if sci.get("sismos_mes"):
        lineas.append(f"Tierra: {sci['sismos_mes'].get('count', 0)} sismos significativos USGS (mes).")
    if (evidencia.get("media") or {}).get("lectura"):
        lineas.append("Media: " + evidencia["media"]["lectura"])
    wiki = (evidencia.get("conocimiento") or {}).get("wikipedia") or {}
    if isinstance(wiki, dict) and wiki.get("extract"):
        lineas.append("Marco: " + ". ".join(wiki["extract"].split(". ")[:2]).rstrip(".") + ".")
    lineas.append(
        f"Confianza {reflexion.get('confianza')} — huecos: "
        + (", ".join(reflexion.get("huecos") or []) or "ninguno crítico") + "."
    )
    lineas.append("Cruce de fuentes abiertas. No es oráculo.")
    return {"tesis": lineas[2] if len(lineas) > 2 else lineas[-1], "cadena": lineas, "respuesta": "\n".join(lineas)}


def _lugar(texto: str) -> str | None:
    low = texto.lower()
    for token in ("en ", "para ", "de "):
        if token in low:
            frag = texto[low.index(token) + len(token) :].strip(" ?!.")
            if frag:
                return frag
    known = {
        "houston": "Houston, Texas", "texas": "Houston, Texas", "cdmx": "Ciudad de Mexico",
        "mexico": "Ciudad de Mexico", "méxico": "Ciudad de Mexico", "bogota": "Bogota, Colombia",
        "bogotá": "Bogota, Colombia", "madrid": "Madrid, Spain", "miami": "Miami, Florida",
    }
    for key, val in known.items():
        if key in low:
            return val
    return None
