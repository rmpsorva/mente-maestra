# Mente Maestra

100 APIs públicas **que aportan** + ciclo de pensamiento + chat con avatar R.M.P.

[rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra) · v1.3.0

## Qué se conectó (y por qué)

No se pegaron 50.000 listings. Se sumaron **50 fuentes extra** solo si dan señal nueva:

| Capa | IDs | Aporte |
| --- | --- | --- |
| Clima / riesgo | 51-54, 56 | Altitud, inundación, marino, alertas NWS |
| Energía | 55 | Intensidad de carbono de red |
| Tránsito | 57-58 | Aviones OpenSky + ruta OSRM |
| Salud | 61-64 | FDA, ClinicalTrials, OMS, Open Food Facts |
| Crypto profunda | 70-73 | Hashrate, fees, miedo/codicia, cap global |
| Macro | 74-76 | Stooq equity, desempleo, FMI |
| IA | 87-89 | Hugging Face, Papers with Code, conceptos OpenAlex |
| Media R.M.P | 79-82 | iTunes, Deezer, lyrics, SportsDB Houston |
| Resiliencia | 86, 93-96 | Wayback, TLS, DNS, URLhaus, HIBP |

Núcleo 1-50 sigue en `catalog.py`. Oleada 2 en `catalog_plus.py`. Registro único: `registry.py`.

## Chat

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

http://127.0.0.1:8000

```bash
python -m mente_maestra pensar "alertas en Houston y miedo de bitcoin" --solo-respuesta
python -m mente_maestra listar --categoria energia
python -m mente_maestra pulso --limit 30
```

MIT · R.M.P 2026
