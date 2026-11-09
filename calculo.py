import csv
import os
from collections import defaultdict

SEP = ";"
ENCODING = "utf-8"

COL_VOTOS = "QT_VOTOS"
COL_NUMERO = "NR_VOTAVEL"
COL_NOME = "NM_VOTAVEL"
COL_CARGO = "DS_CARGO"

SIGLAS = {
    "10": "REPUBLICANOS", "11": "PP", "12": "PDT", "13": "PT", "14": "MISSÃO",
    "15": "MDB", "16": "PSTU", "18": "REDE", "20": "PODE", "22": "PL",
    "23": "CIDADANIA", "25": "PRD", "27": "DC", "29": "PCO", "30": "NOVO",
    "33": "MOBILIZA", "36": "AGIR", "40": "PSB", "43": "PV", "44": "UNIÃO",
    "45": "PSDB", "50": "PSOL", "55": "PSD", "65": "PCdoB", "70": "AVANTE",
    "77": "SOLIDARIEDADE", "80": "UP",
}
NUMEROS_BRANCO_NULO = {"95", "96"}

def ler_cabecalho(caminho):
    with open(caminho, "r", encoding="utf-8-sig", newline="") as f:
        cols = next(csv.reader(f, delimiter=SEP))
    return {nome: i for i, nome in enumerate(cols)}

def dividir_intervalos(caminho, n):
    tam = os.path.getsize(caminho)
    passo = max(1, tam // n)
    limites = [i * passo for i in range(n)] + [tam]
    return list(zip(limites[:-1], limites[1:]))

def _linhas_do_intervalo(caminho, inicio, fim):
    with open(caminho, "rb") as f:
        if inicio > 0:
            f.seek(inicio - 1)
            f.readline()
        while f.tell() < fim:
            linha = f.readline()
            if not linha:
                break
            yield linha.decode(ENCODING)

def processar_bloco(args):
    caminho, inicio, fim, idx = args
    i_votos, i_num, i_cargo = idx[COL_VOTOS], idx[COL_NUMERO], idx[COL_CARGO]
    total = [0, 0]
    por_partido = defaultdict(lambda: [0, 0])
    por_cargo = defaultdict(lambda: [0, 0])

    for linha in _linhas_do_intervalo(caminho, inicio, fim):
        linha = linha.lstrip("\ufeff").rstrip("\r\n")
        if not linha or linha.startswith("DT_GERACAO"):
            continue
        campos = next(csv.reader([linha], delimiter=SEP))
        numero = campos[i_num].strip()
        if numero in NUMEROS_BRANCO_NULO or len(numero) <= 2:
            continue
        votos = int(campos[i_votos])
        partido = SIGLAS.get(numero[:2], "Nº " + numero[:2])
        cargo = campos[i_cargo].strip()

        total[0] += votos; total[1] += 1
        por_partido[partido][0] += votos; por_partido[partido][1] += 1
        por_cargo[cargo][0] += votos; por_cargo[cargo][1] += 1

    return total[0], total[1], dict(por_partido), dict(por_cargo)

def combinar(parciais):
    soma = n = 0
    partidos = defaultdict(lambda: [0, 0])
    cargos = defaultdict(lambda: [0, 0])
    for s, c, p, g in parciais:
        soma += s; n += c
        for k, (a, b) in p.items():
            partidos[k][0] += a; partidos[k][1] += b
        for k, (a, b) in g.items():
            cargos[k][0] += a; cargos[k][1] += b
    return {
        "media_geral": soma / n if n else 0.0,
        "registos": n,
        "medias_partido": {k: a / b for k, (a, b) in partidos.items()},
        "medias_cargo": {k: a / b for k, (a, b) in cargos.items()},
    }
