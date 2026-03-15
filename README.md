# TSP Proiect — Laborator #03  
## Backtracking vs Hill Climbing

Acest proiect implementează și compară două abordări diferite pentru rezolvarea **Problemei Vânzătorului Voiajor** (*Traveling Salesman Problem - TSP*):  
- o metodă **exactă** (Backtracking)  
- o metodă **euristică** (Hill Climbing cu reporniri aleatorii)

---

# 📋 Descrierea Cerințelor

Proiectul este împărțit în trei sarcini principale:

## Sarcina A — Backtracking
Implementarea algoritmului de **backtracking** într-o structură modulară, eliminând variabilele globale și utilizând documentație în stil **Google Docstring**.

Această metodă oferă **soluția optimă**, dar are complexitate algoritmică:

\[
O(n!)
\]

---

## Sarcina B — Hill Climbing
Utilizarea bibliotecii `simpleai` pentru implementarea algoritmului:

```
hill_climbing_random_restarts
```

Această abordare **euristică** găsește soluții **sub-optime**, dar într-un timp mult mai scurt.

---

## Sarcina C — Analiza Performanței
Realizarea unui experiment comparativ care:

- măsoară **timpul de execuție**
- pentru instanțe cu **N între 5 și 50**
- pentru **ambele metode**

Rezultatul este un **grafic comparativ**:
- scară liniară
- scară logaritmică

---

# 🏗️ Structura Proiectului

Proiectul este organizat modular pentru a asigura separarea logică a funcționalităților.

```
tsp_proiect/
│
├── requirements.txt       # Dependențele proiectului
│
├── src/
│   ├── main.py            # Punctul de intrare (CLI)
│   │
│   └── utils/
│       ├── io_utils.py            # Citire / Scriere date
│       ├── backtracking.py        # Algoritmul exact Backtracking
│       ├── hill_climbing_tsp.py   # Implementarea cu simpleai
│       └── performance.py         # Generare instanțe și benchmarking
│
└── data/                  # (Opțional) Fișierele .txt cu matrice
```

---

# 🛠️ Instalare și Cerințe

### Versiune Python recomandată
```
Python 3.10+
```

### Instalare dependențe

Creează un **mediu virtual**, apoi rulează:

```bash
pip install simpleai matplotlib
```

sau

```bash
pip install -r requirements.txt
```

---

# 🚀 Utilizare CLI

Interfața liniei de comandă permite două moduri principale:

- rezolvarea unei instanțe TSP
- rularea experimentului comparativ

---

# 1️⃣ Rezolvarea unei instanțe (Solve)

Pentru a rezolva un TSP dintr-un fișier de intrare.

### Backtracking

```bash
python src/main.py solve orase.txt --algo bt
```

### Hill Climbing (cu parametri custom)

```bash
python src/main.py solve orase.txt --algo hc --restarts 30 --iterations 3000
```

---

# 2️⃣ Rularea experimentului (Experiment)

Generează automat instanțe și creează graficul comparativ.

```bash
python src/main.py experiment --output comparare_performanta.png
```

---

# 📥 Date de Intrare și Ieșire

## Format Date Intrare

Fișierul text trebuie să conțină:

- pe prima linie **numărul de orașe N**
- urmat de **matricea de distanțe**

Exemplu:

```
4
0 10 15 20
10 0 35 25
15 35 0 30
20 25 30 0
```

---

# 📤 Format Output

Programul va afișa în consolă:

- numărul de orașe procesate
- traseul optim / găsit

Exemplu:

```
0 -> 2 -> 3 -> 1 -> 0
```

- costul total al traseului
- timpul de execuție (secunde)

---

## Output pentru experiment

Subcomanda `experiment` generează:

```
comparare_performanta.png
```

Fișierul conține **două grafice**:

- performanța algoritmilor pe scară **liniară**
- performanța pe scară **logaritmică**

pentru a evidenția diferențele de complexitate.

---
