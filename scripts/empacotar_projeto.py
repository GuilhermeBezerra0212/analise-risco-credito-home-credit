"""Cria o pacote final do projeto sem incluir dados brutos ou dependências locais."""

from __future__ import annotations

import zipfile
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "entrega" / "Projeto_Analise_Risco_Credito_Home_Credit.zip"

ARQUIVOS_RAIZ = [
    RAIZ / "README.md",
    RAIZ / "requirements-colab.txt",
    RAIZ / ".gitignore",
    RAIZ / "dados" / "README.md",
    RAIZ / "relatorios" / "auditoria_dados_recuperados.json",
]
PASTAS = [RAIZ / "notebooks", RAIZ / "scripts", RAIZ / "tests"]


def arquivos_do_pacote():
    for arquivo in ARQUIVOS_RAIZ:
        yield arquivo
    for pasta in PASTAS:
        for arquivo in sorted(pasta.rglob("*")):
            if arquivo.is_file() and "__pycache__" not in arquivo.parts and arquivo.suffix != ".pyc":
                yield arquivo


def main() -> None:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SAIDA, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as pacote:
        for arquivo in arquivos_do_pacote():
            if not arquivo.exists():
                raise FileNotFoundError(arquivo)
            pacote.write(arquivo, arquivo.relative_to(RAIZ).as_posix())

    with zipfile.ZipFile(SAIDA) as pacote:
        corrompido = pacote.testzip()
        if corrompido:
            raise ValueError(f"Falha de integridade no pacote: {corrompido}")
        print(f"OK: {len(pacote.infolist())} arquivos empacotados")
    print(f"Pacote: {SAIDA}")
    print(f"Tamanho: {SAIDA.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()

