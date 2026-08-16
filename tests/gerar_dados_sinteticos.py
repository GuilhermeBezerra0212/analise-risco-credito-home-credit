"""Gera uma base pequena para testar todos os ramos do notebook, sem valor analítico."""

from __future__ import annotations

import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "validacao" / "python_deps"))

import numpy as np
import pandas as pd


DESTINO = RAIZ / "validacao" / "dados_sinteticos_completos"
RNG = np.random.default_rng(42)


def aplicacoes(ids: np.ndarray, com_alvo: bool) -> pd.DataFrame:
    n = len(ids)
    idade = RNG.integers(22, 70, n)
    renda = RNG.lognormal(np.log(150_000), 0.45, n)
    credito = renda * RNG.uniform(1.2, 5.5, n)
    fonte_2 = RNG.beta(4, 3, n)
    fonte_3 = RNG.beta(3, 3, n)
    dados = pd.DataFrame({
        "SK_ID_CURR": ids,
        "DAYS_BIRTH": -(idade * 365 + RNG.integers(0, 365, n)),
        "DAYS_EMPLOYED": -RNG.integers(30, 9_000, n),
        "DAYS_REGISTRATION": -RNG.integers(30, 12_000, n),
        "AMT_INCOME_TOTAL": renda,
        "AMT_CREDIT": credito,
        "AMT_ANNUITY": credito / RNG.uniform(10, 35, n),
        "AMT_GOODS_PRICE": credito * RNG.uniform(0.85, 1.05, n),
        "CNT_FAM_MEMBERS": RNG.integers(1, 6, n).astype(float),
        "EXT_SOURCE_1": RNG.beta(3, 3, n),
        "EXT_SOURCE_2": fonte_2,
        "EXT_SOURCE_3": fonte_3,
        "NAME_CONTRACT_TYPE": RNG.choice(["Cash loans", "Revolving loans"], n, p=[0.9, 0.1]),
        "CODE_GENDER": RNG.choice(["F", "M"], n, p=[0.65, 0.35]),
        "NAME_INCOME_TYPE": RNG.choice(["Working", "Commercial associate", "Pensioner"], n),
        "NAME_EDUCATION_TYPE": RNG.choice(["Secondary / secondary special", "Higher education"], n),
    })
    dados.loc[RNG.choice(n, max(1, n // 12), replace=False), "EXT_SOURCE_1"] = np.nan
    dados.loc[RNG.choice(n, max(1, n // 20), replace=False), "DAYS_EMPLOYED"] = 365243
    if com_alvo:
        logito = -2.4 + 2.0 * (1 - fonte_2) + 1.2 * (1 - fonte_3) + 0.12 * (credito / renda)
        prob = 1 / (1 + np.exp(-logito))
        dados["TARGET"] = RNG.binomial(1, np.clip(prob, 0.03, 0.7))
    return dados


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ids_treino = np.arange(100001, 101001)
    ids_teste = np.arange(200001, 200201)
    todos_ids = np.concatenate([ids_treino, ids_teste])

    treino = aplicacoes(ids_treino, True)
    teste = aplicacoes(ids_teste, False)
    treino.to_csv(DESTINO / "application_train.csv", index=False)
    teste.to_csv(DESTINO / "application_test.csv", index=False)

    linhas_bureau = []
    linhas_saldo = []
    id_bureau = 500001
    for cliente in todos_ids:
        for _ in range(int(RNG.integers(1, 4))):
            credito = float(RNG.uniform(10_000, 500_000))
            divida = credito * float(RNG.uniform(0, 1))
            linhas_bureau.append({
                "SK_ID_CURR": cliente,
                "SK_ID_BUREAU": id_bureau,
                "CREDIT_ACTIVE": RNG.choice(["Active", "Closed"]),
                "AMT_CREDIT_SUM_OVERDUE": max(0, float(RNG.normal(500, 2_000))),
                "AMT_CREDIT_SUM": credito,
                "AMT_CREDIT_SUM_DEBT": divida,
                "DAYS_CREDIT": -int(RNG.integers(10, 3_000)),
                "CNT_CREDIT_PROLONG": int(RNG.integers(0, 3)),
            })
            for mes in range(-int(RNG.integers(2, 9)), 1):
                linhas_saldo.append({
                    "SK_ID_BUREAU": id_bureau,
                    "MONTHS_BALANCE": mes,
                    "STATUS": RNG.choice(["C", "0", "1", "2"], p=[0.35, 0.5, 0.12, 0.03]),
                })
            id_bureau += 1
    pd.DataFrame(linhas_bureau).to_csv(DESTINO / "bureau.csv", index=False)
    pd.DataFrame(linhas_saldo).to_csv(DESTINO / "bureau_balance.csv", index=False)

    anteriores = []
    pos = []
    cartao = []
    parcelas = []
    id_prev = 700001
    for cliente in todos_ids:
        for _ in range(int(RNG.integers(1, 4))):
            solicitado = float(RNG.uniform(5_000, 400_000))
            concedido = solicitado * float(RNG.uniform(0.7, 1.1))
            anteriores.append({
                "SK_ID_CURR": cliente,
                "SK_ID_PREV": id_prev,
                "NAME_CONTRACT_STATUS": RNG.choice(["Approved", "Refused"], p=[0.75, 0.25]),
                "AMT_APPLICATION": solicitado,
                "AMT_CREDIT": concedido,
                "AMT_ANNUITY": concedido / float(RNG.uniform(6, 30)),
                "AMT_DOWN_PAYMENT": solicitado * float(RNG.uniform(0, 0.25)),
                "CNT_PAYMENT": int(RNG.integers(6, 37)),
                "DAYS_DECISION": -int(RNG.integers(5, 2_000)),
            })
            for numero, mes in enumerate(range(-int(RNG.integers(2, 8)), 1), start=1):
                dpd = max(0, int(RNG.normal(2, 8)))
                pos.append({
                    "SK_ID_CURR": cliente,
                    "SK_ID_PREV": id_prev,
                    "MONTHS_BALANCE": mes,
                    "CNT_INSTALMENT_FUTURE": max(0, 12 - numero),
                    "SK_DPD": dpd,
                    "SK_DPD_DEF": max(0, dpd - 3),
                    "NAME_CONTRACT_STATUS": "Completed" if numero >= 12 else "Active",
                })
                limite = float(RNG.uniform(10_000, 100_000))
                cartao.append({
                    "SK_ID_CURR": cliente,
                    "SK_ID_PREV": id_prev,
                    "MONTHS_BALANCE": mes,
                    "AMT_BALANCE": limite * float(RNG.uniform(0, 1.2)),
                    "AMT_CREDIT_LIMIT_ACTUAL": limite,
                    "AMT_DRAWINGS_CURRENT": float(RNG.uniform(0, 10_000)),
                    "AMT_PAYMENT_CURRENT": float(RNG.uniform(0, 12_000)),
                    "SK_DPD": dpd,
                })
                vencimento = -30 * numero
                atraso = max(0, int(RNG.normal(1, 6)))
                valor = float(RNG.uniform(500, 15_000))
                parcelas.append({
                    "SK_ID_CURR": cliente,
                    "SK_ID_PREV": id_prev,
                    "NUM_INSTALMENT_NUMBER": numero,
                    "DAYS_INSTALMENT": vencimento,
                    "DAYS_ENTRY_PAYMENT": vencimento + atraso,
                    "AMT_INSTALMENT": valor,
                    "AMT_PAYMENT": valor * float(RNG.uniform(0.85, 1.05)),
                })
            id_prev += 1

    pd.DataFrame(anteriores).to_csv(DESTINO / "previous_application.csv", index=False)
    pd.DataFrame(pos).to_csv(DESTINO / "POS_CASH_balance.csv", index=False)
    pd.DataFrame(cartao).to_csv(DESTINO / "credit_card_balance.csv", index=False)
    pd.DataFrame(parcelas).to_csv(DESTINO / "installments_payments.csv", index=False)
    pd.DataFrame({"SK_ID_CURR": ids_teste, "TARGET": 0.5}).to_csv(DESTINO / "sample_submission.csv", index=False)

    descricao = pd.DataFrame({
        "Table": ["application_{train|test}.csv", "previous_application.csv", "installments_payments.csv"],
        "Row": ["SK_ID_CURR", "SK_ID_PREV", "AMT_PAYMENT"],
        "Description": ["Identificador do cliente", "Identificador da proposta anterior", "Valor pago"],
        "Special": [np.nan, np.nan, np.nan],
    })
    descricao.to_csv(DESTINO / "HomeCredit_columns_description.csv", index=False, encoding="latin1")
    print(f"OK: base sintética completa criada em {DESTINO}")


if __name__ == "__main__":
    main()

