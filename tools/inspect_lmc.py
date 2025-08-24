# Francesco Falcon SM3201408

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lmc import Assembler, LMC


def inspect_lmc_state(machine: LMC, step_num: int = 0):
    """Stampa lo stato completo della macchina LMC."""
    print(f"\n=== STEP {step_num} ===")
    print(f"PC: {machine.pc:02d}")
    print(f"ACC: {machine.accumulator}")
    print(f"FLAG: {machine.flag}")
    print(f"INPUT: {list(machine.input_queue)}")
    print(f"OUTPUT: {list(machine.output_queue)}")
    print(f"MEMORIA (0-20): {machine.memory[:21]}")
    if machine.pc < len(machine.memory):
        print(f"PROSSIMA ISTRUZIONE: {machine.memory[machine.pc]:03d}")


def demo_inspection():
    # Programma: leggi due numeri e stampa la somma
    src = """
    INP
    STA 10
    INP  
    ADD 10
    OUT
    HLT
    """
    
    asm = Assembler()
    memory = asm.assemble_source(src)
    
    machine = LMC()
    machine.reset(memory=memory, inputs=[5, 7])
    
    step = 0
    inspect_lmc_state(machine, step)
    
    # Esegui step by step con ispezione
    while True:
        try:
            continuing = machine.step()
            step += 1
            inspect_lmc_state(machine, step)
            
            if not continuing:
                print("\n HALT raggiunto!")
                break
                
        except Exception as e:
            print(f"\n Errore: {e}")
            break


if __name__ == "__main__":
    demo_inspection()
