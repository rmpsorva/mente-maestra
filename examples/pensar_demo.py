from mente_maestra import MenteMaestra

PREGUNTAS = [
    "¿Va a llover en Houston y cómo está bitcoin?",
    "qué es time series forecasting",
]


def run() -> None:
    with MenteMaestra() as mente:
        for q in PREGUNTAS:
            print("\n===== " + q + " =====")
            out = mente.pensar(q)
            print(out["respuesta"])
            print(f"confianza={out['confianza']} memoria={out['memoria_n']}")


if __name__ == "__main__":
    run()
