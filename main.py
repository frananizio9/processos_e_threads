import argparse
import os
import statistics
import time

import abordagem_processos
import abordagem_threads


def cronometrar(funcao, caminho, workers, repeticoes):
    tempos, resultado = [], None
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        resultado = funcao(caminho, workers)
        tempos.append(time.perf_counter() - t0)
    return resultado, statistics.mean(tempos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ficheiro", nargs="?", default="votacao_candidato_munzona_2026_SP.csv")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--repeticoes", type=int, default=5,
                    help="nº de execuções por abordagem (usa-se o tempo médio)")
    a = ap.parse_args()

    res_proc, t_proc = cronometrar(abordagem_processos.executar, a.ficheiro, a.workers, a.repeticoes)
    res_thr, t_thr = cronometrar(abordagem_threads.executar, a.ficheiro, a.workers, a.repeticoes)

    assert res_proc == res_thr, "As duas abordagens devem dar o mesmo resultado"
    r = res_proc
    melhor_partido = max(r["medias_partido"], key=r["medias_partido"].get)
    melhor_cargo = max(r["medias_cargo"], key=r["medias_cargo"].get)

    print(f"Ficheiro: {a.ficheiro} | registos considerados: {r['registos']} | "
          f"workers: {a.workers} | repetições: {a.repeticoes}")
    print("-" * 70)
    print(f"Média geral (QT_VOTOS nominais válidos): {r['media_geral']:.4f}")
    print(f"Partido com a maior média: {melhor_partido} "
          f"({r['medias_partido'][melhor_partido]:.4f})")
    print(f"Cargo com a maior média:   {melhor_cargo} "
          f"({r['medias_cargo'][melhor_cargo]:.4f})")
    print("-" * 70)
    print(f"Tempo (processos): {t_proc:.4f} s")
    print(f"Tempo (threads):   {t_thr:.4f} s")
    if t_proc < t_thr:
        print(f">>> Melhor desempenho: PROCESSOS ({t_thr / t_proc:.2f}x mais rápido)")
    elif t_thr < t_proc:
        print(f">>> Melhor desempenho: THREADS ({t_proc / t_thr:.2f}x mais rápido)")
    else:
        print(">>> Empate técnico")

    print("\nMédias por partido:")
    for k, v in sorted(r["medias_partido"].items(), key=lambda x: -x[1]):
        print(f"  {k:<15} {v:10.4f}")
    print("\nMédias por cargo:")
    for k, v in sorted(r["medias_cargo"].items(), key=lambda x: -x[1]):
        print(f"  {k:<20} {v:10.4f}")


if __name__ == "__main__":
    main()
