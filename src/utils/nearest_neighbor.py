"""Euristica celui mai apropiat vecin (Nearest Neighbor) pentru TSP.

Algoritmul NN este o cautare informata constructiva (greedy): construieste turul
pas cu pas, alegand la fiecare iteratie cel mai apropiat oras nevizitat.
"""

from __future__ import annotations

import random
import time
from typing import List, Sequence, Tuple, Optional

Matrix = List[List[int]]


def _cost_tur(traseu: Sequence[int], matrice: Matrix) -> int:
    """Calculeaza costul total al turului, incluzand revenirea la orasul de start.

    Args:
        traseu (Sequence[int]): Lista cu indecsii oraselor in ordinea vizitarii.
        matrice (Matrix): Matricea de distante NxN.

    Returns:
        int: Costul total al traseului. Returneaza 0 daca traseul este gol.
    """
    if not traseu:
        return 0
    
    cost_drum = sum(matrice[traseu[i]][traseu[i + 1]] for i in range(len(traseu) - 1))
    cost_drum += matrice[traseu[-1]][traseu[0]]
    
    return cost_drum


def genereaza_tur_initial_aleator(n: int, seed: Optional[int] = None) -> List[int]:
    """Genereaza un tur aleator valid, fixand orasul 0 ca punct de start.

    Args:
        n (int): Numarul total de orase.
        seed (Optional[int], optional): Seed pentru generatorul de numere 
            aleatoare, util pentru reproductibilitate.

    Returns:
        List[int]: O permutare aleatoare a oraselor, incepand mereu cu 0.
    """
    if seed is not None:
        random.seed(seed)
        
    orase = list(range(1, n))
    random.shuffle(orase)
    
    return [0] + orase


def rezolva_tsp_nn(n: int, matrice: Matrix, start: int = 0) -> Tuple[List[int], int]:
    """Construieste un tur TSP folosind Nearest Neighbor (NN), dintr-un start dat.

    La fiecare pas, algoritmul alege cel mai apropiat oras nevizitat. Daca exista
    mai multe orase la aceeasi distanta minima, il va alege implicit pe cel cu 
    indexul mai mic.

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN.
        start (int, optional): Indexul orasului de unde incepe turul. Default este 0.

    Returns:
        Tuple[List[int], int]: Un tuplu (traseu, cost) unde `traseu` este ordinea 
            vizitarii, incepand cu orasul `start`.

    Raises:
        ValueError: Daca parametrii `n`, `matrice` sau `start` sunt invalizi.
    """
    if n <= 0:
        raise ValueError("n trebuie sa fie > 0")
    if len(matrice) != n or any(len(row) != n for row in matrice):
        raise ValueError("matrice trebuie sa fie de dimensiune NxN")
    if not (0 <= start < n):
        raise ValueError("Orasul de start trebuie sa apartina intervalului [0, n)")
    
    if n == 1:
        return [start], 0

    vizitat = [False] * n
    vizitat[start] = True
    traseu = [start]
    oras_curent = start

    for _ in range(n - 1):
        oras_urmator = -1
        distanta_minima = float('inf')
        
        for j in range(n):
            if not vizitat[j]:
                distanta = matrice[oras_curent][j]
                # Folosim < strict; egalitatea pastreaza automat primul index gasit (cel mai mic)
                if distanta < distanta_minima:
                    distanta_minima = distanta
                    oras_urmator = j

        if oras_urmator == -1:
            break

        vizitat[oras_urmator] = True
        traseu.append(oras_urmator)
        oras_curent = oras_urmator

    return traseu, _cost_tur(traseu, matrice)


def rezolva_tsp_nn_multistart(
    n: int, matrice: Matrix
) -> Tuple[List[int], int, List[Tuple[int, List[int], int]]]:
    """Ruleaza algoritmul NN din toate punctele de start posibile si returneaza optimul.

    Itereaza prin fiecare oras ca punct de pornire si pastreaza cel mai bun 
    tur gasit (cel cu costul minim).

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN.

    Returns:
        Tuple[List[int], int, List[Tuple[int, List[int], int]]]: Un tuplu format din:
            - cel mai bun traseu gasit
            - costul acelui traseu
            - istoricul detaliat (`rezultate`), o lista de tuple (start, traseu, cost) 
              pentru fiecare rulare.
    """
    cel_mai_bun_traseu: List[int] = []
    cost_minim = float('inf')
    istoric_rulari: List[Tuple[int, List[int], int]] = []

    for start in range(n):
        traseu, cost = rezolva_tsp_nn(n, matrice, start=start)
        istoric_rulari.append((start, traseu, cost))
        
        if cost < cost_minim:
            cost_minim = cost
            cel_mai_bun_traseu = traseu

    return cel_mai_bun_traseu, int(cost_minim), istoric_rulari


def rezolva_tsp_nn_timp(
    n: int,
    matrice: Matrix,
    timp_max: float,
    *,
    seed: int = 42,
) -> Tuple[List[int], int, int, float]:
    """Cauta iterativ o solutie NN mai buna, in limita unui timp dat.

    Ruleaza NN repetat pornind din orase de start alese aleator, pana 
    cand expira timpul alocat (`timp_max`). Returneaza cel mai bun tur gasit.

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN.
        timp_max (float): Timpul maxim de executie alocat, in secunde.
        seed (int, optional): Seed pentru generatorul aleator (reproductibilitate). Default 42.

    Returns:
        Tuple[List[int], int, int, float]: Un tuplu format din:
            - cel mai bun traseu gasit
            - costul minim
            - numarul de iteratii (rulari) efectuate
            - durata reala de executie in secunde

    Raises:
        ValueError: Daca `timp_max` este mai mic sau egal cu 0.
    """
    if timp_max <= 0:
        raise ValueError("timp_max trebuie sa fie o valoare strict pozitiva.")

    moment_start = time.perf_counter()
    deadline = moment_start + float(timp_max)
    generator = random.Random(seed)

    # Rulare de baza (start=0) pentru a garanta macar o solutie in caz de timp foarte scurt
    cel_mai_bun_traseu, cost_minim = rezolva_tsp_nn(n, matrice, start=0)
    iteratii = 1

    while time.perf_counter() < deadline:
        oras_start = generator.randrange(0, n)
        traseu, cost = rezolva_tsp_nn(n, matrice, start=oras_start)
        iteratii += 1
        
        if cost < cost_minim:
            cost_minim = cost
            cel_mai_bun_traseu = traseu

    durata_totala = time.perf_counter() - moment_start
    return cel_mai_bun_traseu, int(cost_minim), iteratii, durata_totala