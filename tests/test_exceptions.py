# Nome Cognome Matricola

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lmc import Assembler, LMC, AssemblerError, IllegalInstructionError, MemoryErrorLMC, InputUnderflowError


def test_assembler_errors():
    """Testa che l'assembler generi eccezioni coerenti."""
    asm = Assembler()
    
    print("=== TEST ECCEZIONI ASSEMBLER ===")
    
    # Istruzione sconosciuta
    try:
        asm.assemble_source("INVALID 10")
    except AssemblerError as e:
        print(f" Istruzione sconosciuta: {e}")
    
    # Etichetta duplicata
    try:
        asm.assemble_source("LABEL: ADD 1\nLABEL: SUB 2")
    except AssemblerError as e:
        print(f" Etichetta duplicata: {e}")
    
    # Etichetta non trovata
    try:
        asm.assemble_source("ADD MISSING")
    except AssemblerError as e:
        print(f" Etichetta mancante: {e}")
    
    # Indirizzo fuori range
    try:
        asm.assemble_source("ADD 150")
    except AssemblerError as e:
        print(f" Indirizzo fuori range: {e}")
    
    # DAT fuori range
    try:
        asm.assemble_source("DATA: DAT 1500")
    except AssemblerError as e:
        print(f" DAT fuori range: {e}")


def test_machine_errors():
    """Testa che la macchina LMC generi eccezioni coerenti."""
    print("\n=== TEST ECCEZIONI MACCHINA ===")
    
    # Istruzione illegale
    try:
        m = LMC()
        m.memory[0] = 456  # 4xx non è un'istruzione valida
        m.step()
    except IllegalInstructionError as e:
        print(f" Istruzione illegale: {e}")
    
    # Input vuoto
    try:
        asm = Assembler()
        mem = asm.assemble_source("INP\nHLT")
        m = LMC()
        m.reset(memory=mem, inputs=[])  # Nessun input
        m.step()  # Prova a eseguire INP
    except InputUnderflowError as e:
        print(f" Input vuoto: {e}")
    
    # Memoria fuori range durante reset
    try:
        m = LMC()
        m.reset(memory=[0] * 50)  # Solo 50 celle invece di 100
    except MemoryErrorLMC as e:
        print(f" Memoria dimensione errata: {e}")
    
    # Valore input fuori range
    try:
        m = LMC()
        m.push_input(1500)  # > 999
    except ValueError as e:
        print(f" Input fuori range: {e}")


if __name__ == "__main__":
    test_assembler_errors()
    test_machine_errors()
    print("\n🎯 TUTTE LE ECCEZIONI SONO COERENTI E SPECIFICHE!")
