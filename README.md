# Mente Maestra

Inteligencia pública que se **alimenta de 50 APIs gratuitas** y **piensa en ciclo**: percibir → planear → recoger evidencia → reflexionar → juzgar.

Ahora también tiene **avatar + chat** (fondo oscuro, burbujas, caja abajo), igual que una conversación aquí.

Proyecto **R.M.P / Real Mente Poder** · [rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra) · v1.2.0

## Chat con avatar

```bash
git clone https://github.com/rmpsorva/mente-maestra.git
cd mente-maestra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000)

- Avatar metálico R.M.P (`static/avatar.svg`)
- Tus mensajes a la derecha
- Respuestas de Mente Maestra a la izquierda, con confianza
- Enter envía, Shift+Enter salto de línea

## Pensar en terminal

```bash
python -m mente_maestra pensar "va a llover en Houston y como esta bitcoin" --solo-respuesta
```

```python
from mente_maestra import MenteMaestra

with MenteMaestra() as mente:
    out = mente.pensar("va a llover en Houston y como esta bitcoin")
    print(out["respuesta"])
```

## Arquitectura

```
app.py                 FastAPI /pensar + UI
static/index.html      chat
static/avatar.svg      cara metálica + gorra R.M.P
mente_maestra/cortex.py  pensamiento
mente_maestra/catalog.py 50 APIs
```

MIT · R.M.P 2026
