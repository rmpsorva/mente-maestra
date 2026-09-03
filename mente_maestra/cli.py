"""CLI de la única Mente Maestra."""

from __future__ import annotations

import argparse
import json
import sys

from .registry import CATEGORIES
from .una import get_mente


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mente-maestra", description="Una sola mente. 100 APIs que aportan.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("listar", help="Ver las 100 APIs")
    p_list.add_argument("--categoria", choices=CATEGORIES)
    p_call = sub.add_parser("llamar", help="Llamar API por id")
    p_call.add_argument("id", type=int)
    p_fore = sub.add_parser("pronostico")
    p_fore.add_argument("lugar", nargs="?", default="Houston, Texas")
    sub.add_parser("mercado")
    p_know = sub.add_parser("conocer")
    p_know.add_argument("tema", nargs="+")
    p_think = sub.add_parser("pensar")
    p_think.add_argument("texto", nargs="+")
    p_think.add_argument("--solo-respuesta", action="store_true")
    p_ask = sub.add_parser("preguntar")
    p_ask.add_argument("texto", nargs="+")
    p_pulse = sub.add_parser("pulso")
    p_pulse.add_argument("--limit", type=int, default=20)
    sub.add_parser("quien", help="Identidad de la mente única")

    args = parser.parse_args(argv)
    mente = get_mente()
    if args.cmd == "listar":
        _print(mente.listar(args.categoria))
    elif args.cmd == "llamar":
        _print(mente.llamar(args.id))
    elif args.cmd == "pronostico":
        _print(mente.pronostico(args.lugar))
    elif args.cmd == "mercado":
        _print(mente.mercado())
    elif args.cmd == "conocer":
        _print(mente.conocimiento(" ".join(args.tema)))
    elif args.cmd in {"pensar", "preguntar"}:
        thought = mente.pensar(" ".join(args.texto))
        if args.cmd == "pensar" and getattr(args, "solo_respuesta", False):
            print(thought.get("respuesta", ""))
        else:
            _print(thought)
    elif args.cmd == "pulso":
        _print(mente.pulso(args.limit))
    elif args.cmd == "quien":
        _print({"una": True, **mente.identidad, "memoria": len(mente.memoria)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
