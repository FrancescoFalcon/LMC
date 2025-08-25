# Francesco Falcon SM3201408

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional

from .exceptions import (
    LMCError,
    IllegalInstructionError,
    MemoryErrorLMC,
    InputUnderflowError,
)


@dataclass
class LMC:
    """Simulatore di Little Man Computer (LMC)."""

    memory: List[int] = field(default_factory=lambda: [0] * 100)
    accumulator: int = 0
    pc: int = 0
    flag: bool = False  # negativo: True se l'ultimo risultato aritmetico è negativo
    input_queue: Deque[int] = field(default_factory=deque)
    output_queue: Deque[int] = field(default_factory=deque)

    def reset(self, memory: Optional[List[int]] = None, inputs: Optional[List[int]] = None):
        """Reinizializza lo stato della macchina.

        Args:
            memory: opzionale, lista di 100 interi (0..999). Se None, mantiene la corrente.
            inputs: opzionale, lista di interi da caricare come coda di input.
        """
        if memory is not None:
            if len(memory) != 100:
                raise MemoryErrorLMC("La memoria deve avere 100 celle")
            for i, v in enumerate(memory):
                if not (0 <= v <= 999):
                    raise MemoryErrorLMC(f"Valore memoria fuori range in cella {i}: {v}")
            self.memory = list(memory)
        self.accumulator = 0
        self.pc = 0
        self.flag = False
        self.input_queue.clear()
        self.output_queue.clear()
        if inputs:
            for v in inputs:
                self.push_input(v)

    def push_input(self, value: int):
        """Inserisce un valore nella coda di input (0..999)."""
        if not (0 <= value <= 999):
            raise ValueError(f"Input fuori range: {value}")
        self.input_queue.append(value)

    def pop_output(self) -> Optional[int]:
        """Estrae un valore dalla coda di output se presente."""
        return self.output_queue.popleft() if self.output_queue else None

    def step(self) -> bool:
        """Esegue una singola istruzione. Ritorna False se HALT, True altrimenti.

    Istruzioni secondo specifica:
        - 1xx: ADD xx
        - 2xx: SUB xx
        - 3xx: STA xx (STORE)
        - 5xx: LDA xx (LOAD)
        - 6xx: BRA xx (branch always)
        - 7xx: BRZ xx (branch if zero: dipende solo da ACC==0)
        - 8xx: BRP xx (branch if positive/zero: dipende da flag negativo assente)
        - 901: INP
        - 902: OUT
        - 000: HLT
        Tutti i valori 400..499 e altri non mappati: illegal instruction.
        """
        opcode = self._read_mem(self.pc)
        next_pc = (self.pc + 1) % 100

        if opcode == 0:
            # HLT
            return False

        hundred = opcode // 100
        arg = opcode % 100

        if opcode == 901:
            # INP: non modifica il flag
            if not self.input_queue:
                raise InputUnderflowError("Coda di input vuota durante INP")
            self.accumulator = self.input_queue.popleft()
            self.pc = next_pc
            return True
        if opcode == 902:
            # OUT
            v = self._clamp(self.accumulator)
            self.output_queue.append(v)
            self.pc = next_pc
            return True

        if hundred == 1:  # ADD
            self._arith(self.accumulator + self._read_mem(arg))
            self.pc = next_pc
            return True
        if hundred == 2:  # SUB
            self._arith(self.accumulator - self._read_mem(arg))
            self.pc = next_pc
            return True
        if hundred == 3:  # STA
            self._write_mem(arg, self._clamp(self.accumulator))
            self.pc = next_pc
            return True
        if hundred == 5:  # LDA: non modifica il flag
            self.accumulator = self._read_mem(arg)
            self.pc = next_pc
            return True
        if hundred == 6:  # BRA
            self._jump(arg)
            return True
        if hundred == 7:  # BRZ: salta se ACC==0 (ignora il flag)
            if self._clamp(self.accumulator) == 0:
                self._jump(arg)
            else:
                self.pc = next_pc
            return True
        if hundred == 8:  # BRP: salta se l'ultimo risultato non è negativo (flag==False)
            if not self.flag:
                self._jump(arg)
            else:
                self.pc = next_pc
            return True

        # Se arriviamo qui: illegal instruction
        raise IllegalInstructionError(self.pc, opcode)

    def run(self, max_steps: int = 10000):
        """Esegue fino a HALT o fino a max_steps per evitare loop infiniti."""
        steps = 0
        while steps < max_steps and self.step():
            steps += 1
        return steps

    # Helpers
    def _arith(self, value: int):
        """Aggiorna accumulatore e flag negativo in base al risultato aritmetico.

        Il flag indica solo la negatività del risultato prima del clamp:
        - flag = True se value < 0 (risultato negativo)
        - flag = False se value >= 0 (risultato non negativo), anche in caso di overflow positivo

        Args:
            value: risultato dell'operazione aritmetica (può essere fuori range)

        Effetti:
            - self.accumulator viene clampato nel range 0-999 (mod 1000)
            - self.flag viene impostato in base a (value < 0)
        """
        self.flag = value < 0
        self.accumulator = self._clamp(value)

    @staticmethod
    def _clamp(value: int) -> int:
        """Applica modulo 1000 per mantenere valori nel range LMC.
        
        Args:
            value: valore intero qualsiasi
            
        Returns:
            Valore modulo 1000 (range 0-999)
        """
        return value % 1000

    def _jump(self, addr: int):
        """Esegue un salto incondizionato del program counter.
        
        Args:
            addr: indirizzo di destinazione (0-99)
            
        Output:
            Modifica self.pc con il nuovo indirizzo
            
        Raises:
            MemoryErrorLMC: se addr fuori range 0-99
        """
        if not (0 <= addr <= 99):
            raise MemoryErrorLMC(f"Indirizzo di salto fuori range: {addr}")
        self.pc = addr

    def _read_mem(self, addr: int) -> int:
        """Legge un valore dalla memoria con controlli di validità.
        
        Args:
            addr: indirizzo memoria da leggere (0-99)
            
        Returns:
            Valore contenuto nella cella di memoria (0-999)
            
        Raises:
            MemoryErrorLMC: se addr fuori range o contenuto memoria non valido
        """
        if not (0 <= addr <= 99):
            raise MemoryErrorLMC(f"Accesso memoria fuori range: {addr}")
        v = self.memory[addr]
        if not (0 <= v <= 999):
            raise MemoryErrorLMC(f"Valore in memoria fuori range in {addr}: {v}")
        return v

    def _write_mem(self, addr: int, value: int):
        """Scrive un valore in memoria con controlli di validità.
        
        Args:
            addr: indirizzo memoria di destinazione (0-99)
            value: valore da scrivere (0-999)
            
        Output:
            Modifica self.memory[addr] con il nuovo valore
            
        Raises:
            MemoryErrorLMC: se addr o value fuori range
        """
        if not (0 <= addr <= 99):
            raise MemoryErrorLMC(f"Accesso memoria fuori range: {addr}")
        if not (0 <= value <= 999):
            raise MemoryErrorLMC(f"Scrittura fuori range: {value}")
        self.memory[addr] = value
