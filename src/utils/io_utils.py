from typing import Iterable, List, Sequence, Tuple

def citeste_matrice(cale_fisier):
    """Citeste matricea de distante dintr-un fisier text.

    Formatul fisierului: prima linie contine N (numarul de orase),
    urmatoarele N linii contin cate N intregi separati prin spatii.

    Args:
        cale_fisier (str): Calea catre fisierul de intrare.

    Returns:
        tuple[int, list[list[int]]]: Un tuplu format din (n, matrice), unde
            n este numarul de orase si matricea este lista de liste de intregi.

    Raises:
        FileNotFoundError: Daca fisierul specificat nu exista la calea indicata.
        ValueError: Daca datele nu sunt valide sau fisierul este gol.
    """
    with open(cale_fisier, 'r') as f:
        linii = [linie.strip() for linie in f if linie.strip()]
    
    if not linii:
        raise ValueError("Fisierul este gol.")
        
    try:
        n = int(linii[0])
        matrice = [[int(x) for x in linii[i + 1].split()] for i in range(n)]
    except (ValueError, IndexError) as e:
        raise ValueError(f"Formatul fisierului este invalid: {e}")

    return n, matrice
def formateaza_traseu(traseu: Sequence[int]) -> str:
	"""Formateaza traseul pentru afisare, inchizand turul (revenire la start).

	Args:
		traseu: Secventa de orase in ordinea vizitarii (de obicei incepe cu 0).

	Returns:
		Un string de forma "0 -> 1 -> 3 -> 2 -> 0".
	"""
	if not traseu:
		return ""
	parts = [str(x) for x in traseu]
	parts.append(str(traseu[0]))
	return " -> ".join(parts)
def salveaza_rezultat(cale_fisier, traseu, cost, timp):
    """Salveaza rezultatele algoritmului intr-un fisier text.

    Scrie in fisier ordinea oraselor vizitate (incluzand intoarcerea la start),
    costul total determinat si durata executiei.

    Args:
        cale_fisier (str): Calea unde se va salva rezultatul.
        traseu (list[int]): Lista cu indexul oraselor in ordinea parcurgerii.
        cost (int): Costul total calculat pentru traseul respectiv.
        timp (float): Timpul de executie exprimat in secunde.
    """
    with open(cale_fisier, 'w') as f:
        f.write(f"Traseu: {' -> '.join(map(str, traseu))} -> {traseu[0]}\n")
        f.write(f"Cost: {cost}\n")
        f.write(f"Timp executie: {timp:.6f} secunde\n")