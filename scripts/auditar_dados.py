"""Gera uma auditoria compacta dos CSVs recuperados do Home Credit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


CHAVES = {
    "application_train.csv": ["SK_ID_CURR"],
    "application_test.csv": ["SK_ID_CURR"],
    "bureau.csv": ["SK_ID_CURR", "SK_ID_BUREAU"],
    "bureau_balance.csv": ["SK_ID_BUREAU"],
    "credit_card_balance.csv": ["SK_ID_CURR", "SK_ID_PREV"],
    "POS_CASH_balance.csv": ["SK_ID_CURR", "SK_ID_PREV"],
    "HomeCredit_columns_description.csv": [],
}

CATEGORICAS_DESTAQUE = {
    "application_train.csv": [
        "TARGET",
        "NAME_CONTRACT_TYPE",
        "CODE_GENDER",
        "NAME_INCOME_TYPE",
        "NAME_EDUCATION_TYPE",
    ],
    "bureau.csv": ["CREDIT_ACTIVE", "CREDIT_TYPE"],
    "bureau_balance.csv": ["STATUS"],
    "credit_card_balance.csv": ["NAME_CONTRACT_STATUS"],
    "POS_CASH_balance.csv": ["NAME_CONTRACT_STATUS"],
}


def valor_json(valor):
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return None if np.isnan(valor) else float(valor)
    return valor


def auditar_csv(caminho: Path, tamanho_chunk: int = 500_000) -> tuple[dict, dict[str, set]]:
    nome = caminho.name
    codificacao = "latin1" if nome == "HomeCredit_columns_description.csv" else "utf-8"
    n_linhas = 0
    ausentes: Counter[str] = Counter()
    conjuntos_chaves = {chave: set() for chave in CHAVES.get(nome, [])}
    contagens_categoricas = {
        coluna: Counter() for coluna in CATEGORICAS_DESTAQUE.get(nome, [])
    }
    colunas: list[str] = []
    tipos: dict[str, str] = {}

    for indice, chunk in enumerate(
        pd.read_csv(
            caminho,
            chunksize=tamanho_chunk,
            low_memory=False,
            encoding=codificacao,
        )
    ):
        if indice == 0:
            colunas = chunk.columns.tolist()
            tipos = {coluna: str(tipo) for coluna, tipo in chunk.dtypes.items()}
        n_linhas += len(chunk)
        ausentes.update(chunk.isna().sum().astype(int).to_dict())

        for chave, valores in conjuntos_chaves.items():
            if chave in chunk:
                valores.update(chunk[chave].dropna().astype("int64").tolist())

        for coluna, contador in contagens_categoricas.items():
            if coluna in chunk:
                contador.update(chunk[coluna].fillna("<AUSENTE>").astype(str).tolist())

    top_ausentes = sorted(
        (
            {
                "coluna": coluna,
                "quantidade": int(quantidade),
                "percentual": round(quantidade / n_linhas * 100, 4) if n_linhas else 0.0,
            }
            for coluna, quantidade in ausentes.items()
            if quantidade
        ),
        key=lambda item: item["quantidade"],
        reverse=True,
    )[:15]

    resumo = {
        "arquivo": nome,
        "tamanho_mb": round(caminho.stat().st_size / 1024**2, 2),
        "linhas": n_linhas,
        "colunas": len(colunas),
        "nomes_colunas": colunas,
        "tipos_amostra": tipos,
        "celulas_ausentes": int(sum(ausentes.values())),
        "percentual_celulas_ausentes": round(
            sum(ausentes.values()) / (n_linhas * len(colunas)) * 100, 4
        ) if n_linhas and colunas else 0.0,
        "top_15_colunas_ausentes": top_ausentes,
        "chaves_unicas": {chave: len(valores) for chave, valores in conjuntos_chaves.items()},
        "categorias_destaque": {
            coluna: [
                {"valor": valor, "quantidade": quantidade}
                for valor, quantidade in contador.most_common(15)
            ]
            for coluna, contador in contagens_categoricas.items()
        },
    }
    return resumo, conjuntos_chaves


def estatisticas_aplicacao(caminho: Path) -> dict:
    colunas = [
        "TARGET",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "DAYS_BIRTH",
        "DAYS_EMPLOYED",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
    ]
    dados = pd.read_csv(caminho, usecols=colunas)
    dias_emprego_validos = dados["DAYS_EMPLOYED"].where(dados["DAYS_EMPLOYED"] >= -36500)
    fontes = dados[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)
    return {
        "taxa_inadimplencia": round(float(dados["TARGET"].mean()), 6),
        "inadimplentes": int(dados["TARGET"].sum()),
        "adimplentes": int((dados["TARGET"] == 0).sum()),
        "idade_mediana_anos": round(float((-dados["DAYS_BIRTH"] / 365.25).median()), 2),
        "renda_mediana": round(float(dados["AMT_INCOME_TOTAL"].median()), 2),
        "credito_mediano": round(float(dados["AMT_CREDIT"].median()), 2),
        "anuidade_mediana": round(float(dados["AMT_ANNUITY"].median()), 2),
        "tempo_emprego_mediano_anos": round(float((-dias_emprego_validos / 365.25).median()), 2),
        "fonte_externa_media_adimplentes": round(float(fontes[dados["TARGET"] == 0].mean()), 6),
        "fonte_externa_media_inadimplentes": round(float(fontes[dados["TARGET"] == 1].mean()), 6),
    }


def cobertura(conjuntos: dict[str, dict[str, set]]) -> dict:
    treino = conjuntos["application_train.csv"]["SK_ID_CURR"]
    teste = conjuntos["application_test.csv"]["SK_ID_CURR"]
    resultado = {}
    for nome in ["bureau.csv", "credit_card_balance.csv", "POS_CASH_balance.csv"]:
        clientes = conjuntos[nome]["SK_ID_CURR"]
        resultado[nome] = {
            "clientes_unicos": len(clientes),
            "cobertura_treino_percentual": round(len(treino & clientes) / len(treino) * 100, 4),
            "cobertura_teste_percentual": round(len(teste & clientes) / len(teste) * 100, 4),
        }

    bureaus_com_saldo = conjuntos["bureau_balance.csv"]["SK_ID_BUREAU"]
    bureaus = conjuntos["bureau.csv"]["SK_ID_BUREAU"]
    resultado["bureau_balance.csv"] = {}
    resultado["bureau_balance.csv"]["cobertura_bureau_percentual"] = round(
        len(bureaus & bureaus_com_saldo) / len(bureaus) * 100, 4
    )
    resultado["bureau_balance.csv"]["ids_bureau_unicos"] = len(bureaus_com_saldo)
    return resultado


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("diretorio_dados", type=Path)
    parser.add_argument("arquivo_saida", type=Path)
    args = parser.parse_args()

    arquivos = sorted(args.diretorio_dados.glob("*.csv"))
    auditorias = []
    conjuntos: dict[str, dict[str, set]] = {}

    for caminho in arquivos:
        print(f"Auditando {caminho.name}...")
        resumo, chaves = auditar_csv(caminho)
        auditorias.append(resumo)
        conjuntos[caminho.name] = chaves

    resultado = {
        "auditoria": auditorias,
        "estatisticas_application_train": estatisticas_aplicacao(
            args.diretorio_dados / "application_train.csv"
        ),
        "cobertura_relacional": cobertura(conjuntos),
        "observacao": (
            "O ZIP de origem está truncado. Installments_payments.csv é parcial e "
            "previous_application.csv e sample_submission.csv não foram recuperados."
        ),
    }

    args.arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    args.arquivo_saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=valor_json),
        encoding="utf-8",
    )
    print(f"Auditoria salva em {args.arquivo_saida}")


if __name__ == "__main__":
    main()

