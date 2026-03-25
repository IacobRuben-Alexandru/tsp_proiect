from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Callable, List, Tuple, Union

import matplotlib.pyplot as plt

try:
    import seaborn as sns
    _HAS_SEABORN = True
except ImportError:
    _HAS_SEABORN = False

# Importurile au fost curatate de duplicate
from .backtracking import rezolva_tsp_backtracking, rezolva_tsp_backtracking_extins
from .hill_climbing_tsp import rezolva_tsp_hc
from .nearest_neighbor import rezolva_tsp_nn, rezolva_tsp_nn_multistart
from .nn_aima import rezolva_tsp_nn_aima, rezolva_tsp_nn_aima_multistart

Matrix = List[List[int]]


def genereaza_matrice_aleatorie(n: int, seed: int = 42) -> Matrix:
    """Genereaza o matrice de distante simetrica, cu valori intre 1 si 100.

    Args:
        n (int): Numarul de orase (dimensiunea matricei NxN).
        seed (int, optional): Seed pentru reproducerea rezultatelor. Default este 42.

    Returns:
        Matrix: Matricea generata.
    """
    random.seed(seed)
    matrice = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            distanta = random.randint(1, 100)
            matrice[i][j] = matrice[j][i] = distanta
    return matrice


def genereaza_instanta_tsp(n: int, rng: random.Random) -> Matrix:
    """Helper intern: genereaza o matrice TSP folosind un generator de tip Random.

    Args:
        n (int): Numarul de orase.
        rng (random.Random): Instanta de generator aleatoriu.

    Returns:
        Matrix: Matricea simetrica generata.
    """
    matrice = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            distanta = rng.randint(1, 100)
            matrice[i][j] = matrice[j][i] = distanta
    return matrice


def _time_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Tuple[float, Any]:
    """Masoara timpul de executie al unei functii.

    Args:
        func (Callable): Functia care trebuie cronometrata.
        *args: Argumente pozitionale pasate functiei.
        **kwargs: Argumente cu nume pasate functiei.

    Returns:
        Tuple[float, Any]: Un tuplu continand durata de executie (secunde) 
            si rezultatul returnat de functie.
    """
    start = time.perf_counter()
    rezultat = func(*args, **kwargs)
    durata = time.perf_counter() - start
    return durata, rezultat


def ruleaza_experiment_timpi() -> Path:
    """Genereaza Graficul 1: Timpul de rulare intre algoritmul Backtracking si NN.

    Evalueaza performanta in timp pentru Backtracking (prima si Y solutii) 
    versus Nearest Neighbor (baza si multistart) pe diferite dimensiuni ale problemei.

    Returns:
        Path: Calea catre imaginea salvata ('timp_performanta.png').
    """
    valori_n_bt = [5, 8, 10, 12]
    valori_n_nn = valori_n_bt + [15, 20, 30, 50]
    seed_baza = 42

    timpi_a, timpi_c = [], []
    timpi_nn, timpi_nn_multi = [], []

    for n in valori_n_bt:
        matrice = genereaza_matrice_aleatorie(n, seed_baza + n)
        durata_a, _ = _time_call(rezolva_tsp_backtracking, n, matrice, mod='prima')
        durata_c, _ = _time_call(rezolva_tsp_backtracking, n, matrice, mod='y_solutii', Y=n)
        timpi_a.append(durata_a)
        timpi_c.append(durata_c)

    for n in valori_n_nn:
        matrice = genereaza_matrice_aleatorie(n, seed_baza + n)
        durata_nn, _ = _time_call(rezolva_tsp_nn, n, matrice)
        durata_multi, _ = _time_call(rezolva_tsp_nn_multistart, n, matrice)
        timpi_nn.append(durata_nn)
        timpi_nn_multi.append(durata_multi)

    if _HAS_SEABORN:
        sns.set_theme()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Grafic Liniar
    ax1.plot(valori_n_bt, timpi_a, 'o-', label='BT a) prima')
    ax1.plot(valori_n_bt, timpi_c, 's-', label='BT c) Y solutii')
    ax1.plot(valori_n_nn, timpi_nn, '^-', label='NN base')
    ax1.plot(valori_n_nn, timpi_nn_multi, 'v-', label='NN multistart')
    ax1.set(xlabel='N', ylabel='Timp (s)', title='Timp linear')
    ax1.legend()
    ax1.grid(True)

    # Grafic Logaritmic
    ax2.semilogy(valori_n_bt, timpi_a, 'o-', label='BT a) prima')
    ax2.semilogy(valori_n_bt, timpi_c, 's-', label='BT c) Y solutii')
    ax2.semilogy(valori_n_nn, timpi_nn, '^-', label='NN base')
    ax2.semilogy(valori_n_nn, timpi_nn_multi, 'v-', label='NN multistart')
    ax2.set(xlabel='N', ylabel='Timp (s, log)', title='Timp log')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    cale_iesire = Path('timp_performanta.png')
    fig.savefig(cale_iesire, dpi=200, bbox_inches='tight')
    plt.close()
    
    return cale_iesire


