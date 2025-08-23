# Nome Cognome Matricola

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lmc import Assembler, LMC


def run(mem, inputs=None, max_steps=1000):
    m = LMC(memory=mem)
    m.reset(memory=mem, inputs=inputs or [])
    m.run(max_steps=max_steps)
    return list(m.output_queue), m


def test_sum2_outputs_15():
    src = """
    INP
    STA A
    INP
    ADD A
    OUT
    HLT
    A DAT 0
    """
    mem = Assembler().assemble_source(src)
    out, _ = run(mem, inputs=[7, 8])
    assert out == [15]


def test_brz_and_brp_semantics():
    # Programma: imposta ACC=0, poi BRZ salta se acc==0 e flag assente.
    src = """
    LDA Z
    BRZ SKIP
    OUT
    SKIP HLT
    Z DAT 0
    """
    mem = Assembler().assemble_source(src)
    out, _ = run(mem)
    assert out == []  # BRZ deve saltare, quindi OUT non eseguito

    # Ora verifica BRP: fai una SUB che porta ACC sotto 0 -> flag presente, BRP non deve saltare
    src2 = """
    LDA ONE
    SUB TWO
    BRP OK
    OUT
    HLT
    OK HLT
    ONE DAT 1
    TWO DAT 2
    """
    mem2 = Assembler().assemble_source(src2)
    out2, _ = run(mem2)
    assert out2 == [999]  # dopo SUB 1-2 = -1 -> clamp 999, BRP non salta, OUT stampa 999


def test_label_without_colon():
    src = """
    LABEL ADD 4
    BRA LABEL
    HLT
    """
    mem = Assembler().assemble_source(src)
    assert mem[0] == 104
    assert mem[1] == 600
