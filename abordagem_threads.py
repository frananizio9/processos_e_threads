"""Abordagem 2: multithreading (threads concorrentes no mesmo processo)."""
from concurrent.futures import ThreadPoolExecutor

from calculo import combinar, dividir_intervalos, ler_cabecalho, processar_bloco


def executar(caminho, n_workers):
    idx = ler_cabecalho(caminho)
    tarefas = [(caminho, i, f, idx) for i, f in dividir_intervalos(caminho, n_workers)]
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        parciais = list(pool.map(processar_bloco, tarefas))
    return combinar(parciais)
