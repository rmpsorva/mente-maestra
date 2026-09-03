"""Interfaz de línea de comandos."""

from __future__ import annotations

import argparse
import json
import sys

from .brain import MenteMaestra
from .catalog import CATEGORIES


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mente-maestra",
        description="Inteligencia alimentada por 50 APIs públicas gratuitas.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("listar", help="Ver las 50 APIs")
    p_list.add_argument("--categoria", choices=CATEGORIES)

    p_call = sub.add_parser("llamar", help="Llamar una API por id (1-50)")
    p_call.add_argument("id", type=int)

    p_fore = sub.add_parser("pronostico", help="Pronóstico clima + aire + sismos")
    p_fore.add_argument("lugar", nargs="?", default="Houston, Texas")

    sub.add_parser("mercado", help="FX + crypto + macro")

    p_know = sub.add_parser("conocer", help="Papers, wiki y repos de un tema")
    p_know.add_argument("tema", nargs="+")

    p_ask = sub.add_parser("preguntar", help="Pregunta en lenguaje natural")
    p_ask.add_argument("texto", nargs="+")

    p_pulse = sub.add_parser("pulso", help="Chequea cuántas APIs responden")
    p_pulse.add_argument("--limit", type=int, default=12)

    args = parser.parse_args(argv)
    mind = MenteMaestra()
    try:
        if args.cmd == "listar":
            _print(mind.listar(args.categoria))
        elif args.cmd == "llamar":
            _print(mind.llamar(args.id))
        elif args.cmd == "pronostico":
            _print(mind.pronostico(args.lugar))
        elif args.cmd == "mercado":
            _print(mind.mercado())
        elif args.cmd == "conocer":
            _print(mind.conocimiento(" ".join(args.tema)))
        elif args.cmd == "preguntar":
            _print(mind.consultar(" ".join(args.texto)))
        elif args.cmd == "pulso":
            _print(mind.pulso(args.limit))
        return 0
    finally:
        mind.close()


if __name__ == "__main__":
    sys.exit(main())
