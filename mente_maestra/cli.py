"""CLI de la única Mente Maestra."""

from __future__ import annotations

import argparse
import json
import sys

from .llm import descubrir
from .registry import CATEGORIES
from .una import get_mente


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mente-maestra", description="Una sola mente. Voz propia.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("listar")
    p_list.add_argument("--categoria", choices=CATEGORIES)
    p_call = sub.add_parser("llamar")
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
    sub.add_parser("quien")
    sub.add_parser("voz", help="Qué motor de voz está vivo")

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
        motor = descubrir()
        _print({
            "una": True,
            **mente.identidad,
            "memoria": len(mente.memoria),
            "voz": {"motor": motor["id"], "modelo": motor.get("modelo")} if motor else {"motor": "propia"},
        })
    elif args.cmd == "voz":
        motor = descubrir()
        _print(motor or {"motor": "propia", "detalle": "Ningún Ollama/LM Studio/llama.cpp vivo. Usa voz local."})
    return 0


if __name__ == "__main__":
    sys.exit(main())
