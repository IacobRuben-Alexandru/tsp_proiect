import time
import random
import matplotlib.pyplot as plt
from src.utils.backtracking import rezolva_tsp_backtracking
from src.utils.hill_climbing_tsp import rezolva_tsp_hc

def genereaza_instanta_aleatorie(n, cost_max=100, seed=42):
    """Genereaza o matrice de distante simetrica aleatorie.

    Creeaza un graf complet sub forma unei matrici de adiacenta unde costul
    de la i la j este egal cu cel de la j la i.

    Args:
        n (int): Numarul de orase.
        cost_max (int): Limita superioara a distantelor generate (exclusiv).
        seed (int): Valoarea seed pentru generatorul random (reproductibilitate).

    Returns:
        list[list[int]]: Matricea de distante NxN rezultata.
    """
    random.seed(seed)
    matrice = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            val = random.randint(1, cost_max)
            matrice[i][j] = val
            matrice[j][i] = val
    return matrice

def masoara_timp_executie(functie, *args):
    """Masoara timpul de executie al unei functii primite ca argument.

    Utilizeaza time.perf_counter pentru o precizie ridicata a masuratorii.

    Args:
        functie (callable): Functia care trebuie executata si masurata.
        *args: Argumentele pozitionale care vor fi transmise functiei.

    Returns:
        tuple: Un tuplu (rezultat, durata) unde:
            - rezultat: Valoarea returnata de functia apelata.
            - durata (float): Timpul de executie in secunde.
    """
    start = time.perf_counter()
    rezultat = functie(*args)
    sfarsit = time.perf_counter()
    return rezultat, sfarsit - start

def ruleaza_experiment():
    """Ruleaza experimentul comparativ si genereaza graficul de performanta.

    Executa atat algoritmul de Backtracking cat si cel de Hill Climbing pe 
    instante de dimensiuni diferite, apoi salveaza rezultatele intr-un grafic 
    cu doua subplot-uri (scara liniara si scara logaritmica).
    """
    valori_n_bt = [5, 7, 8, 10, 12]
    valori_n_hc = [5, 7, 8, 10, 12, 15, 20, 30, 50]
    
    timpi_bt = []
    timpi_hc = []
    
    print("Incepere experiment...")

    # Rulare Backtracking
    print("Masurare Backtracking...")
    for n in valori_n_bt:
        matrice = genereaza_instanta_aleatorie(n)
        _, durata = masoara_timp_executie(rezolva_tsp_backtracking, n, matrice)
        timpi_bt.append(durata)
        print(f"   BT N={n}: {durata:.4f}s")

    # Rulare Hill Climbing
    print("Masurare Hill Climbing...")
    for n in valori_n_hc:
        matrice = genereaza_instanta_aleatorie(n)
        # Folosim 10 restarts pentru un echilibru intre timp si calitate
        _, durata = masoara_timp_executie(rezolva_tsp_hc, n, matrice, 10)
        timpi_hc.append(durata)
        print(f"   HC N={n}: {durata:.4f}s")

    # Generare Grafice
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot stang: Scara liniara
    ax1.plot(valori_n_bt, timpi_bt, 'o-', label='Backtracking', color='red')
    ax1.plot(valori_n_hc, timpi_hc, 's-', label='Hill Climbing', color='blue')
    ax1.set_title('Performanta TSP (Scara Liniara)')
    ax1.set_xlabel('Numar de orase (N)')
    ax1.set_ylabel('Timp (secunde)')
    ax1.legend()
    ax1.grid(True)

    # Subplot drept: Scara logaritmica
    ax2.semilogy(valori_n_bt, timpi_bt, 'o-', label='Backtracking (Exponential)', color='red')
    ax2.semilogy(valori_n_hc, timpi_hc, 's-', label='Hill Climbing (Cvasiliniar)', color='blue')
    ax2.set_title('Performanta TSP (Scara Logaritmica)')
    ax2.set_xlabel('Numar de orase (N)')
    ax2.set_ylabel('Timp (log secunde)')
    ax2.legend()
    ax2.grid(True, which="both", ls="-")

    plt.tight_layout()
    plt.savefig('comparare_performanta.png')
    print("\nGraficul a fost salvat ca 'comparare_performanta.png'.")
    plt.show()

if __name__ == "__main__":
    ruleaza_experiment()