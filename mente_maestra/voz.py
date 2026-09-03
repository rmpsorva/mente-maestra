"""Voz de Mente Maestra: habla como persona.

Primero intenta Ollama / LM Studio / llama.cpp / vLLM / LocalAI / Jan.
Si no hay modelo, redacta en local con las lecturas — sin tono de reporte.
"""

from __future__ import annotations

from typing import Any

from . import llm


def vestir(out: dict[str, Any]) -> dict[str, Any]:
    notas = _notas(out)
    motor = llm.hablar(notas)
    if motor.get("ok") and motor.get("texto"):
        texto = motor["texto"]
        fuente = motor["motor"]
    else:
        texto = _local(out)
        fuente = "propia"
    out["cadena"] = out.get("cadena") or []
    out["respuesta_cruda"] = out.get("respuesta")
    out["respuesta"] = texto
    out["voz"] = {"motor": fuente, "modelo": motor.get("modelo")}
    return out


def _notas(out: dict[str, Any]) -> str:
    lineas = [
        f"Pregunta del usuario: {out.get('pregunta')}",
        f"Confianza interna: {out.get('confianza')}",
        f"Huecos: {', '.join(out.get('huecos') or []) or 'ninguno'}",
    ]
    for row in out.get("cadena") or []:
        if isinstance(row, str) and not row.startswith("Pregunta:") and not row.startswith("Intenciones:"):
            lineas.append(row)
    return "\n".join(lineas) + "\n\nRedacta la respuesta como una persona hablando."


def _local(out: dict[str, Any]) -> str:
    q = (out.get("pregunta") or "").strip()
    partes: list[str] = []
    if q:
        partes.append(_apertura(q))
    for row in out.get("cadena") or []:
        if not isinstance(row, str):
            continue
        if row.startswith("Ambiente:"):
            partes.append(_clima(row[9:].strip()))
        elif row.startswith("Mercado:"):
            partes.append(_mercado(row[8:].strip()))
        elif row.startswith("Energía:"):
            partes.append(row[8:].strip().rstrip(".") + ". Eso marca si conviene cargar o esperar.")
        elif row.startswith("Salud:"):
            partes.append(row[6:].strip())
        elif row.startswith("Tránsito:"):
            partes.append(row[9:].strip())
        elif row.startswith("Tierra:"):
            partes.append(row)
        elif row.startswith("Marco:"):
            partes.append(row[6:].strip())
        elif row.startswith("Media:"):
            partes.append(row[6:].strip())
    conf = out.get("confianza")
    huecos = out.get("huecos") or []
    if huecos:
        partes.append("Me faltó señal en " + ", ".join(huecos) + "; no lo relleno con invento.")
    elif isinstance(conf, (int, float)):
        if conf >= 0.7:
            partes.append("Con lo que hay, el cuadro está claro. No es destino, es lectura de ahora.")
        else:
            partes.append("Lo dejo provisional: hay dato, pero no para apostar la casa.")
    texto = " ".join(p.strip() for p in partes if p and p.strip())
    return texto or "No me alcanzó la señal para hablar con calma. Pregúntame otra vez más concreto."


def _apertura(q: str) -> str:
    low = q.lower()
    if any(w in low for w in ("bitcoin", "btc", "crypto", "miedo")):
        return "Miro el mercado en vivo, no el rumor."
    if any(w in low for w in ("lluvia", "clima", "tiempo", "alerta")):
        return "Te digo lo que hay afuera, con número, no con presentimiento."
    if any(w in low for w in ("que es", "qué es", "como funciona", "cómo funciona")):
        return "Va en corto y en claro."
    return "Mira, esto es lo que sostiene la pregunta."


def _clima(lect: str) -> str:
    if "no disponible" in lect.lower() or "saturada" in lect.lower():
        return "El modelo de clima está saturado; no te voy a pintar un cielo inventado."
    return lect.replace("Pronóstico para", "En")


def _mercado(lect: str) -> str:
    if "no disponible" in lect.lower():
        return "El tape no contestó entero."
    t = lect.replace("USD->", "El dólar va a").replace("miedo/codicia", "el ánimo está en")
    if "Greed" in t or "greed" in t.lower():
        t += " Greed no es señal de compra sola: es régimen de apetito."
    elif "Fear" in t:
        t += " Fear es precaución, no profecía."
    return t
