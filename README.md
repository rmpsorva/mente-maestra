# Mente Maestra

Inteligencia pública que se **alimenta de 50 APIs gratuitas** y **piensa en ciclo**: percibir → planear → recoger evidencia → reflexionar → juzgar.

Proyecto **R.M.P / Real Mente Poder** · [rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra) · v1.1.0

## Pensar por sí misma

`mente.pensar(pregunta)` no solo enruta. Construye una traza auditable:

1. **Percibir** intenciones (clima, mercado, ciencia, conocimiento, lugar)
2. **Planear** qué fuentes abrir y por qué
3. **Actuar** contra las APIs vivas
4. **Reflexionar** si la evidencia alcanza (confianza + huecos)
5. **Juzgar** una tesis en lenguaje claro, sin fingir oráculo

No es un LLM de pago. Es una corteza simbólica + datos reales. Sirve como esqueleto de agente para desarrollar IA.

```bash
python -m mente_maestra pensar "va a llover en Houston y como esta bitcoin" --solo-respuesta
PYTHONPATH=. python examples/pensar_demo.py
```

```python
from mente_maestra import MenteMaestra

with MenteMaestra() as mente:
    out = mente.pensar("va a llover en Houston y como esta bitcoin")
    print(out["respuesta"])
    print(out["confianza"], out["plan"], out["huecos"])
```

## Resto del núcleo

- Pronóstico 7 días, AQI, amanecer, sismos
- FX + crypto + PIB
- Papers / wiki / Datamuse / GitHub para RAG
- 50 APIs en [`mente_maestra/catalog.py`](mente_maestra/catalog.py)

```bash
git clone https://github.com/rmpsorva/mente-maestra.git
cd mente-maestra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m mente_maestra listar
python -m mente_maestra pronostico "Houston, Texas"
python -m mente_maestra mercado
python -m mente_maestra pensar "qué es forecasting"
```

## Arquitectura

```
mente_maestra/
  catalog.py   50 APIs
  client.py    HTTP
  cortex.py    percibir / planear / reflexionar / juzgar
  brain.py     actuar + memoria de sesión
  cli.py       pensar | preguntar | pronostico | mercado
```

## Límite honesto

Piensa con reglas + evidencia abierta. No inventa cotizaciones ni papers. Si falta dato, baja la confianza y lo dice.

MIT · R.M.P 2026
