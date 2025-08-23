# Francesco Falcon SM3201408

from __future__ import annotations
import re
from typing import Dict, List, Tuple

from .exceptions import AssemblerError

INSTRUCTION_OPCODES = {
    # arith/mem
    "ADD": 1,
    "SUB": 2,
    "STA": 3,
    "LDA": 5,
    "BRA": 6,
    "BRZ": 7,
    "BRP": 8,
    # io/ctrl
    "INP": 901,
    "OUT": 902,
    "HLT": 0,
}

LABEL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Assembler:
    """Assembler per LMC.

    Converte un sorgente assembly LMC (stringa o file) nella memoria iniziale (lista da 100 int).

    Sintassi supportata:
    - Etichette opzionali all'inizio di riga: LABEL:
    - Istruzioni case-insensitive con argomento opzionale (numero 0..99 o etichetta)
    - Pseudo-istruzione DAT [val]: memorizza un dato costante 0..999 (default 0)
    - Commenti con // fino a fine riga
    - Una istruzione per riga, al più 100 righe utili; restanti celle riempite con 0.
    """

    def assemble_source(self, source: str) -> List[int]:
        lines = source.splitlines()
        parsed: List[Tuple[int, str, str | None]] = []  # (lineno, mnemonic, arg)
        labels: Dict[str, int] = {}

        # prima passata: raccogli etichette e tokenizza
        mem_index = 0
        for lineno, raw in enumerate(lines, start=1):
            code = raw.split("//", 1)[0].strip()
            if not code:
                continue
            label, instr_part = self._split_label(code, lineno)
            if label:
                key = label.upper()
                if key in labels:
                    raise AssemblerError(f"Linea {lineno}: etichetta duplicata '{label}'")
                labels[key] = mem_index
            if not instr_part:
                # riga con sola etichetta: non conta memoria
                continue
            mnemonic, arg = self._parse_instruction(instr_part, lineno)
            parsed.append((lineno, mnemonic, arg))
            mem_index += 1
            if mem_index > 100:
                raise AssemblerError("Programma troppo lungo (oltre 100 istruzioni)")

        # seconda passata: risolvi etichette e costruisci memoria
        memory = [0] * 100
        for i, (lineno, mnemonic, arg) in enumerate(parsed):
            opcode = self._encode(mnemonic, arg, labels, lineno)
            memory[i] = opcode
        return memory

    def assemble_file(self, path: str) -> List[int]:
        """Assembla un file sorgente assembly LMC.
        
        Args:
            path: percorso al file .asm da assemblare
            
        Returns:
            Lista di 100 interi rappresentanti la memoria iniziale LMC
            
        Raises:
            AssemblerError: per errori di sintassi o riferimenti
            FileNotFoundError: se il file non esiste
        """
        with open(path, "r", encoding="utf-8") as f:
            return self.assemble_source(f.read())

    # internals
    def _split_label(self, code: str, lineno: int) -> tuple[str | None, str | None]:
        """Separa etichetta da istruzione in una riga di codice.
        
        Args:
            code: riga di codice assembly (senza commenti)
            lineno: numero riga per error reporting
            
        Returns:
            Tupla (etichetta, parte_istruzione) dove None indica assenza
        """
        # 1) Stile con due punti: "LABEL: INSTR ..." o solo "LABEL:"
        if ":" in code:
            left, right = code.split(":", 1)
            left = left.strip()
            right = right.strip()
            if left and LABEL_RE.match(left):
                return left, (right if right else None)
        # 2) Stile senza due punti: "LABEL INSTR ..." oppure solo "LABEL"
        parts = code.split()
        if not parts:
            return None, code
        first = parts[0]
        first_up = first.upper()
        # Se la prima parola è un mnemonico valido o DAT, NON è un'etichetta
        if first_up == "DAT" or first_up in INSTRUCTION_OPCODES:
            return None, code
        # Altrimenti, se è una parola valida come etichetta
        if LABEL_RE.match(first):
            rest = " ".join(parts[1:])
            return first, (rest if rest else None)
        return None, code

    def _parse_instruction(self, text: str, lineno: int) -> tuple[str, str | None]:
        """Analizza una parte di istruzione estraendo mnemonico e argomento.
        
        Args:
            text: testo dell'istruzione (senza etichetta)
            lineno: numero riga per error reporting
            
        Returns:
            Tupla (mnemonico_maiuscolo, argomento_o_None)
            
        Raises:
            AssemblerError: per istruzioni malformate o sconosciute
        """
        parts = text.split()
        if not parts:
            raise AssemblerError(f"Linea {lineno}: istruzione mancante")
        mnemonic = parts[0].upper()
        if mnemonic == "DAT":
            # DAT [val]
            if len(parts) > 2:
                raise AssemblerError(f"Linea {lineno}: DAT accetta al più un argomento")
            arg = parts[1] if len(parts) == 2 else None
            if arg is not None and not arg.isdigit():
                raise AssemblerError(f"Linea {lineno}: DAT richiede un numero 0..999")
            return mnemonic, arg
        if mnemonic not in INSTRUCTION_OPCODES:
            raise AssemblerError(f"Linea {lineno}: istruzione sconosciuta '{mnemonic}'")
        arg: str | None = None
        if len(parts) > 1:
            arg = parts[1]
        if len(parts) > 2:
            raise AssemblerError(f"Linea {lineno}: troppi argomenti")
        # Controlli base su arg presenza/assenza
        needs_arg = INSTRUCTION_OPCODES[mnemonic] in {1, 2, 3, 5, 6, 7, 8}
        if needs_arg and arg is None:
            raise AssemblerError(f"Linea {lineno}: l'istruzione {mnemonic} richiede un argomento")
        if (not needs_arg) and arg is not None:
            raise AssemblerError(f"Linea {lineno}: l'istruzione {mnemonic} non accetta argomenti")
        return mnemonic, arg

    def _encode(self, mnemonic: str, arg: str | None, labels: Dict[str, int], lineno: int) -> int:
        """Converte mnemonico e argomento in codice macchina LMC.
        
        Args:
            mnemonic: istruzione in maiuscolo (es. "ADD", "DAT")
            arg: argomento opzionale (numero o etichetta)
            labels: dizionario etichette->indirizzi
            lineno: numero riga per error reporting
            
        Returns:
            Codice macchina LMC (0-999)
            
        Raises:
            AssemblerError: per errori di codifica o riferimenti non risolti
        """
        if mnemonic == "DAT":
            if arg is None:
                return 0
            val = int(arg)
            if not (0 <= val <= 999):
                raise AssemblerError(f"Linea {lineno}: DAT fuori range {val}")
            return val
        code = INSTRUCTION_OPCODES[mnemonic]
        if code in {901, 902, 0}:
            return code
        # Istruzioni con operando
        addr = self._resolve_address(arg, labels, lineno)
        return code * 100 + addr

    def _resolve_address(self, token: str | None, labels: Dict[str, int], lineno: int) -> int:
        """Risolve un token (numero o etichetta) in un indirizzo memoria.
        
        Args:
            token: stringa da risolvere (numero 0-99 o nome etichetta)
            labels: dizionario etichette->indirizzi
            lineno: numero riga per error reporting
            
        Returns:
            Indirizzo memoria risolto (0-99)
            
        Raises:
            AssemblerError: per token non validi o etichette non trovate
        """
        assert token is not None
        # Prova numero diretto
        if token.isdigit():
            addr = int(token)
            if not (0 <= addr <= 99):
                raise AssemblerError(f"Linea {lineno}: indirizzo fuori range {addr}")
            return addr
        # Etichetta
        if LABEL_RE.match(token):
            key = token.upper()
            if key not in labels:
                raise AssemblerError(f"Linea {lineno}: etichetta sconosciuta '{token}'")
            return labels[key]
        raise AssemblerError(f"Linea {lineno}: argomento non valido '{token}'")
