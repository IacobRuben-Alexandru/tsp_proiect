"""Rezolvarea TSP cu algoritmul alpinistului (Hill Climbing) folosind `simpleai`.

Modelare:
- Starea este un tuplu cu ordinea oraselor (ex. (0, 3, 1, 2)).
- Vecinatatea foloseste miscari 2-opt: inversarea unui segment din tur.
- `simpleai` maximizeaza `value`, deci folosim `value(state) = -cost(state)`.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, List, Sequence, Tuple

from simpleai.search import SearchProblem
from simpleai.search.local import hill_climbing_random_restarts


Matrix = List[List[int]]
State = Tuple[int, ...]
Action = Tuple[int, int]  # (i, j) -> inverseaza segmentul [i, j]


def _tsp_cost(state: Sequence[int], matrice: Matrix) -> int:
    """Calculeaza costul total al unui tur, incluzand revenirea la punctul de start.

    Args:
        state (Sequence[int]): O secventa de indici ai oraselor ce reprezinta turul.
        matrice (Matrix): Matricea de adiacenta cu costurile dintre orase.

    Returns:
        int: Costul total al drumului parcurs.
    """
    n = len(state)
    if n == 0:
        return 0
    cost = 0
    for k in range(n - 1):
        cost += matrice[state[k]][state[k + 1]]
    cost += matrice[state[-1]][state[0]]
    return cost


@dataclass
class TSPHillClimbing(SearchProblem):
    """Problema TSP adaptata pentru cautare locala in biblioteca `simpleai`.

    Starea este reprezentata printr-o permutare a oraselor, mentinand orasul 0
    fix pe prima pozitie pentru a reduce spatiul de cautare (elimina simetriile de rotatie).

    Attributes:
        matrice (Matrix): Matricea de distante intre orase.
        seed (int): Valoare pentru initializarea generatorului de numere aleatoare.
    """

    matrice: Matrix
    seed: int = 42

    def __post_init__(self) -> None:
        """Initializeaza problema dupa constructia dataclass-ului."""
        n = len(self.matrice)
        initial_state = tuple(range(n))
        super().__init__(initial_state=initial_state)
        self._rng = random.Random(self.seed)

    @property
    def n(self) -> int:
        """Determina numarul de orase din instanta curenta.

        Returns:
            int: Numarul de orase.
        """
        return len(self.matrice)

    def actions(self, state: State) -> Iterable[Action]:
        """Genereaza toate miscarile posibile de tip 2-opt.

        O miscare 2-opt consta in selectarea a doi indici i si j si inversarea
        segmentului dintre acestia.

        Args:
            state (State): Starea curenta a turului.

        Yields:
            Action: Un tuplu (i, j) reprezentand limitele segmentului de inversat.
        """
        n = len(state)
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                yield (i, j)

    def result(self, state: State, action: Action) -> State:
        """Aplica o miscare 2-opt asupra starii curente.

        Args:
            state (State): Turul actual.
            action (Action): Tuplul (i, j) care indica segmentul ce trebuie inversat.

        Returns:
            State: Noul tur rezultat dupa inversarea segmentului.
        """
        i, j = action
        if i <= 0:
            i = 1
        if j <= i:
            return state
        new_state = list(state)
        new_state[i : j + 1] = reversed(new_state[i : j + 1])
        return tuple(new_state)

    def value(self, state: State) -> float:
        """Calculeaza valoarea starii (functia de fitness).

        Deoarece `simpleai` maximizeaza valoarea, se returneaza costul cu semn negativ.

        Args:
            state (State): Starea care trebuie evaluata.

        Returns:
            float: Valoarea negativa a costului turului.
        """
        return -float(_tsp_cost(state, self.matrice))

    def generate_random_state(self) -> State:
        """Genereaza un tur aleator pentru repornirea algoritmului.

        Pastreaza orasul 0 pe prima pozitie si amesteca restul oraselor.

        Returns:
            State: O permutare aleatorie a oraselor (incepand cu 0).
        """
        if self.n <= 1:
            return tuple(range(self.n))
        rest = list(range(1, self.n))
        self._rng.shuffle(rest)
        return tuple([0] + rest)

    def random_state(self) -> State:
        """Alias pentru generate_random_state, utilizat de anumite versiuni simpleai.

        Returns:
            State: O stare initiala generata aleatoriu.
        """
        return self.generate_random_state()


def rezolva_tsp_hc(
    n: int,
    matrice: Matrix,
    reporniri: int = 30,
    iteratii: int = 2000,
    seed: int = 42,
) -> Tuple[List[int], int]:
    """Rezolva TSP folosind Hill Climbing cu reporniri aleatorii.

    Algoritmul incearca sa gaseasca un optim global prin executarea mai multor
    cautari locale pornite din puncte initiale diferite.

    Args:
        n (int): Numarul de orase.
        matrice (Matrix): Matricea costurilor de deplasare.
        reporniri (int): De cate ori se reinitializeaza cautarea din stari aleatorii.
        iteratii (int): Limita maxima de pasi per executie locala.
        seed (int): Valoarea seed-ului pentru controlul aleatorismului.

    Returns:
        Tuple[List[int], int]: Un tuplu format din:
            - traseu (List[int]): Cel mai bun tur gasit.
            - cost (int): Costul total asociat acestui tur.

    Raises:
        ValueError: Daca dimensiunea parametrului n nu corespunde cu matricea.
    """
    if n != len(matrice):
        raise ValueError("n nu corespunde cu dimensiunea matricei")

    problem = TSPHillClimbing(matrice=matrice, seed=seed)

    result_state = hill_climbing_random_restarts(
        problem,
        restarts_limit=reporniri,
        iterations_limit=iteratii,
    )

    state = getattr(result_state, "state", result_state)
    route = list(state)
    cost = _tsp_cost(route, matrice)
    return route, cost