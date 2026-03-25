"""Nearest Neighbor pentru TSP folosind biblioteca AIMA (cand este disponibila).

In enuntul Lab #04 se recomanda utilizarea `aima3` pentru NN. In practica,
versiunile PyPI ale `aima3` pot sa nu includa o functie NN dedicata pentru TSP.
Acest modul expune o interfata stabila (wrapper) si:
  - foloseste `aima3` daca exista o functie compatibila;
  - altfel face fallback la implementarea manuala NN.

Scop: proiectul sa fie executabil si comparabil cu backtracking/NN manual.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Any

# Presupunem ca aceste functii sunt importate din modulul refactorizat anterior
from .nearest_neighbor import rezolva_tsp_nn, rezolva_tsp_nn_multistart


Matrix = List[List[int]]


def _incearca_gaseste_nn_aima() -> Optional[Callable[..., Any]]:
    """Incearca sa localizeze o functie NN pentru TSP in biblioteca `aima3`.

    Returns:
        Optional[Callable]: Functia compatibila din aima3 daca exista, altfel None.
    """
    try:
        from aima3 import search  # type: ignore
    except ImportError:
        return None

    # Unele materiale mentioneaza `nearest_neighbor_tsp`, dar poate lipsi in anumite fork-uri
    candidat = getattr(search, "nearest_neighbor_tsp", None)
    if callable(candidat):
        return candidat
        
    return None


_NEAREST_NEIGHBOR_TSP = _incearca_gaseste_nn_aima()


def rezolva_tsp_nn_aima(n: int, matrice: Matrix, start: int = 0) -> Tuple[List[int], int]:
    """Wrapper NN TSP bazat pe AIMA, cu fallback automat catre solutia manuala.

    Incearca sa apeleze functia din `aima3`. Daca pachetul lipseste,
    functia nu are semnatura asteptata sau apare orice eroare la executie, 
    redirectioneaza transparent apelul catre `rezolva_tsp_nn` implementat manual.

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN.
        start (int, optional): Orasul de start. Default este 0.

    Returns:
        Tuple[List[int], int]: Un tuplu continand traseul gasit si costul acestuia.
    """
    # Daca AIMA nu a fost gasita la initializarea modulului, trecem direct la fallback
    if _NEAREST_NEIGHBOR_TSP is None:
        return rezolva_tsp_nn(n, matrice, start=start)

    orase = list(range(n))

    def distanta(i: int, j: int) -> int:
        return matrice[i][j]

    try:
        # Best-effort adapter pentru semnatura presupusa a functiei AIMA
        traseu = list(_NEAREST_NEIGHBOR_TSP(start, orase, distanta))
        
        # Ne asiguram ca ruta incepe cu orasul cerut, rotind lista daca este nevoie
        if traseu and traseu[0] != start and start in traseu:
            index_start = traseu.index(start)
            traseu = traseu[index_start:] + traseu[:index_start]
            
        # Calculam costul turului folosind o expresie generatoare, la fel ca in implementarea curata
        cost = sum(matrice[traseu[i]][traseu[i + 1]] for i in range(len(traseu) - 1))
        cost += matrice[traseu[-1]][traseu[0]]
        
        return traseu, cost
        
    except Exception:
        # Fallback robust: daca AIMA da gres (ex: pachetul e instalat, dar semnatura e alta)
        return rezolva_tsp_nn(n, matrice, start=start)


def rezolva_tsp_nn_aima_multistart(
    n: int, matrice: Matrix
) -> Tuple[List[int], int, List[Tuple[int, List[int], int]]]:
    """Ruleaza NN AIMA (sau fallback) din toate punctele de start posibile.

    Pastreaza cel mai bun tur (cu costul minim) din toate rularile. Daca
    `aima3` nu este disponibil, deleaga direct catre versiunea manuala multistart
    pentru o performanta superioara.

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN.

    Returns:
        Tuple[List[int], int, List[Tuple[int, List[int], int]]]: Un tuplu format din:
            - cel mai bun traseu gasit
            - costul minim asociat
            - istoricul (start, traseu, cost) pentru fiecare iteratie.
    """
    # Evitam ineficienta rularii fallback-ului intr-o bucla repetitiva aici,
    # apeland direct implementarea manuala optimizata pentru multistart
    if _NEAREST_NEIGHBOR_TSP is None:
        return rezolva_tsp_nn_multistart(n, matrice)

    cel_mai_bun_traseu: List[int] = []
    cost_minim = float('inf')
    istoric_rulari: List[Tuple[int, List[int], int]] = []

    for start in range(n):
        traseu, cost = rezolva_tsp_nn_aima(n, matrice, start=start)
        istoric_rulari.append((start, traseu, cost))
        
        if cost < cost_minim:
            cost_minim = cost
            cel_mai_bun_traseu = traseu

    cost_final = int(cost_minim) if cost_minim != float('inf') else 0
    return cel_mai_bun_traseu, cost_final, istoric_rulari