// Conta da 0 a n (incluso)
START:   INP          // leggi n
          STA N
          LDA ZERO
          STA I       // i = 0
PRINT:    LDA I
          OUT          // stampa i
          LDA I
          ADD ONE
          STA I       // i += 1
CHECK:    LDA N
          SUB I       // calcola N - I
          BRP PRINT   // se >= 0 (flag assente), continua
          HLT

// dati
ZERO:     DAT 0
ONE:      DAT 1
N:        DAT 0
I:        DAT 0
