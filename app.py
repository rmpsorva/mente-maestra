"""Chat web — una sola Mente Maestra."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mente_maestra import ID, IDENTIDAD, NOMBRE, get_mente

ROOT = Path(__file__).parent
STATIC = ROOT / "static"

app = FastAPI(title=NOMBRE, version="1.3.1")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class Pregunta(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/salud")
def salud():
    mente = get_mente()
    return {
        "ok": True,
        "una": True,
        "id": ID,
        "nombre": NOMBRE,
        "marca": IDENTIDAD,
        "memoria": len(mente.memoria),
    }


@app.post("/pensar")
def pensar(body: Pregunta):
    out = get_mente().pensar(body.texto.strip())
    return {
        "una": True,
        "identidad": out.get("identidad"),
        "respuesta": out.get("respuesta", ""),
        "tesis": out.get("tesis", ""),
        "confianza": out.get("confianza", 0),
        "intenciones": out.get("intenciones", []),
        "huecos": out.get("huecos", []),
        "plan": [p.get("paso") for p in out.get("plan", [])],
        "memoria_n": out.get("memoria_n", 0),
    }