def ruleaza_experiment_calitate() -> Path:
    """Genereaza Graficul 2: Comparatie a calitatii solutiilor pentru un timp fix.

    Evalueaza costul solutiilor gasite de Backtracking exhaustiv si NN multistart 
    intr-un interval de timp controlat.

    Returns:
        Path: Calea catre imaginea salvata ('calitate_timp_fix.png').
    """
    n_orase = 18
    timpi_limita = [1, 2, 5]
    matrice = genereaza_matrice_aleatorie(n_orase, 42)

    costuri_bt, costuri_nn = [], []
    
    for limita in timpi_limita:
        _, (_, cost_bt) = _time_call(rezolva_tsp_backtracking, n_orase, matrice, mod='exhaustiv', time_limit_s=limita)
        costuri_bt.append(cost_bt)
        
        estimare_y = max(1, int(limita * 1000))
        _, (_, cost_nn) = _time_call(rezolva_tsp_nn_multistart, n_orase, matrice, Y=estimare_y)
        costuri_nn.append(cost_nn)

    fig, ax = plt.subplots()
    pozitii_x = range(len(timpi_limita))
    latime = 0.35
    
    ax.bar([p - latime/2 for p in pozitii_x], costuri_bt, latime, label='BT exhaustiv')
    ax.bar([p + latime/2 for p in pozitii_x], costuri_nn, latime, label='NN multistart')
    ax.set(xlabel='T (s)', ylabel='Cost', title='Calitate la timp fix T')
    ax.set_xticks(pozitii_x)
    ax.set_xticklabels(timpi_limita)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    cale_iesire = Path('calitate_timp_fix.png')
    fig.savefig(cale_iesire, dpi=200, bbox_inches='tight')
    plt.close()
    
    return cale_iesire


def ruleaza_experiment_gap() -> Path:
    """Genereaza Graficul 3: Deviatia (Gap %) intre NN multistart si optimul absolut.

    Calculeaza cat de mult deviaza procentual solutia euristica fata de solutia 
    optima gasita prin Backtracking exhaustiv.

    Returns:
        Path: Calea catre imaginea salvata ('gap_optimal.png').
    """
    valori_n = [5, 8, 10, 12]
    deviatii_procentuale = []
    seed_baza = 42

    for n in valori_n:
        matrice = genereaza_matrice_aleatorie(n, seed_baza + n)
        _, cost_optim = rezolva_tsp_backtracking(n, matrice, mod='exhaustiv')
        _, cost_nn = rezolva_tsp_nn_multistart(n, matrice)
        
        gap = 100 * (cost_nn - cost_optim) / cost_optim if cost_optim > 0 else 0
        deviatii_procentuale.append(gap)

    fig, ax = plt.subplots()
    ax.plot(valori_n, deviatii_procentuale, 'o-')
    ax.set(xlabel='N', ylabel='Gap %', title='Gap NN multistart vs BT optim')
    ax.grid(True)
    
    plt.tight_layout()
    cale_iesire = Path('gap_optimal.png')
    fig.savefig(cale_iesire, dpi=200, bbox_inches='tight')
    plt.close()
    
    return cale_iesire


def ruleaza_experiment() -> List[Path]:
    """Apeleaza suita de baza a primelor 3 experimente.

    Returns:
        List[Path]: Lista cailor catre cele 3 fisiere PNG generate.
    """
    imagine1 = ruleaza_experiment_timpi()
    imagine2 = ruleaza_experiment_calitate()
    imagine3 = ruleaza_experiment_gap()
    print(f'Grafice generate: {imagine1}, {imagine2}, {imagine3}')
    return [imagine1, imagine2, imagine3]


