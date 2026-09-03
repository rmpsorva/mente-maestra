"""Chat web de Mente Maestra — avatar + conversación."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mente_maestra import MenteMaestra

ROOT = Path(__file__).parent
STATIC = ROOT / "static"

app = FastAPI(title="Mente Maestra", version="1.2.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

mind = MenteMaestra()


class Pregunta(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/salud")
def salud():
    return {"ok": True, "nombre": "Mente Maestra", "memoria": len(mind.memoria)}


@app.post("/pensar")
def pensar(body: Pregunta):
    out = mind.pensar(body.texto.strip())
    return {
        "respuesta": out.get("respuesta", ""),
        "tesis": out.get("tesis", ""),
        "confianza": out.get("confianza", 0),
        "intenciones": out.get("intenciones", []),
        "huecos": out.get("huecos", []),
        "plan": [p.get("paso") for p in out.get("plan", [])],
        "memoria_n": out.get("memoria_n", 0),
    }
