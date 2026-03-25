from __future__ import annotations

import time
from typing import List, Literal, Sequence, Tuple, Optional

Matrix = List[List[int]]
ModOprire = Literal["prima", "toate", "timp", "y_solutii"]


def _cost_tur(traseu: Sequence[int], matrice: Matrix) -> int:
    """Calculeaza costul total al unui tur, incluzand intoarcerea la punctul de start.

    Itereaza prin traseul dat si aduna costurile muchiilor adiacente din
    matricea de distante, adaugand la final costul muchiei de la ultimul 
    nod inapoi la primul.

    Args:
        traseu (Sequence[int]): O secventa de indecsi reprezentand ordinea oraselor.
        matrice (Matrix): Matricea patratica a distantelor dintre orase.

    Returns:
        int: Costul total al traseului. Returneaza 0 daca traseul este gol.
    """
    if not traseu:
        return 0
    
    # Calcul refactorizat cu o expresie generatoare pentru claritate
    cost_drum = sum(matrice[traseu[i]][traseu[i + 1]] for i in range(len(traseu) - 1))
    cost_drum += matrice[traseu[-1]][traseu[0]]
    
    return cost_drum


def rezolva_tsp_backtracking_extins(
    n: int,
    matrice: Matrix,
    *,
    mod: ModOprire = "toate",
    timp_max: Optional[float] = None,
    y_max: Optional[int] = None,
) -> Tuple[List[int], int, int, float]:
    """Rezolva TSP utilizand algoritmul de backtracking cu moduri de oprire configurabile.

    Functia implementeaza Branch and Bound pentru a taia (prune) ramurile care
    depasesc costul minim curent gasit. Suporta oprirea la prima solutie,
    dupa un timp dat, dupa un anumit numar de solutii sau exhaustiv.

    Args:
        n (int): Numarul total de orase.
        matrice (Matrix): Matricea distantelor (simetrica, cu 0 pe diagonala principala).
        mod (ModOprire, optional): Conditia de oprire ("prima", "toate", "timp", "y_solutii").
            Implicit este "toate".
        timp_max (Optional[float], optional): Limita de timp in secunde. Utilizata doar 
            cand mod="timp". Implicit este None.
        y_max (Optional[int], optional): Numarul maxim de solutii cautate. Utilizat doar
            cand mod="y_solutii". Implicit este None.

    Returns:
        Tuple[List[int], int, int, float]: Un tuplu format din:
            - cel mai bun traseu gasit (lista de indecsi)
            - costul acestui traseu
            - numarul total de solutii gasite
            - timpul de executie in secunde

    Raises:
        ValueError: Daca parametri n, matrice, mod, timp_max sau y_max sunt invalizi.
    """
    if n <= 0:
        raise ValueError("n trebuie sa fie > 0")
    if len(matrice) != n or any(len(rand) != n for rand in matrice):
        raise ValueError("matrice trebuie sa fie de dimensiune NxN")
    if mod not in ("prima", "toate", "timp", "y_solutii"):
        raise ValueError("mod invalid")
    if mod == "timp" and (timp_max is None or timp_max <= 0):
        raise ValueError("timp_max trebuie sa fie > 0 pentru mod='timp'")
    if mod == "y_solutii" and (y_max is None or y_max <= 0):
        raise ValueError("y_max trebuie sa fie > 0 pentru mod='y_solutii'")

    moment_start = time.perf_counter()
    limita_timp = (moment_start + float(timp_max)) if mod == "timp" and timp_max else None

    if n == 1:
        return [0], 0, 1, time.perf_counter() - moment_start

    # Generam un traseu initial secvential pentru a avea un bound superior valid garantat
    cel_mai_bun_traseu = list(range(n))
    cost_optim = _cost_tur(cel_mai_bun_traseu, matrice)

    orase_vizitate = [False] * n
    orase_vizitate[0] = True
    traseu_curent = [0]

    solutii_contorizate = 0
    cautare_oprita = False

    def verifica_timp() -> bool:
        return limita_timp is not None and time.perf_counter() >= limita_timp

    def backtracking_intern(oras_curent: int, cost_acumulat: int) -> None:
        # Folosim nonlocal in loc de liste (ex. nr_solutii[0])
        nonlocal cost_optim, cel_mai_bun_traseu, solutii_contorizate, cautare_oprita

        if cautare_oprita or (limita_timp is not None and verifica_timp()):
            cautare_oprita = True
            return

        # Daca am format un tur complet
        if len(traseu_curent) == n:
            solutii_contorizate += 1
            cost_final = cost_acumulat + matrice[oras_curent][0]
            
            if cost_final < cost_optim:
                cost_optim = cost_final
                cel_mai_bun_traseu = traseu_curent.copy()
            
            # Verificam conditiile de oprire in functie de solutii gasite
            if mod == "prima" or (mod == "y_solutii" and y_max and solutii_contorizate >= y_max):
                cautare_oprita = True
            return

        for urmatorul_oras in range(1, n):
            if orase_vizitate[urmatorul_oras]:
                continue

            cost_viitor = cost_acumulat + matrice[oras_curent][urmatorul_oras]
            
            # Prunere: Daca depasim deja costul optim, abandonam ramura curenta
            if cost_viitor >= cost_optim:
                continue

            orase_vizitate[urmatorul_oras] = True
            traseu_curent.append(urmatorul_oras)
            
            backtracking_intern(urmatorul_oras, cost_viitor)
            
            traseu_curent.pop()
            orase_vizitate[urmatorul_oras] = False

            if cautare_oprita:
                return

    backtracking_intern(0, 0)
    timp_total = time.perf_counter() - moment_start
    
    return cel_mai_bun_traseu, cost_optim, solutii_contorizate, timp_total


def rezolva_tsp_backtracking(n: int, matrice: Matrix) -> Tuple[List[int], int]:
    """Rezolva problema comis-voiajorului (TSP) optim, folosind backtracking.

    Este o functie de tip wrapper (convenience) care apeleaza implementarea 
    extinsa (`rezolva_tsp_backtracking_extins`) in modul "toate" (exhaustiv).

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea de distante NxN (simetrica, diagonala 0).

    Returns:
        Tuple[List[int], int]: Un tuplu continand lista oraselor in ordinea 
            vizitarii (incepand cu 0) si costul minim gasit.
    """
    traseu, cost, _, _ = rezolva_tsp_backtracking_extins(n, matrice, mod="toate")
    return traseu, cost