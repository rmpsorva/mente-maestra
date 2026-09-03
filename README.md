# Mente Maestra

**Una sola mente. Voz propia.** Habla como persona. Si hay modelo local, lo usa.

[rmpsorva/mente-maestra](https://github.com/rmpsorva/mente-maestra) · R.M.P · v1.4.0

## Voz

Orden de motores (el primero vivo gana):

1. **Ollama** `127.0.0.1:11434`
2. **LM Studio** `:1234/v1`
3. **llama.cpp** `:8080/v1`
4. **vLLM** `:8008/v1`
5. **LocalAI** `:8081/v1`
6. **Jan** `:1337/v1`
7. **TabbyAPI** `:5000/v1`
8. `OPENAI_BASE_URL` si lo pones

Si ninguno responde, redacta igual con la voz local (sin alucinación de números).

```bash
ollama pull llama3.2
ollama serve
python -m mente_maestra voz
python -m mente_maestra pensar "miedo de bitcoin" --solo-respuesta
```

Variables útiles: `OLLAMA_MODEL`, `OLLAMA_HOST`, `LMS_HOST`, `OPENAI_BASE_URL`.

MIT · R.M.P 2026
