"""Valida estrutura, sintaxe e requisitos essenciais do notebook entregue."""

from __future__ import annotations

import json
import io
import tokenize
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOK = RAIZ / "notebooks" / "Projeto_Analise_Risco_Credito_Home_Credit.ipynb"


def main() -> None:
    documento = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert documento["nbformat"] == 4
    assert len(documento["cells"]) >= 30

    texto_total = "\n".join("".join(celula.get("source", [])) for celula in documento["cells"])
    obrigatorios = [
        "application_train.csv",
        "application_test.csv",
        "bureau.csv",
        "bureau_balance.csv",
        "previous_application.csv",
        "POS_CASH_balance.csv",
        "credit_card_balance.csv",
        "installments_payments.csv",
        "sample_submission.csv",
        "portao_qualidade",
        "Dá para melhorar?",
        "Regressão logística",
        "Gradient boosting",
        "manifesto_modelo.json",
    ]
    ausentes = [item for item in obrigatorios if item not in texto_total]
    assert not ausentes, f"Conteúdos obrigatórios ausentes: {ausentes}"
    assert "C:\\Users\\Guilherme" not in texto_total, "O notebook contém caminho local do autor."

    codigos = [c for c in documento["cells"] if c["cell_type"] == "code"]
    linhas_narradas = 0
    for indice, celula in enumerate(codigos, start=1):
        codigo = "".join(celula["source"])
        compile(codigo, f"celula_codigo_{indice}", "exec")

        linhas = codigo.splitlines()
        dentro_de_string: set[int] = set()
        for token in tokenize.generate_tokens(io.StringIO(codigo).readline):
            if token.type == tokenize.STRING and token.end[0] > token.start[0]:
                dentro_de_string.update(range(token.start[0] + 1, token.end[0] + 1))

        for numero, linha in enumerate(linhas, start=1):
            trecho = linha.strip()
            if not trecho or trecho.startswith("#") or numero in dentro_de_string:
                continue
            assert numero > 1 and linhas[numero - 2].lstrip().startswith("#"), (
                f"Célula {indice}, linha {numero} não possui comentário narrativo imediatamente antes."
            )
            linhas_narradas += 1

    print(
        f"OK: {len(documento['cells'])} células; {len(codigos)} células de código compiladas; "
        f"{linhas_narradas} linhas executáveis com comentário narrativo."
    )


if __name__ == "__main__":
    main()

