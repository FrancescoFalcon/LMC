# Francesco Falcon SM3201408

class LMCError(Exception):
    """Errore base per il simulatore LMC."""


class IllegalInstructionError(LMCError):
    """Istruzione non valida trovata in memoria."""
    def __init__(self, pc: int, opcode: int):
        super().__init__(f"Istruzione non valida {opcode} alla cella {pc}")
        self.pc = pc
        self.opcode = opcode


class MemoryErrorLMC(LMCError):
    """Errore di accesso alla memoria del LMC."""
    pass


class InputUnderflowError(LMCError):
    """Coda di input vuota durante un'operazione di input."""
    pass


class AssemblerError(LMCError):
    """Errore generato dall'assembler per problemi di sintassi o riferimenti."""
    pass
