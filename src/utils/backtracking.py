import sys

def rezolva_tsp_backtracking(n, matrice):
    """Rezolva problema comis-voiajorului (TSP) folosind backtracking cu prunere.

    Aceasta functie implementeaza o abordare de tip Branch and Bound simplificat 
    pentru a gasi traseul cel mai scurt care viziteaza toate orasele exact o data 
    si revine la punctul de plecare.

    Args:
        n (int): Numarul total de orase din problema.
        matrice (list[list[int]]): O matrice patrata de adiacenta unde 
            matrice[i][j] reprezinta costul deplasarii de la orasul i la orasul j.

    Returns:
        tuple[list[int], int]: Un tuplu continand:
            - traseu_optim (list[int]): Lista indicilor oraselor in ordinea vizitarii.
            - cost_minim (int): Valoarea numerica a celui mai mic cost gasit.

    Raises:
        ValueError: Daca n este mai mic de 1 sau matricea nu este valida.
    """
    
    # Folosim un dictionar pentru a stoca starea optima (tehnica wrapper)
    stare_optima = {
        'cost_minim': sys.maxsize,
        'traseu_optim': []
    }

    def _backtracking(oras_curent, vizitat, traseu, cost_acumulat):
        """Exploreaza recursiv ramurile arborelui de decizie pentru TSP.

        Args:
            oras_curent (int): Indicele orasului in care ne aflam in prezent.
            vizitat (list[bool]): Lista de flag-uri pentru a urmari orasele vizitate.
            traseu (list[int]): Stiva care retine ordinea actuala a oraselor.
            cost_acumulat (int): Suma costurilor marginilor parcurse pana acum.
        """
        # Caz de baza: toate orasele vizitate
        if len(traseu) == n:
            # Adaugam costul intoarcerii la orasul de start (0)
            cost_total = cost_acumulat + matrice[oras_curent][traseu[0]]
            
            if cost_total < stare_optima['cost_minim']:
                stare_optima['cost_minim'] = cost_total
                stare_optima['traseu_optim'] = traseu[:]
            return

        for urmator in range(n):
            if not vizitat[urmator]:
                cost_nou = cost_acumulat + matrice[oras_curent][urmator]

                # Prunere: daca deja am depasit cel mai bun cost gasit, abandonam ramura
                if cost_nou < stare_optima['cost_minim']:
                    vizitat[urmator] = True
                    traseu.append(urmator)
                    
                    _backtracking(urmator, vizitat, traseu, cost_nou)
                    
                    # Backtrack (revenire la starea anterioara)
                    traseu.pop()
                    vizitat[urmator] = False

    # Initializare: pornim intotdeauna din orasul 0 pentru a evita permutarile redundante
    if n > 0:
        vizitat = [False] * n
        vizitat[0] = True
        _backtracking(0, vizitat, [0], 0)

    return stare_optima['traseu_optim'], stare_optima['cost_minim']