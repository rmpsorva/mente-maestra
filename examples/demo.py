"""Ejemplo mínimo: pronóstico Houston + señal de mercado."""

from mente_maestra import MenteMaestra


def run() -> None:
    with MenteMaestra() as mente:
        print("=== APIs disponibles ===")
        print(len(mente.listar()), "endpoints catalogados")
        print("\n=== Pronóstico ===")
        clima = mente.pronostico("Houston, Texas")
        print(clima.get("lectura"))
        print("\n=== Mercado ===")
        mkt = mente.mercado()
        print(mkt.get("lectura"))
        print("\n=== Conocimiento IA ===")
        know = mente.conocimiento("time series forecasting")
        wiki = know.get("wikipedia") or {}
        if isinstance(wiki, dict):
            print(wiki.get("extract", wiki.get("title", "sin extracto"))[:400])


if __name__ == "__main__":
    run()
