# p-way-merge-sort-algorithm
Repositório para entrega de trabalho

Como usar:
----------
Digite no terminal:

    python /pways <p> <input.txt> <output.txt>

e aguarde a saída ser exibida (tempo estimado: 15 a 30 segundos).

Destaques da especificação:
---------------------------
* Apenas *p* registros são mantidos na RAM ao mesmo tempo.
* No máximo 2*p* arquivos são abertos simultaneamente.
* As sequências iniciais são geradas com seleção por substituição.
* As passagens subsequentes utilizam intercalação p‑caminhos baseada em heap mínima.
* Funciona com qualquer entrada de inteiros separados por espaços (um por linha ou vários por linha).
* Nunca realiza ordenação completa em memória.
* Após gerar o arquivo de saída completamente ordenado, imprime exatamente a linha de relatório exigida:

        #Regs Ways #Runs #Parses
