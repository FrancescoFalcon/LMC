# LMC - Little Man Computer (Python)
[![CI](https://github.com/FrancescoFalcon/LMC/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/FrancescoFalcon/LMC/actions/workflows/ci.yml)

Francesco Falcon SM3201408 

Questo progetto implementa:
- Un simulatore di LMC (classe `LMC` in `lmc/machine.py`)
- Un assembler per l'assembly semplificato LMC (classe `Assembler` in `lmc/assembler.py`)

Requisiti: Python 3.11+. Runtime senza dipendenze esterne (solo standard library). Strumenti opzionali richiedono dipendenze aggiuntive.

## Quick start (30s)

```powershell
python -m venv .venv
\.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools/run_lmc.py examples/sum2.asm --inputs 7 8
# Output atteso: [15]
```

## Caratteristiche implementate

### Architettura LMC
- Memoria: 100 celle (0-99), valori 0-999
- Accumulatore con clamp modulo 1000
- Program counter con wrap 0-99
- Flag per overflow/underflow aritmetico
- Code FIFO per input e output

### Istruzioni supportate
- `1xx`: ADD xx - Addizione
- `2xx`: SUB xx - Sottrazione  
- `3xx`: STA xx - Store accumulatore
- `5xx`: LDA xx - Load in accumulatore
- `6xx`: BRA xx - Branch incondizionato
- `7xx`: BRZ xx - Branch se acc=0 e flag assente
- `8xx`: BRP xx - Branch se flag assente
- `901`: INP - Input da coda
- `902`: OUT - Output a coda
- `000`: HLT - Halt

### Assembler features
- Etichette con ":" e senza ":"
- Pseudo-istruzione `DAT [valore]`
- Case-insensitive
- Commenti con "//"
- Gestione errori con eccezioni specifiche

## Installazione

### Ambiente virtuale (PowerShell su Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Dipendenze
Necessario solo per provare i tests (opzionali). Installa tutto da un unico file:

```powershell
pip install -r requirements.txt
```

## Utilizzo

### Assembler (da sorgente a memoria)

```python
from lmc import Assembler

asm = Assembler()
with open("examples/counter.asm", "r", encoding="utf-8") as f:
    memory = asm.assemble_source(f.read())
print(memory)  # lista di 100 interi (0..999)
```

### Simulatore LMC

```python
from lmc import LMC

machine = LMC(memory=memory)
machine.reset(memory=memory, inputs=[5])  # esempio: input n=5
machine.run()
print(list(machine.output_queue))
```

### CLI rapido

```powershell
python tools/run_lmc.py examples/sum2.asm --inputs 7 8
# Output: [15]

python tools/run_lmc.py examples/counter.asm --inputs 3
# Output: [0, 1, 2, 3]
```

### Ispezione stato passo-passo

```powershell
python tools/inspect_lmc.py
```

## Test

```powershell
python -m pytest -q
```

## Esempi

- `examples/sum2.asm`: somma due input e stampa il risultato.
- `examples/counter.asm`: stampa da 0 a n (incluso) dove n è l'input.
- `examples/screenshot_prog.asm`: programma di esempio basato sul pdf.


## Struttura progetto

```
.
├─ lmc/         # Libreria: macchina LMC, assembler, eccezioni
├─ tools/       # Script CLI (runner e ispezione)
├─ examples/    # Programmi LMC di esempio
├─ tests/       # Test PyTest
├─ README.md    # Documentazione
└─ requirements.txt
```

## Note

- In caso di errori, vengono sollevate eccezioni specifiche (vedi `lmc/exceptions.py`).
- BRZ salta solo se accumulatore=0 E flag assente.
- BRP salta se flag assente (operazione precedente in range 0-999).

## Troubleshooting

- ModuleNotFoundError: lmc → esegui i comandi dalla root del progetto (dove c'è `README.md`).
- INP con coda vuota → fornisci input con `--inputs` al runner oppure `reset(inputs=[...])` nelle API.

## Integrazione CI

- GitHub Actions esegue automaticamente i test su push/PR (vedi badge in alto).

## Licenza

Distribuito con licenza MIT. Vedi il file `LICENSE`.
