# Francesco Falcon SM3201408

import argparse
import sys
from pathlib import Path

# Aggiunge la root del progetto al sys.path per permettere `import lmc`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lmc import Assembler, LMC


def main():
    parser = argparse.ArgumentParser(description="Esegui un programma LMC da file .asm")
    parser.add_argument("asm", help="Percorso al file sorgente .asm")
    parser.add_argument("--inputs", nargs="*", type=int, default=[], help="Valori di input (0..999)")
    args = parser.parse_args()

    asm = Assembler()
    memory = asm.assemble_file(args.asm)

    m = LMC(memory=memory)
    m.reset(memory=memory, inputs=args.inputs)
    m.run()

    print("Output:", list(m.output_queue))


if __name__ == "__main__":
    main()
