"""Abordagem 1: multiprocessing (processos independentes, sem GIL partilhado)."""
from multiprocessing import Pool

from calculo import combinar, dividir_intervalos, ler_cabecalho, processar_bloco


def executar(caminho, n_workers):
    idx = ler_cabecalho(caminho)
    tarefas = [(caminho, i, f, idx) for i, f in dividir_intervalos(caminho, n_workers)]
    with Pool(processes=n_workers) as pool:
        parciais = pool.map(processar_bloco, tarefas)
    return combinar(parciais)
