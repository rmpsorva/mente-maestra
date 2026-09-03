# Mente Maestra

Inteligencia pública que se **alimenta de 50 APIs gratuitas** para pronosticar y dar contexto útil al desarrollo de IA.

Proyecto **R.M.P / Real Mente Poder** · repo: [rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra)

## Qué hace

Mente Maestra no es un LLM cerrado. Es un **núcleo de datos vivos**:

- Pronóstico de clima 7 días, calidad de aire, amanecer y sismos
- Señales de mercado: FX (USD/EUR/MXN/COP), crypto y PIB
- Conocimiento para construir IA: papers (OpenAlex, Crossref, arXiv, PubMed, Semantic Scholar), Wikipedia, Datamuse y repos de GitHub
- Cliente único con timeout, reintentos y User-Agent ético
- CLI para preguntar en lenguaje natural

Las 50 APIs están en [`mente_maestra/catalog.py`](mente_maestra/catalog.py). Casi todas **no piden clave**. NASA usa `DEMO_KEY` pública.

## Instalación

```bash
git clone https://github.com/rmpsorva/mente-maestra.git
cd mente-maestra
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso rápido

```bash
# Catálogo
python -m mente_maestra listar

# Pronóstico (geocoding OSM + Open-Meteo)
python -m mente_maestra pronostico "Houston, Texas"

# Mercado
python -m mente_maestra mercado

# Papers + wiki + repos para desarrollar IA
python -m mente_maestra conocer time series forecasting

# Pregunta libre (enruta sola)
python -m mente_maestra preguntar "clima en Ciudad de Mexico"
python -m mente_maestra preguntar bitcoin

# Llamar una API por id (1-50)
python -m mente_maestra llamar 15

# Pulso: cuántas APIs responden ahora
python -m mente_maestra pulso --limit 20
```

## Uso en Python

```python
from mente_maestra import MenteMaestra

with MenteMaestra() as mente:
    print(mente.pronostico("Houston, Texas")["lectura"])
    print(mente.mercado()["lectura"])
    print(mente.consultar("papers de forecasting"))
```

Demo:

```bash
PYTHONPATH=. python examples/demo.py
```

## Las 50 APIs (por capa)

| Capa | IDs | Fuentes |
| --- | --- | --- |
| Clima / ambiente | 1-4 | Open-Meteo, Air Quality, wttr.in, Sunrise-Sunset |
| Geo | 6-9 | Nominatim, ip-api, ipify, Zippopotam |
| Ciencia | 5, 25-28 | USGS, NASA APOD/NEO, ISS, SpaceX |
| Economía / FX / crypto | 11-17 | World Bank, Frankfurter, ER-API, CoinGecko, CoinCap |
| Investigación IA | 20-24 | OpenAlex, Crossref, arXiv, PubMed, Semantic Scholar |
| Conocimiento / NLP | 18-19, 36-39, 44-46, 48 | Wikipedia, Open Library, Gutendex, Dictionary, Datamuse, Agify/Genderize/Nationalize, Numbers |
| Noticias | 29-31 | Hacker News, Reddit worldnews |
| Developer | 32-35, 40 | GitHub, npm, PyPI, MusicBrainz |
| Sandbox / tests | 41-43, 47, 49-50 | JSONPlaceholder, DummyJSON, Random User, PokeAPI, Joke, Advice |
| Países | 10 | REST Countries |

## Por qué sirve para desarrollar IA

1. **Features reales** para modelos: temperatura, lluvia, AQI, FX, BTC, PIB, sismos.
2. **Corpus vivo** de papers y texto libre (Gutenberg, Wikipedia) para RAG.
3. **Enrutado** (`consultar`) como esqueleto de un agente de herramientas.
4. **Pulso** para medir fiabilidad de fuentes abiertas antes de depender de ellas.
5. Cero costo de arranque: no hay tarjeta ni vendor lock-in.

## Límites honestos

- Rate limits existen (Nominatim ~1 req/s, CoinGecko ~10-30/min, NASA DEMO_KEY es compartida).
- Algunas APIs caen o cambian de dominio. Usa `pulso` antes de producción.
- Esto **no reemplaza** un modelo de lenguaje: le da datos y herramientas.
- Respeta ToS de cada proveedor. User-Agent identifica este proyecto a propósito.

## Arquitectura

```
mente_maestra/
  catalog.py   50 APIs + metadatos + uso
  client.py    HTTP único
  brain.py     pronostico / mercado / conocimiento / consultar
  cli.py       interfaz
examples/demo.py
```

## Licencia

MIT · R.M.P 2026
