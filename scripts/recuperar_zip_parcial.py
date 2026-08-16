"""Recupera entradas completas de um ZIP truncado sem alterar o arquivo original."""

from __future__ import annotations

import argparse
import binascii
import struct
import zlib
from pathlib import Path


ASSINATURA_ARQUIVO_LOCAL = 0x04034B50
TAMANHO_CABECALHO = 30
TAMANHO_BLOCO = 1024 * 1024


def ler_tamanhos_zip64(extra: bytes, comprimido_32: int, original_32: int) -> tuple[int, int]:
    comprimido, original = comprimido_32, original_32
    posicao = 0
    while posicao + 4 <= len(extra):
        identificador, tamanho = struct.unpack_from("<HH", extra, posicao)
        posicao += 4
        campo = extra[posicao : posicao + tamanho]
        posicao += tamanho
        if identificador != 0x0001:
            continue

        cursor = 0
        if original_32 == 0xFFFFFFFF:
            original = struct.unpack_from("<Q", campo, cursor)[0]
            cursor += 8
        if comprimido_32 == 0xFFFFFFFF:
            comprimido = struct.unpack_from("<Q", campo, cursor)[0]
        return comprimido, original

    if comprimido_32 == 0xFFFFFFFF or original_32 == 0xFFFFFFFF:
        raise ValueError("Entrada ZIP64 sem campo de tamanhos.")
    return comprimido, original


def caminho_seguro(destino: Path, nome: str) -> Path:
    candidato = (destino / nome).resolve()
    raiz = destino.resolve()
    if candidato != raiz and raiz not in candidato.parents:
        raise ValueError(f"Caminho inseguro no ZIP: {nome!r}")
    return candidato


def extrair(arquivo_zip: Path, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    tamanho_zip = arquivo_zip.stat().st_size
    recuperados = 0

    with arquivo_zip.open("rb") as origem:
        while origem.tell() + TAMANHO_CABECALHO <= tamanho_zip:
            deslocamento = origem.tell()
            cabecalho = origem.read(TAMANHO_CABECALHO)
            (
                assinatura,
                _versao,
                flags,
                metodo,
                _hora,
                _data,
                crc_esperado,
                comprimido_32,
                original_32,
                tamanho_nome,
                tamanho_extra,
            ) = struct.unpack("<IHHHHHIIIHH", cabecalho)

            if assinatura != ASSINATURA_ARQUIVO_LOCAL:
                break

            codificacao = "utf-8" if flags & 0x0800 else "cp437"
            nome = origem.read(tamanho_nome).decode(codificacao)
            extra = origem.read(tamanho_extra)
            comprimido, original = ler_tamanhos_zip64(extra, comprimido_32, original_32)
            inicio_dados = origem.tell()
            fim_dados = inicio_dados + comprimido

            if fim_dados > tamanho_zip:
                disponivel = max(tamanho_zip - inicio_dados, 0)
                print(
                    f"INCOMPLETO | {nome} | disponível {disponivel:,} de {comprimido:,} bytes"
                )
                break

            saida = caminho_seguro(destino, nome)
            saida.parent.mkdir(parents=True, exist_ok=True)
            temporario = saida.with_name(saida.name + ".part")
            temporario.unlink(missing_ok=True)

            if metodo == 8:
                descompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            elif metodo == 0:
                descompressor = None
            else:
                raise ValueError(f"Método de compressão {metodo} não suportado em {nome}.")

            restante = comprimido
            crc_calculado = 0
            bytes_gravados = 0
            with temporario.open("wb") as arquivo_saida:
                while restante:
                    bloco = origem.read(min(TAMANHO_BLOCO, restante))
                    if not bloco:
                        raise EOFError(f"Fim inesperado durante a leitura de {nome}.")
                    restante -= len(bloco)
                    dados = descompressor.decompress(bloco) if descompressor else bloco
                    arquivo_saida.write(dados)
                    crc_calculado = binascii.crc32(dados, crc_calculado)
                    bytes_gravados += len(dados)

                if descompressor:
                    dados_finais = descompressor.flush()
                    arquivo_saida.write(dados_finais)
                    crc_calculado = binascii.crc32(dados_finais, crc_calculado)
                    bytes_gravados += len(dados_finais)

            if bytes_gravados != original or crc_calculado & 0xFFFFFFFF != crc_esperado:
                temporario.unlink(missing_ok=True)
                raise ValueError(f"Falha de integridade ao recuperar {nome}.")

            temporario.replace(saida)
            recuperados += 1
            print(f"OK        | {nome} | {bytes_gravados:,} bytes")
            origem.seek(fim_dados)

    print(f"\n{recuperados} arquivo(s) íntegro(s) recuperado(s) em: {destino}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo_zip", type=Path)
    parser.add_argument("destino", type=Path)
    argumentos = parser.parse_args()
    extrair(argumentos.arquivo_zip, argumentos.destino)


if __name__ == "__main__":
    main()

