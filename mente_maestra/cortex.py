"""Corteza de Mente Maestra.

Ciclo de pensamiento offline (sin LLM de pago):
  percibir -> planear -> recoger evidencia -> reflexionar -> juzgar

No simula conciencia. Sí produce una cadena de razonamiento auditable
con intenciones, evidencia viva, confianza y lagunas.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

INTENTS = {
    "clima": ("clima", "tiempo", "lluvia", "weather", "aire", "calor", "frio", "frío", "tormenta", "pronostic"),
    "mercado": ("bitcoin", "btc", "eth", "crypto", "dolar", "dólar", "fx", "cambio", "mercado", "pib", "inflacion", "inflación", "oro", "bolsa"),
    "ciencia": ("sismo", "terremoto", "nasa", "asteroide", "iss", "spacex", "espacio", "sol"),
    "conocimiento": ("paper", "investig", "arxiv", "modelo", "ia", "ai", "aprender", "que es", "qué es", "como funciona", "cómo funciona", "forecast"),
    "lugar": ("houston", "mexico", "méxico", "bogota", "bogotá", "madrid", "miami", "texas", "ciudad"),
}


def percibir(texto: str) -> dict[str, Any]:
    q = (texto or "").strip()
    low = q.lower()
    hits = [name for name, keys in INTENTS.items() if any(k in low for k in keys)]
    if not hits:
        hits = ["conocimiento"]
    lugar = _lugar(q)
    return {
        "pregunta": q,
        "intenciones": hits,
        "lugar": lugar,
        "tokens": _tokens(low),
        "hora_utc": datetime.now(timezone.utc).isoformat(),
    }


def planear(percepcion: dict[str, Any]) -> list[dict[str, Any]]:
    intents = set(percepcion.get("intenciones") or [])
    plan = []
    if "clima" in intents or "lugar" in intents:
        plan.append({"paso": "pronostico", "por_que": "Necesito señal ambiental local para proyectar."})
    if "mercado" in intents:
        plan.append({"paso": "mercado", "por_que": "Necesito FX/crypto/macro para un juicio de riesgo."})
    if "ciencia" in intents:
        plan.append({"paso": "ciencia", "por_que": "Hay señal espacial o geológica en la pregunta."})
    if "conocimiento" in intents or not plan:
        plan.append({"paso": "conocimiento", "por_que": "Falta marco conceptual o papers para anclar la respuesta."})
    plan.append({"paso": "juzgar", "por_que": "Cruzar evidencia, declarar confianza y lagunas."})
    return plan


def reflexionar(evidencia: dict[str, Any]) -> dict[str, Any]:
    huecos = []
    peso = 0
    if evidencia.get("pronostico") and evidencia["pronostico"].get("lectura"):
        peso += 2
    else:
        if "pronostico" in (evidencia.get("pasos_hechos") or []):
            huecos.append("clima incompleto")
    if evidencia.get("mercado") and evidencia["mercado"].get("lectura"):
        peso += 2
    elif "mercado" in (evidencia.get("pasos_hechos") or []):
        huecos.append("mercado incompleto")
    if evidencia.get("conocimiento"):
        wiki = evidencia["conocimiento"].get("wikipedia") or {}
        extract = wiki.get("extract") if isinstance(wiki, dict) else None
        if extract:
            peso += 2
        else:
            huecos.append("wiki débil")
    if evidencia.get("ciencia"):
        peso += 1
    confianza = min(0.95, 0.25 + 0.12 * peso)
    if huecos:
        confianza = max(0.2, confianza - 0.15 * len(huecos))
    return {
        "confianza": round(confianza, 2),
        "peso_evidencia": peso,
        "huecos": huecos,
        "suficiente": confianza >= 0.45 and len(huecos) <= 2,
    }


def juzgar(percepcion: dict[str, Any], evidencia: dict[str, Any], reflexion: dict[str, Any]) -> dict[str, Any]:
    lineas = []
    pregunta = percepcion.get("pregunta") or ""
    lineas.append(f"Pregunta: {pregunta}")
    lineas.append("Intenciones: " + ", ".join(percepcion.get("intenciones") or []))

    clima = evidencia.get("pronostico") or {}
    if clima.get("lectura"):
        lineas.append("Ambiente: " + clima["lectura"])
        daily = (clima.get("clima") or {}).get("daily") or {}
        rain = daily.get("precipitation_sum") or []
        if rain and max(rain) >= 10:
            lineas.append("Juicio clima: hay probabilidad material de lluvia en la ventana 7d; no asumas cielo estable.")
        elif rain:
            lineas.append("Juicio clima: señal de precipitación baja/moderada; útil como feature, no como alarma.")

    mkt = evidencia.get("mercado") or {}
    if mkt.get("lectura"):
        lineas.append("Mercado: " + mkt["lectura"])
        crypto = mkt.get("crypto") or {}
        moves = []
        if isinstance(crypto, dict):
            for coin, info in crypto.items():
                chg = (info or {}).get("usd_24h_change")
                if isinstance(chg, (int, float)):
                    moves.append((coin, chg))
        if moves:
            fuerte = [f"{c} {v:.1f}%" for c, v in moves if abs(v) >= 3]
            if fuerte:
                lineas.append("Juicio mercado: movimiento 24h relevante en " + ", ".join(fuerte) + ". Trata como volatilidad, no como destino.")
            else:
                lineas.append("Juicio mercado: 24h relativamente contenido. Mejor para baseline que para trade impulsivo.")

    sci = evidencia.get("ciencia") or {}
    if sci.get("sismos_mes"):
        n = sci["sismos_mes"].get("count", 0)
        lineas.append(f"Tierra: {n} sismos significativos reportados en el feed mensual USGS.")
    if sci.get("iss"):
        lineas.append("Espacio: posición ISS disponible como pulso de sistemas orbitales.")

    know = evidencia.get("conocimiento") or {}
    wiki = know.get("wikipedia") or {}
    if isinstance(wiki, dict) and wiki.get("extract"):
        extract = wiki["extract"].strip().split(". ")
        lineas.append("Marco: " + ". ".join(extract[:2]).rstrip(".") + ".")
    words = know.get("palabras_relacionadas") or []
    if isinstance(words, list) and words:
        labels = [w.get("word") for w in words[:6] if isinstance(w, dict) and w.get("word")]
        if labels:
            lineas.append("Campo semántico: " + ", ".join(labels))

    lineas.append(
        f"Confianza {reflexion.get('confianza')} — huecos: "
        + (", ".join(reflexion.get("huecos") or []) or "ninguno crítico")
        + "."
    )
    if not reflexion.get("suficiente"):
        lineas.append("Laguna: evidencia floja. El juicio es provisional; conviene otra pasada o una clave opcional (FRED/NASA propia).")
    lineas.append("Esto no es oráculo. Es un cruce de fuentes abiertas + reglas de consistencia.")
    return {
        "tesis": lineas[2] if len(lineas) > 2 else lineas[-1],
        "cadena": lineas,
        "respuesta": "\n".join(lineas),
    }


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-záéíóúñü0-9]+", text) if len(t) > 2]


def _lugar(texto: str) -> str | None:
    low = texto.lower()
    for token in ("en ", "para ", "de "):
        if token in low:
            frag = texto[low.index(token) + len(token) :].strip(" ?!.")
            if frag:
                return frag
    known = {
        "houston": "Houston, Texas",
        "texas": "Houston, Texas",
        "cdmx": "Ciudad de Mexico",
        "mexico": "Ciudad de Mexico",
        "méxico": "Ciudad de Mexico",
        "bogota": "Bogota, Colombia",
        "bogotá": "Bogota, Colombia",
        "madrid": "Madrid, Spain",
        "miami": "Miami, Florida",
    }
    for key, val in known.items():
        if key in low:
            return val
    return None
