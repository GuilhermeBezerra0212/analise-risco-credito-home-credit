"""Executa o notebook em modo rápido com os dados íntegros recuperados."""

from __future__ import annotations

import json
import os
import sys
import argparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "notebooks" / "Projeto_Analise_Risco_Credito_Home_Credit.ipynb"
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=RAIZ / "dados" / "raw_recuperados",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RAIZ / "resultados_smoke",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=RAIZ / "validacao" / "smoke_ok.json",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(RAIZ / "validacao" / "python_deps"))
    os.environ["HOME_CREDIT_DATA_DIR"] = str(args.data_dir.resolve())
    os.environ["HOME_CREDIT_OUTPUT_DIR"] = str(args.output_dir.resolve())
    os.environ["HOME_CREDIT_MODE"] = "rapido"
    os.environ["HOME_CREDIT_STRICT"] = "1" if args.strict else "0"

    os.environ["MPLBACKEND"] = "Agg"
    os.chdir(RAIZ)

    notebook = json.loads(ORIGEM.read_text(encoding="utf-8"))
    namespace = {"__name__": "__notebook_smoke__"}
    codigos = [c for c in notebook["cells"] if c["cell_type"] == "code"]

    for indice, celula in enumerate(codigos, start=1):
        codigo = "".join(celula["source"])
        print(f"Executando célula {indice}/{len(codigos)}...", flush=True)
        exec(compile(codigo, f"celula_{indice}", "exec"), namespace)

    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    resumo = {
        "status": "ok",
        "celulas_codigo_executadas": len(codigos),
        "modelo_selecionado": namespace["nome_vencedor"],
        "metricas_teste": {k: float(v) for k, v in namespace["metricas_teste"].items()},
        "artefatos": namespace["artefatos"],
        "arquivos_ausentes_declarados": namespace["faltantes"],
    }
    args.evidence.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: notebook executado de ponta a ponta. Evidência: {args.evidence}")


if __name__ == "__main__":
    main()