def ruleaza_experiment(
    output_png: Union[str, Path] = "comparare_performanta.png",
    seed: int = 42,
    reporniri_hc: int = 30,
    iteratii_hc: int = 2000,
    bt_time_limit_s: float = 30.0,
) -> Path:
    """Ruleaza experimentul comparativ si genereaza graficul de performanta.
    
    ATENTIE: In Python, aceasta functie o suprascrie pe cea de deasupra datorita
    numelui identic. A fost pastrata conform cerintelor.

    Protocol (conform laborator):
        - N pentru backtracking: 5, 7, 8, 10, 12
        - N pentru hill climbing: 5, 7, 8, 10, 12, 15, 20, 30, 50
        - distante intregi in [1, 100], matrice simetrica, seed fix
        - timp masurat cu time.perf_counter
        - grafic: 2 subploturi (liniar + semilogy), salvat ca PNG

    Args:
        output_png (Union[str, Path], optional): Calea fisierului PNG.
        seed (int, optional): Seed de baza pentru instante.
        reporniri_hc (int, optional): Numar reporniri pentru hill climbing.
        iteratii_hc (int, optional): Limita iteratii per repornire.
        bt_time_limit_s (float, optional): Pragul limita pentru Backtracking.

    Returns:
        Path: Calea catre imaginea PNG generata.
    """
    valori_n_bt = [5, 7, 8, 10, 12]
    valori_n_hc = [5, 7, 8, 10, 12, 15, 20, 30, 50]

    timpi_bt, timpi_hc = [], []
    max_n_bt_sub_prag = None

    for n in valori_n_bt:
        generator = random.Random(seed + n)
        matrice = genereaza_instanta_tsp(n, generator)
        durata, _ = _time_call(rezolva_tsp_backtracking, n, matrice)
        timpi_bt.append(durata)
        if durata <= bt_time_limit_s:
            max_n_bt_sub_prag = n

    for n in valori_n_hc:
        generator = random.Random(seed + n)
        matrice = genereaza_instanta_tsp(n, generator)
        durata, _ = _time_call(
            rezolva_tsp_hc,
            n,
            matrice,
            reporniri=reporniri_hc,
            iteratii=iteratii_hc,
            seed=seed,
        )
        timpi_hc.append(durata)

    if _HAS_SEABORN:
        sns.set_theme()

    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Grafic Liniar
    ax_lin.plot(valori_n_bt, timpi_bt, marker="o", label="Backtracking")
    ax_lin.plot(valori_n_hc, timpi_hc, marker="o", label="Hill Climbing (RR)")
    ax_lin.set(title="Timp executie (scala liniara)", xlabel="N (orase)", ylabel="Timp (secunde)")
    ax_lin.grid(True, which="both", alpha=0.3)
    ax_lin.legend()

    # Grafic Logaritmic
    ax_log.semilogy(valori_n_bt, timpi_bt, marker="o", label="Backtracking")
    ax_log.semilogy(valori_n_hc, timpi_hc, marker="o", label="Hill Climbing (RR)")
    ax_log.set(title="Timp executie (scala log)", xlabel="N (orase)", ylabel="Timp (secunde, log)")
    ax_log.grid(True, which="both", alpha=0.3)
    ax_log.legend()

    if max_n_bt_sub_prag is not None:
        fig.suptitle(f"Prag backtracking {bt_time_limit_s:.0f}s: max N = {max_n_bt_sub_prag}")

    fig.tight_layout()
    cale_iesire = Path(output_png)
    fig.savefig(cale_iesire, dpi=200, bbox_inches='tight')
    plt.close(fig)
    
    return cale_iesire


