# Mente Maestra

**Una sola mente.** Un id, un avatar, una memoria, un ciclo de pensamiento.
Chat, CLI y API no crean cerebros distintos: piden `get_mente()`.

[rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra) · R.M.P · v1.3.1

```python
from mente_maestra import get_mente

mente = get_mente()          # siempre la misma
otra = get_mente()
assert mente is otra         # una
print(mente.identidad)
```

```bash
python -m mente_maestra quien
python -m mente_maestra pensar "alertas en Houston y bitcoin" --solo-respuesta
uvicorn app:app --port 8000
```

Memoria persistente: `data/memoria.json` (las últimas 80 tesis).
100 APIs que aportan. No hay enjambre de agentes.

MIT · R.M.P 2026
