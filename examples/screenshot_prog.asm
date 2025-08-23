LOAD   LDA 0
       OUT
       SUB ONE
       BRZ END
       LDA LOAD
       ADD ONE
       STA LOAD
       BRA LOAD
END    HLT
ONE    DAT 1
