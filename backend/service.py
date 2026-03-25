import pandas as pd
from collections import defaultdict

# =========================
# NORMALIZAÇÃO
# =========================
def normalizar_nota(valor):
    if pd.isna(valor):
        return None
    return str(valor).strip().zfill(9)

def extrair_codigo_c197(linha):
    return linha.split("|")[2].strip()

def extrair_nota(linha):
    return normalizar_nota(linha.split("|")[8])

# =========================
# MAPAS
# =========================
MAPA_C195 = {
    "MG23000999": ("3", "Débito para a sub-apuração"),
    "MG53000999": ("1", "Crédito para a sub-apuração"),
    "MG50000999": ("2", "Estorno de crédito devido à devolução de mercadoria alcançada com o crédito presumido")
}

MAPA_0460 = {
    "1": "|0460|1|Crédito para a sub-apuração|\n",
    "2": "|0460|2|Devolução de mercadoria alcançada com o crédito presumido|\n",
    "3": "|0460|3|Estorno de débito - e-PTA n. 45.000304995-7|\n"
}

# =========================
# FUNÇÃO PRINCIPAL
# =========================
def processar_sped(arquivo_sped, arquivo_excel, saida):

    df = pd.read_excel(arquivo_excel, dtype=str)
    mapa_notas = defaultdict(list)

    for _, row in df.iterrows():
        nota = normalizar_nota(row.iloc[12])
        linha = row.iloc[10]

        if nota and isinstance(linha, str) and linha.startswith("|C197|"):
            linha = linha.strip()
            if not linha.endswith("|"):
                linha += "|"
            mapa_notas[nota].append(linha + "\n")

    with open(arquivo_sped, "r", encoding="latin1") as f:
        linhas = f.readlines()

    resultado = []
    bloco = []
    nota_atual = None
    dentro_bloco_c = False

    codigos_gerais = set()
    qtd_c195 = 0
    qtd_c197 = 0

    for linha in linhas:

        if linha.startswith("|C001|"):
            dentro_bloco_c = True

        if linha.startswith("|C990|"):
            dentro_bloco_c = False

        if linha.startswith("|C100|") and dentro_bloco_c:
            if bloco and nota_atual:
                if nota_atual in mapa_notas:
                    grupos = defaultdict(list)

                    for c in mapa_notas[nota_atual]:
                        codigo = extrair_codigo_c197(c)
                        grupos[codigo].append(c)

                    for codigo, lista in grupos.items():
                        if codigo in MAPA_C195:
                            cod, desc = MAPA_C195[codigo]

                            bloco.append(f"|C195|{cod}|{desc}|\n")
                            qtd_c195 += 1
                            codigos_gerais.add(cod)

                            bloco.extend(lista)
                            qtd_c197 += len(lista)

                resultado.extend(bloco)
                bloco = []

            nota_atual = extrair_nota(linha)

        if not linha.endswith("\n"):
            linha += "\n"

        bloco.append(linha)

    if bloco:
        resultado.extend(bloco)

    pos_0990 = next(i for i, l in enumerate(resultado) if l.startswith("|0990|"))

    linhas_0460 = [MAPA_0460[c] for c in sorted(codigos_gerais)]
    qtd_0460 = len(linhas_0460)

    resultado = resultado[:pos_0990] + linhas_0460 + resultado[pos_0990:]

    for i, l in enumerate(resultado):
        if l.startswith("|0990|"):
            partes = l.split("|")
            partes[2] = str(int(partes[2]) + qtd_0460)
            resultado[i] = "|".join(partes)

    qtd_linhas_c = sum(1 for l in resultado if l.startswith("|C"))

    for i, l in enumerate(resultado):
        if l.startswith("|C990|"):
            resultado[i] = f"|C990|{qtd_linhas_c}|\n"

    pos_0220 = next(i for i, l in enumerate(resultado) if l.startswith("|9900|0220|"))

    if qtd_0460 > 0:
        resultado.insert(pos_0220 + 1, f"|9900|0460|{qtd_0460}|\n")

    pos_9900_c990 = next(i for i, l in enumerate(resultado) if l.startswith("|9900|C990|"))

    if qtd_c195 > 0:
        resultado.insert(pos_9900_c990, f"|9900|C195|{qtd_c195}|\n")
        pos_9900_c990 += 1

    if qtd_c197 > 0:
        resultado.insert(pos_9900_c990, f"|9900|C197|{qtd_c197}|\n")

    total_linhas = len(resultado)

    for i, l in enumerate(resultado):
        if l.startswith("|9999|"):
            resultado[i] = f"|9999|{total_linhas}|\n"

    incremento = 0

    if qtd_c195 > 0:
        incremento += 1
    if qtd_c197 > 0:
        incremento += 1
    if qtd_0460 > 0:
        incremento += 1

    for i, l in enumerate(resultado):
        if l.startswith("|9900|9900|"):
            partes = l.split("|")
            partes[3] = str(int(partes[3]) + incremento)
            resultado[i] = "|".join(partes)

        if l.startswith("|9990|"):
            partes = l.split("|")
            partes[2] = str(int(partes[2]) + incremento)
            resultado[i] = "|".join(partes)

    with open(saida, "w", encoding="latin1") as f:
        f.writelines(resultado)