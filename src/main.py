"""Punct de intrare pentru proiectul TSP (laborator #03).

Ofera:
  - rezolvare TSP prin backtracking (optim) sau hill climbing (euristic)
  - rularea experimentului comparativ si generarea graficului PNG
"""

from __future__ import annotations

import argparse
import time
import sys
from pathlib import Path

# Importuri adaptate la structura folderului src/
from src.utils.backtracking import rezolva_tsp_backtracking
from src.utils.hill_climbing_tsp import rezolva_tsp_hc
from src.utils.io_utils import citeste_matrice, salveaza_rezultat
from src.utils.performance import ruleaza_experiment


def formateaza_traseu(traseu: list[int]) -> str:
    """Transforma lista oraselor intr-un sir formatat pentru afisare.

    Args:
        traseu (list[int]): Lista cu indicii oraselor.

    Returns:
        str: Traseul formatat (ex: "0 -> 1 -> 2 -> 0").
    """
    if not traseu:
        return "N/A"
    return " -> ".join(map(str, traseu)) + f" -> {traseu[0]}"


def _cmd_solve(args: argparse.Namespace) -> int:
    """Executa subcomanda de rezolvare a unei instante specifice.

    Args:
        args (argparse.Namespace): Argumentele parsate din CLI.

    Returns:
        int: Cod de status (0 pentru succes).
    """
    n, matrix = citeste_matrice(args.input)

    start = time.perf_counter()
    if args.algo == "bt":
        route, cost = rezolva_tsp_backtracking(n, matrix)
        algo_name = "backtracking"
    else:
        # Folosim parametrii primiti din CLI pentru Hill Climbing
        route, cost = rezolva_tsp_hc(
            n,
            matrix,
            reporniri=args.restarts,
            iteratii=args.iterations,
            seed=args.seed,
        )
        algo_name = "hill_climbing_random_restarts"
    duration = time.perf_counter() - start

    print(f"\n" + "="*40)
    print(f"REZULTAT TSP ({algo_name.upper()})")
    print(f"="*40)
    print(f"Numar de orase: {n}")
    print(f"Traseu:         {formateaza_traseu(route)}")
    print(f"Cost:           {cost}")
    print(f"Timp executie:  {duration:.6f} secunde")
    print(f"="*40)

    if args.output:
        # Adaptam functia de salvare pentru a include si numele algoritmului daca e nevoie
        salveaza_rezultat(args.output, route, cost, duration)
        print(f"Rezultat salvat in: {args.output}")

    return 0


def _cmd_experiment(args: argparse.Namespace) -> int:
    """Executa subcomanda pentru rularea experimentului comparativ.

    Args:
        args (argparse.Namespace): Argumentele parsate din CLI.

    Returns:
        int: Cod de status (0 pentru succes).
    """
    print("Se ruleaza experimentul comparativ... Acest lucru poate dura cateva secunde.")
    # Apelam functia din performance.py care genereaza graficul
    ruleaza_experiment() 
    
    print(f"\nExperiment finalizat cu succes.")
    print(f"Graficul a fost salvat ca: {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construieste parserul de argumente pentru interfata CLI.

    Returns:
        argparse.ArgumentParser: Obiectul parser configurat.
    """
    parser = argparse.ArgumentParser(
        prog="tsp_proiect", 
        description="Utilitar TSP: Backtracking vs Hill Climbing (Random Restarts)"
    )
    sub = parser.add_subparsers(dest="command", required=True, help="Comanda de executat")

    # Configurare subcomanda 'solve'
    p_solve = sub.add_parser("solve", help="Rezolva o instanta TSP dintr-un fisier text")
    p_solve.add_argument("input", help="Calea catre fisierul de intrare (matricea NxN)")
    p_solve.add_argument("--algo", choices=["bt", "hc"], default="bt", 
                         help="Algoritmul utilizat: bt (Backtracking) sau hc (Hill Climbing)")
    p_solve.add_argument("--restarts", type=int, default=30, help="Numar de reporniri (doar pentru HC)")
    p_solve.add_argument("--iterations", type=int, default=2000, help="Limita iteratii per repornire (doar pentru HC)")
    p_solve.add_argument("--seed", type=int, default=42, help="Seed pentru reproductibilitate")
    p_solve.add_argument("--output", help="Cale fisier pentru salvarea rezultatului (optional)")
    p_solve.set_defaults(func=_cmd_solve)

    # Configurare subcomanda 'experiment'
    p_exp = sub.add_parser("experiment", help="Ruleaza protocolul experimental si genereaza graficele")
    p_exp.add_argument("--output", default="comparare_performance.png", help="Numele fisierului PNG generat")
    p_exp.set_defaults(func=_cmd_experiment)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punctul de intrare principal in aplicatie.

    Args:
        argv (list[str] | None): Argumentele liniei de comanda.

    Returns:
        int: Cod de status (0 pentru succes).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    
    try:
        return int(args.func(args))
    except Exception as e:
        print(f"Eroare critica in timpul executiei: {e}")
        return 1


if __name__ == "__main__":
    # SystemExit asigura returnarea codului de eroare catre terminal
    sys.exit(main())