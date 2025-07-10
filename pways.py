"""
Como usar:
Digitar no cmd: 'Python /pways <p> <input.txt> <output.txt> e esperar a exibir a saída (tempo esperado: 15 a 30 segundos).'

Destaques da especificação
-----------------------
* Apenas <p> registros são mantidos na RAM ao mesmo tempo.
* No máximo 2 p arquivos são abertos simultaneamente.
* As sequências iniciais são geradas com seleção por substituição.
* As passagens subsequentes utilizam intercalação p‑caminhos baseada em heap mínima.
* Funciona com qualquer entrada de inteiros separados por espaços (um por linha ou vários por linha)
  e nunca realiza ordenação completa em memória.
* Após gerar o arquivo de saída completamente ordenado, imprime exatamente a linha de relatório exigida:
        #Regs Ways #Runs #Parses
"""

from __future__ import annotations
import heapq
import os
import sys
import tempfile
from pathlib import Path
from typing import List, TextIO, Tuple, IO


INF = float("inf")


def _read_next_int(f: TextIO):
    """
        Função para lidar com diferentes formatos de entrada.
    """

    if not hasattr(f, "_buffer_tokens"):
        f._buffer_tokens = []  # type: ignore[attr-defined]

    while True:
        if f._buffer_tokens:  # type: ignore[attr-defined]
            return int(f._buffer_tokens.pop(0))  # type: ignore[attr-defined]

        line = f.readline()
        if not line:
            return None
        f._buffer_tokens = line.split()  # type: ignore[attr-defined]


# Seleção por substituição para gerar sequências ordenadas iniciais

def replacement_selection(input_path: str | Path, p: int) -> Tuple[List[str], int]:
    """
        Gera sequências ordenadas iniciais usando seleção por substituição.
        Retorna `(caminhos_das_sequencias, total_de_registros)`.
    """
    run_paths: List[str] = []
    num_records = 0

    with open(input_path, "r", encoding="utf-8") as infile:
        active_heap: List[int] = []
        for _ in range(p):
            val = _read_next_int(infile)
            if val is None:
                break
            heapq.heappush(active_heap, val)
            num_records += 1

        if not active_heap:  # arquivo vazio
            return run_paths, num_records

        next_heap: List[int] = []  # heap para os próximos registros
        last_output = -INF

        # Cria um arquivo temporário para armazenar a sequência atual
        tmp = tempfile.NamedTemporaryFile("w", delete=False, prefix="run_", suffix=".tmp")
        run_file: IO[str] = tmp

        while active_heap:
            smallest = heapq.heappop(active_heap)
            print(smallest, file=run_file)
            last_output = smallest

            # Mantenha o heap ativo com registros maiores ou iguais ao último output
            next_val = _read_next_int(infile)
            if next_val is not None:
                num_records += 1
                target_heap = active_heap if next_val >= last_output else next_heap
                heapq.heappush(target_heap, next_val)

            # Se o heap ativo estiver vazio, mova os registros do próximo heap
            if not active_heap:
                run_file.close()
                run_paths.append(run_file.name)
                if next_heap:
                    active_heap, next_heap = next_heap, []
                    last_output = -INF
                    tmp = tempfile.NamedTemporaryFile(
                        "w", delete=False, prefix="run_", suffix=".tmp"
                    )
                    run_file = tmp

        if not run_file.closed:
            run_file.close()
            run_paths.append(run_file.name)

    return run_paths, num_records


# Intercalação p‑caminhos para mesclar sequências ordenadas

def _merge_group(run_paths: List[str], p: int) -> str:
    """
        Mescla um grupo de sequências ordenadas usando intercalação p‑caminhos.
    """

    out_tmp = tempfile.NamedTemporaryFile("w", delete=False, prefix="run_", suffix=".tmp")
    out_path = out_tmp.name


    files = [open(path, "r", encoding="utf-8") for path in run_paths]

    heap: List[Tuple[int, int]] = []
    for idx, f in enumerate(files):
        val = _read_next_int(f)
        if val is not None:
            heapq.heappush(heap, (val, idx))

    while heap:
        val, idx = heapq.heappop(heap)
        print(val, file=out_tmp)
        nxt = _read_next_int(files[idx])
        if nxt is not None:
            heapq.heappush(heap, (nxt, idx))

    for f in files:
        f.close()
    out_tmp.close()
    for path in run_paths:
        os.remove(path)

    return out_path


def pway_merge(run_paths: List[str], p: int, output_path: str | Path) -> int:
    """
        Realiza a intercalação p‑caminhos iterativa até que reste apenas uma sequência.
    """
    passes = 0
    current_runs = run_paths

    while len(current_runs) > 1:
        passes += 1
        new_runs: List[str] = []
        for i in range(0, len(current_runs), p):
            group = current_runs[i : i + p]
            merged = _merge_group(group, p)
            new_runs.append(merged)
        current_runs = new_runs

    final_run = current_runs[0]
    os.replace(final_run, output_path)
    return passes


def main(argv: List[str]):
    if len(argv) != 4:
        print("Usage: pways <p> <input_file> <output_file>")
        sys.exit(1)

    try:
        p = int(argv[1])
        if p < 2:
            raise ValueError
    except ValueError:
        print("Error: p must be an integer ≥ 2")
        sys.exit(1)

    input_path, output_path = argv[2], argv[3]

    # Fase 1: seleção por substituição
    run_paths, num_records = replacement_selection(input_path, p)
    num_runs = len(run_paths)

    # Fase 2: intercalação p‑caminhos
    num_passes = pway_merge(run_paths, p, output_path)

    # Fase 3: saída
    print("#Regs Ways #Runs #Parses")
    print(f"{num_records:<5} {p:<5} {num_runs:<5} {num_passes:<5}")


if __name__ == "__main__":
    main(sys.argv)