def ruleaza_experiment_lab4(
    output_png: Union[str, Path] = "comparare_performanta_lab4.png",
    seed: int = 42,
    timp_nn_s: float = 1.0,
) -> Path:
    """Ruleaza experimentul comparativ cerut in Lab #04.

    Grafic minim (cerinta): compara timpii de executie pentru 4 valori ale lui N
    (5, 8, 10, 12) pentru:
        - cazul a) prima solutie / un singur start
        - cazul c) Y solutii / multistart cu Y=N

    Args:
        output_png (Union[str, Path], optional): Calea fisierului PNG generat.
        seed (int, optional): Seed pentru generarea instantelor.
        timp_nn_s (float, optional): Rezervat pentru extensii, pastrat compatibilitate CLI.

    Returns:
        Path: Calea catre imaginea PNG generata.
    """
    valori_n = [5, 8, 10, 12]
    valori_n_nn_extra = [15, 20, 30, 50]

    bt_prima, bt_y = [], []
    nn_prima, nn_y = [], []
    aima_prima, aima_y = [], []

    for n in valori_n:
        matrice = genereaza_instanta_tsp(n, random.Random(seed + n))

        d, _ = _time_call(rezolva_tsp_backtracking_extins, n, matrice, mod="prima")
        bt_prima.append(d)
        
        d, _ = _time_call(rezolva_tsp_backtracking_extins, n, matrice, mod="y_solutii", y_max=n)
        bt_y.append(d)

        d, _ = _time_call(rezolva_tsp_nn, n, matrice, 0)
        nn_prima.append(d)
        
        d, _ = _time_call(rezolva_tsp_nn_multistart, n, matrice)
        nn_y.append(d)

        d, _ = _time_call(rezolva_tsp_nn_aima, n, matrice, 0)
        aima_prima.append(d)
        
        d, _ = _time_call(rezolva_tsp_nn_aima_multistart, n, matrice)
        aima_y.append(d)

    # Colectare date extra doar pentru algoritmul NN (cerinta din protocolul de laborator)
    nn_prima_extra, nn_y_extra = [], []
    aima_prima_extra, aima_y_extra = [], []

    for n in valori_n_nn_extra:
        matrice = genereaza_instanta_tsp(n, random.Random(seed + n))
        
        d, _ = _time_call(rezolva_tsp_nn, n, matrice, 0)
        nn_prima_extra.append(d)
        
        d, _ = _time_call(rezolva_tsp_nn_multistart, n, matrice)
        nn_y_extra.append(d)
        
        d, _ = _time_call(rezolva_tsp_nn_aima, n, matrice, 0)
        aima_prima_extra.append(d)
        
        d, _ = _time_call(rezolva_tsp_nn_aima_multistart, n, matrice)
        aima_y_extra.append(d)

    if _HAS_SEABORN:
        sns.set_theme()

    fig, (ax_a, ax_c) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Grafic a)
    ax_a.plot(valori_n, bt_prima, marker="o", label="BT (prima)")
    ax_a.plot(valori_n, nn_prima, marker="o", label="NN manual (start=0)")
    ax_a.plot(valori_n, aima_prima, marker="o", label="NN aima (start=0)")
    ax_a.plot(valori_n_nn_extra, nn_prima_extra, marker="x", linestyle="--", label="NN manual (extra N)")
    ax_a.plot(valori_n_nn_extra, aima_prima_extra, marker="x", linestyle="--", label="NN aima (extra N)")
    ax_a.set(title="Caz a) prima solutie / un start", xlabel="N (orase)", ylabel="Timp (secunde)")
    ax_a.grid(True, which="both", alpha=0.3)
    ax_a.legend(fontsize=8)

    # Grafic c)
    ax_c.plot(valori_n, bt_y, marker="o", label="BT (Y=N)")
    ax_c.plot(valori_n, nn_y, marker="o", label="NN manual (multistart)")
    ax_c.plot(valori_n, aima_y, marker="o", label="NN aima (multistart)")
    ax_c.plot(valori_n_nn_extra, nn_y_extra, marker="x", linestyle="--", label="NN manual (extra N)")
    ax_c.plot(valori_n_nn_extra, aima_y_extra, marker="x", linestyle="--", label="NN aima (extra N)")
    ax_c.set(title="Caz c) Y solutii / multistart (Y=N)", xlabel="N (orase)", ylabel="Timp (secunde)")
    ax_c.grid(True, which="both", alpha=0.3)
    ax_c.legend(fontsize=8)

    fig.tight_layout()
    cale_iesire = Path(output_png)
    fig.savefig(cale_iesire, dpi=200, bbox_inches='tight')
    plt.close(fig)
    
    return cale_iesire