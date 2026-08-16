"""Constrói o notebook Colab narrativo do projeto Home Credit."""

from __future__ import annotations

import json
import io
import re
import textwrap
import tokenize
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "notebooks" / "Projeto_Analise_Risco_Credito_Home_Credit.ipynb"


def fonte(texto: str) -> list[str]:
    texto = textwrap.dedent(texto).strip() + "\n"
    return texto.splitlines(keepends=True)


def markdown(texto: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": fonte(texto)}


def comentario_narrativo(linha: str) -> str:
    """Explica o papel de uma linha sem repetir mecanicamente sua sintaxe."""
    trecho = linha.strip()
    if trecho.startswith("from "):
        modulo = trecho.split()[1]
        return f"Trazemos de `{modulo}` as ferramentas que sustentam esta parte da análise."
    if trecho.startswith("import "):
        modulo = trecho.removeprefix("import ").split(" as ")[0].split(",")[0]
        return f"Convidamos `{modulo}` para participar deste capítulo do processamento."
    if trecho.startswith("def "):
        nome = trecho.split("def ", 1)[1].split("(", 1)[0]
        return f"Criamos a função `{nome}` para transformar esta ideia em uma etapa reutilizável."
    if trecho.startswith("return ") or trecho == "return":
        return "Devolvemos o resultado construído para que a próxima etapa possa continuar a história."
    if trecho.startswith("if "):
        return "Testamos esta condição para escolher com segurança o próximo caminho da narrativa."
    if trecho.startswith("elif "):
        return "Avaliamos uma alternativa porque a condição anterior não descreveu este caso."
    if trecho.startswith("else"):
        return "Seguimos pelo caminho alternativo quando a condição anterior não se confirma."
    if trecho.startswith("for "):
        return "Percorremos cada elemento para aplicar a mesma regra de forma consistente."
    if trecho.startswith("while "):
        return "Repetimos a operação enquanto a condição indicar que a etapa ainda não terminou."
    if trecho.startswith("try"):
        return "Tentamos executar a operação principal, preparados para explicar uma eventual falha."
    if trecho.startswith("except "):
        return "Traduzimos a falha técnica em uma mensagem clara e acionável para quem executa o projeto."
    if trecho.startswith("with "):
        return "Abrimos este recurso de forma controlada para garantir que ele seja encerrado corretamente."
    if trecho.startswith("raise "):
        return "Interrompemos a história aqui, pois avançar com esta inconsistência produziria uma conclusão frágil."
    if trecho.startswith("del "):
        return "Liberamos da memória o que já cumpriu seu papel para manter o Colab leve."
    if trecho.startswith("print("):
        return "Contamos ao leitor o estado atual da execução para que nenhum passo aconteça no escuro."
    if trecho.startswith("display("):
        return "Apresentamos o resultado em formato visual para transformar cálculo em comunicação."
    if trecho.startswith(("fig,", "fig =", "plt.", "sns.")):
        return "Preparamos a visualização que dará forma ao argumento construído pelos dados."
    if trecho.startswith("ax") or trecho.startswith("axes"):
        return "Refinamos o gráfico para que a mensagem visual seja direta e elegante."
    if ".fit(" in trecho:
        return "Ensinamos o modelo usando somente as observações reservadas para aprendizagem."
    if ".predict_proba(" in trecho:
        return "Pedimos ao modelo probabilidades de risco, preservando a riqueza do score contínuo."
    if trecho.startswith("portao_qualidade("):
        return "Abrimos o portão de qualidade que decidirá se esta etapa está madura para avançar."
    atribuicao = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", trecho)
    if atribuicao:
        nome = atribuicao.group(1)
        if nome.isupper():
            return f"Fixamos `{nome}` como uma decisão explícita e fácil de ajustar pelo leitor."
        return f"Guardamos em `{nome}` a evidência produzida por esta operação."
    chave = re.match(r"[\"']([^\"']+)[\"']\s*:", trecho)
    if chave:
        return f"Registramos `{chave.group(1)}` para manter esta informação nomeada e auditável."
    if trecho.startswith("."):
        return "Encadeamos mais uma transformação, mantendo o fluxo de leitura de cima para baixo."
    if trecho[0:1] in {"\"", "'"} and trecho.rstrip(",").endswith(("\"", "'")):
        return "Incluímos este elemento na coleção que organiza os componentes da etapa."
    if trecho in {")", "]", "}", "),", "],", "},", "))", ")),", "}).", "})"} or trecho.startswith(("),", "],", "},")):
        return "Fechamos a estrutura iniciada nas linhas anteriores e consolidamos seu significado."
    if trecho.startswith(("#", "@")):
        return "Documentamos a intenção desta instrução para orientar quem revisa o projeto."
    return "Damos continuidade a esta etapa com a operação necessária para sustentar a conclusão seguinte."


def comentar_linha_a_linha(texto: str) -> str:
    """Insere um comentário narrativo antes de cada linha executável."""
    texto = textwrap.dedent(texto).strip()
    linhas = texto.splitlines()
    linhas_dentro_de_strings: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(texto).readline):
            if token.type == tokenize.STRING and token.end[0] > token.start[0]:
                linhas_dentro_de_strings.update(range(token.start[0] + 1, token.end[0] + 1))
    except tokenize.TokenError:
        pass

    narrado: list[str] = []
    for numero, linha in enumerate(linhas, start=1):
        trecho = linha.strip()
        if not trecho or trecho.startswith("#") or numero in linhas_dentro_de_strings:
            narrado.append(linha)
            continue
        recuo = linha[: len(linha) - len(linha.lstrip())]
        narrado.append(f"{recuo}# {comentario_narrativo(linha)}")
        narrado.append(linha)
    return "\n".join(narrado) + "\n"


def codigo(texto: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": comentar_linha_a_linha(texto).splitlines(keepends=True),
    }


celulas: list[dict] = []

celulas.append(markdown(r'''
<div style="background:linear-gradient(135deg,#081C2C 0%,#0E4D64 58%,#137C8B 100%);padding:38px 42px;border-radius:20px;color:white;box-shadow:0 12px 28px rgba(8,28,44,.22)">
  <div style="font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#B9E3E8">Projeto end-to-end • Ciência de dados aplicada</div>
  <h1 style="font-size:38px;line-height:1.12;margin:12px 0 8px">Risco de crédito<br>da evidência à decisão</h1>
  <p style="font-size:18px;max-width:820px;color:#E6F4F6;margin:0">Uma análise do Home Credit Default Risk que conecta histórico financeiro, comportamento de pagamento e modelagem preditiva — com rigor técnico, narrativa executiva e código simples.</p>
  <div style="margin-top:24px;font-size:13px;color:#B9E3E8">Google Colab • Python • PT-BR • versão reproduzível</div>
</div>

> **Pergunta central:** como reconhecer sinais de dificuldade de pagamento antes da decisão de crédito, sem transformar o modelo em uma caixa-preta?
'''))

celulas.append(markdown(r'''
## Roteiro da apresentação

| Capítulo | Pergunta que vamos responder | Entrega |
|---|---|---|
| 1. Contexto e dados | O que existe e como as tabelas se conectam? | Inventário, qualidade e mapa relacional |
| 2. Retrato do risco | Quem inadimple e quais sinais aparecem primeiro? | Análise exploratória orientada ao negócio |
| 3. Memória financeira | O histórico acrescenta informação útil? | Engenharia de atributos de todas as bases |
| 4. Modelo | Conseguimos ordenar clientes por risco? | Baseline interpretável + modelo não linear |
| 5. Decisão | Qual limiar traduz o score em uma política? | Curvas, custos, decis e matriz de confusão |
| 6. Confiança | O resultado é explicável e governável? | Importância, auditoria por grupos e artefatos |

Cada capítulo termina com um **portão de qualidade**. Se a resposta a “dá para melhorar?” for “sim”, a execução para; só avançamos quando a resposta for “não”.
'''))

celulas.append(markdown(r'''
## 0. Preparação do ambiente

No Colab, a forma mais estável é colocar `homecredit.zip` no Google Drive. Altere apenas as variáveis da próxima célula. O notebook também aceita uma pasta já descompactada por meio da variável de ambiente `HOME_CREDIT_DATA_DIR`.

O modo **completo** usa todos os registros. O modo **rápido** reduz apenas a amostra de modelagem; as agregações históricas continuam corretas.
'''))

celulas.append(codigo(r'''
from pathlib import Path
import json
import os
import sys
import time
import warnings
import zipfile

EM_COLAB = "google.colab" in sys.modules
USAR_GOOGLE_DRIVE = False  # Troque para True no Colab se o ZIP estiver no Drive.

CAMINHO_ZIP = Path(os.getenv(
    "HOME_CREDIT_ZIP",
    "/content/drive/MyDrive/homecredit.zip" if EM_COLAB else "homecredit.zip",
))
DIRETORIO_DADOS = Path(os.getenv(
    "HOME_CREDIT_DATA_DIR",
    "/content/home_credit_dados" if EM_COLAB else "dados/raw",
))
PASTA_RESULTADOS = Path(os.getenv(
    "HOME_CREDIT_OUTPUT_DIR",
    "/content/resultados_risco_credito" if EM_COLAB else "resultados",
))

MODO_EXECUCAO = os.getenv("HOME_CREDIT_MODE", "completo")  # completo ou rapido
EXIGIR_BASE_COMPLETA = os.getenv("HOME_CREDIT_STRICT", "1") == "1"
RANDOM_STATE = 42
CUSTO_FALSO_POSITIVO = 1
CUSTO_FALSO_NEGATIVO = 5  # Hipótese ilustrativa; deve ser calibrada pela instituição.

if EM_COLAB and USAR_GOOGLE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")

print(f"Ambiente: {'Google Colab' if EM_COLAB else 'local'}")
print(f"Modo: {MODO_EXECUCAO} | Exigir base completa: {EXIGIR_BASE_COMPLETA}")
'''))

celulas.append(codigo(r'''
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from IPython.display import HTML, Markdown, display
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 140)
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")

CORES = {
    "marinho": "#0B1F33",
    "azul": "#0E4D64",
    "turquesa": "#137C8B",
    "coral": "#FF6B5E",
    "dourado": "#E6A23C",
    "cinza": "#667785",
    "claro": "#EAF3F5",
}
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({
    "figure.figsize": (10, 5),
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.labelcolor": CORES["marinho"],
    "axes.edgecolor": "#D7E2E6",
    "text.color": CORES["marinho"],
    "font.family": "DejaVu Sans",
})

def br_numero(valor, casas=0):
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def portao_qualidade(etapa, criterios):
    falhas = [descricao for descricao, passou in criterios.items() if not bool(passou)]
    if falhas:
        display(HTML(
            f"<div style='border-left:5px solid {CORES['coral']};padding:14px 18px;background:#FFF3F1'>"
            f"<b>{etapa} — Dá para melhorar? Sim.</b><br>" + "<br>".join(f"• {x}" for x in falhas) + "</div>"
        ))
        raise AssertionError("O portão de qualidade encontrou pendências. Corrija antes de avançar.")
    display(HTML(
        f"<div style='border-left:5px solid {CORES['turquesa']};padding:14px 18px;background:#EEF8F7'>"
        f"<b>{etapa} — Dá para melhorar? Não.</b><br>Todos os critérios definidos para esta etapa foram atendidos.</div>"
    ))
'''))

celulas.append(markdown(r'''
## 1. A matéria-prima da decisão

O Home Credit não descreve apenas uma proposta. Ele registra uma trajetória: a solicitação atual, os créditos vistos pelo bureau, empréstimos anteriores na própria instituição e o comportamento mensal de pagamentos. A unidade final da decisão é o **cliente (`SK_ID_CURR`)**; todas as tabelas históricas serão resumidas para essa granularidade antes da modelagem.
'''))

celulas.append(codigo(r'''
ARQUIVOS_ESPERADOS = [
    "HomeCredit_columns_description.csv",
    "application_train.csv",
    "application_test.csv",
    "bureau.csv",
    "bureau_balance.csv",
    "previous_application.csv",
    "POS_CASH_balance.csv",
    "credit_card_balance.csv",
    "installments_payments.csv",
    "sample_submission.csv",
]

def extrair_zip_com_seguranca(caminho_zip, destino):
    if not caminho_zip.exists():
        raise FileNotFoundError(
            f"ZIP não encontrado em {caminho_zip}. Ajuste CAMINHO_ZIP ou HOME_CREDIT_DATA_DIR."
        )
    destino.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(caminho_zip) as arquivo:
            corrompido = arquivo.testzip()
            if corrompido:
                raise zipfile.BadZipFile(f"Entrada corrompida: {corrompido}")
            raiz = destino.resolve()
            for membro in arquivo.infolist():
                alvo = (destino / membro.filename).resolve()
                if alvo != raiz and raiz not in alvo.parents:
                    raise ValueError(f"Caminho inseguro dentro do ZIP: {membro.filename}")
            arquivo.extractall(destino)
    except zipfile.BadZipFile as erro:
        raise zipfile.BadZipFile(
            "O arquivo ZIP está incompleto ou corrompido. Baixe-o novamente no Kaggle antes de executar."
        ) from erro

if not (DIRETORIO_DADOS / "application_train.csv").exists():
    extrair_zip_com_seguranca(CAMINHO_ZIP, DIRETORIO_DADOS)

ARQUIVOS = {p.name: p for p in DIRETORIO_DADOS.rglob("*.csv")}
faltantes = [nome for nome in ARQUIVOS_ESPERADOS if nome not in ARQUIVOS]

if faltantes:
    mensagem = "Arquivos ausentes: " + ", ".join(faltantes)
    if EXIGIR_BASE_COMPLETA:
        raise FileNotFoundError(mensagem + ". Use um download completo ou desative o modo estrito conscientemente.")
    display(HTML(f"<div style='background:#FFF8E8;padding:14px;border-left:5px solid {CORES['dourado']}'><b>Modo tolerante:</b> {mensagem}. O notebook seguirá sem inventar dados e registrará a limitação.</div>"))

print(f"{len(ARQUIVOS)} CSV(s) localizado(s) em {DIRETORIO_DADOS}")
'''))

celulas.append(codigo(r'''
def contar_linhas_csv(caminho, tamanho_bloco=8 * 1024 * 1024):
    linhas = 0
    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(tamanho_bloco):
            linhas += bloco.count(b"\n")
    return max(linhas - 1, 0)

inventario = []
for nome, caminho in sorted(ARQUIVOS.items()):
    codificacao = "latin1" if nome == "HomeCredit_columns_description.csv" else "utf-8"
    cabecalho = pd.read_csv(caminho, nrows=0, encoding=codificacao)
    inventario.append({
        "dataset": nome,
        "linhas": contar_linhas_csv(caminho),
        "colunas": len(cabecalho.columns),
        "tamanho_mb": caminho.stat().st_size / 1024**2,
    })

inventario = pd.DataFrame(inventario).sort_values("linhas", ascending=False)
display(
    inventario.style
    .format({"linhas": "{:,.0f}", "colunas": "{:,.0f}", "tamanho_mb": "{:,.1f}"})
    .background_gradient(subset=["linhas"], cmap="GnBu")
    .hide(axis="index")
)
'''))

celulas.append(markdown(r'''
### Como as tabelas conversam

<div style="display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:14px;align-items:stretch">
  <div style="background:#F2F7F8;padding:16px;border-radius:12px"><b>Bureau externo</b><br><code>bureau</code><br><code>bureau_balance</code><br><small>Chaves: SK_ID_CURR → SK_ID_BUREAU</small></div>
  <div style="background:#0E4D64;color:white;padding:18px;border-radius:12px;text-align:center"><b>Decisão atual</b><br><code style="color:#B9E3E8">application_train / test</code><br><small>Uma linha por SK_ID_CURR</small></div>
  <div style="background:#F2F7F8;padding:16px;border-radius:12px"><b>Histórico interno</b><br><code>previous_application</code><br><code>POS_CASH</code> • <code>credit_card</code> • <code>installments</code><br><small>Chaves: SK_ID_CURR / SK_ID_PREV</small></div>
</div>

O `TARGET` vale 1 quando houve dificuldade de pagamento. Ele existe somente em `application_train` e nunca será usado na criação de atributos históricos.
'''))

celulas.append(codigo(r'''
app_train = pd.read_csv(ARQUIVOS["application_train.csv"], low_memory=False)
app_test = pd.read_csv(ARQUIVOS["application_test.csv"], low_memory=False)

dicionario = None
if "HomeCredit_columns_description.csv" in ARQUIVOS:
    dicionario = pd.read_csv(
        ARQUIVOS["HomeCredit_columns_description.csv"],
        encoding="latin1",
    )

portao_qualidade("Etapa 1 — Integridade e relações", {
    "application_train não foi carregado": len(app_train) > 0,
    "application_test não foi carregado": len(app_test) > 0,
    "SK_ID_CURR não é único no treino": app_train["SK_ID_CURR"].is_unique,
    "SK_ID_CURR não é único no teste": app_test["SK_ID_CURR"].is_unique,
    "TARGET contém valores além de 0 e 1": set(app_train["TARGET"].dropna().unique()) == {0, 1},
    "Há clientes simultaneamente em treino e teste": len(set(app_train["SK_ID_CURR"]) & set(app_test["SK_ID_CURR"])) == 0,
    "A base completa exigida ainda tem arquivos ausentes": (not EXIGIR_BASE_COMPLETA) or not faltantes,
})
'''))

celulas.append(markdown(r'''
## 2. O retrato do risco

Antes de prever, precisamos dimensionar o evento. Inadimplência é rara o suficiente para tornar a acurácia enganosa: um modelo que dissesse “ninguém terá dificuldade” acertaria a maioria e seria inútil. Por isso, as métricas centrais serão **ROC AUC**, **PR AUC**, **KS**, sensibilidade e calibração.
'''))

celulas.append(codigo(r'''
taxa_inadimplencia = app_train["TARGET"].mean()
contagem_target = app_train["TARGET"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(8.5, 4.5))
barras = ax.bar(
    ["Sem dificuldade", "Com dificuldade"],
    contagem_target.values,
    color=[CORES["turquesa"], CORES["coral"]],
    width=0.58,
)
ax.set_title("O evento de risco é minoritário — e isso muda a avaliação")
ax.set_ylabel("Clientes")
ax.grid(axis="x", visible=False)
for barra, valor in zip(barras, contagem_target.values):
    ax.text(barra.get_x() + barra.get_width()/2, valor, br_numero(valor), ha="center", va="bottom", fontweight="bold")
ax.text(0.99, 0.93, f"Taxa de inadimplência: {taxa_inadimplencia:.2%}", transform=ax.transAxes, ha="right", color=CORES["coral"], fontweight="bold")
sns.despine()
plt.show()

display(Markdown(
    f"**Leitura executiva.** Há **{br_numero(contagem_target.get(1, 0))}** clientes com dificuldade "
    f"entre **{br_numero(len(app_train))}** observações — uma prevalência de **{taxa_inadimplencia:.2%}**."
))
'''))

celulas.append(codigo(r'''
ausencias = app_train.isna().mean().sort_values(ascending=False)
top_ausencias = ausencias.head(20).sort_values()
anomalia_emprego = int((app_train["DAYS_EMPLOYED"] == 365243).sum())

fig, ax = plt.subplots(figsize=(9, 6.2))
ax.barh(top_ausencias.index, top_ausencias.values * 100, color=CORES["azul"])
ax.set_title("Concentração de ausências: características do imóvel dominam o topo")
ax.set_xlabel("Valores ausentes (%)")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0f}%")
sns.despine()
plt.show()

resumo_qualidade = pd.DataFrame({
    "indicador": ["Células ausentes", "Colunas com > 65% de ausência", "Sentinela 365243 em DAYS_EMPLOYED"],
    "valor": [
        f"{app_train.isna().sum().sum() / app_train.size:.2%}",
        int((ausencias > 0.65).sum()),
        br_numero(anomalia_emprego),
    ],
})
display(resumo_qualidade.style.hide(axis="index"))
'''))

celulas.append(codigo(r'''
eda = app_train[[
    "TARGET", "DAYS_BIRTH", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
    "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "NAME_CONTRACT_TYPE",
]].copy()
eda["IDADE_ANOS"] = -eda["DAYS_BIRTH"] / 365.25
eda["MEDIA_FONTES_EXTERNAS"] = eda[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].mean(axis=1)
eda["FAIXA_ETARIA"] = pd.cut(eda["IDADE_ANOS"], [20, 30, 40, 50, 60, 70], right=False)
eda["FAIXA_RENDA"] = pd.qcut(eda["AMT_INCOME_TOTAL"].rank(method="first"), 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

taxa_idade = eda.groupby("FAIXA_ETARIA", observed=True)["TARGET"].mean()
taxa_idade.plot(kind="bar", ax=axes[0,0], color=CORES["azul"], rot=0)
axes[0,0].set_title("Risco observado por faixa etária")
axes[0,0].set_xlabel("Idade")
axes[0,0].set_ylabel("Taxa de dificuldade")

taxa_renda = eda.groupby("FAIXA_RENDA", observed=True)["TARGET"].mean()
taxa_renda.plot(kind="bar", ax=axes[0,1], color=CORES["turquesa"], rot=0)
axes[0,1].set_title("Risco observado por quintil de renda")
axes[0,1].set_xlabel("Quintil de renda")
axes[0,1].set_ylabel("")

sns.kdeplot(data=eda.sample(min(100_000, len(eda)), random_state=RANDOM_STATE), x="MEDIA_FONTES_EXTERNAS", hue="TARGET", common_norm=False, fill=False, palette=[CORES["turquesa"], CORES["coral"]], ax=axes[1,0])
axes[1,0].set_title("Fontes externas separam parte do risco")
axes[1,0].set_xlabel("Média das fontes externas")

taxa_contrato = eda.groupby("NAME_CONTRACT_TYPE")["TARGET"].mean().sort_values()
taxa_contrato.plot(kind="barh", ax=axes[1,1], color=CORES["dourado"])
axes[1,1].set_title("Risco por modalidade do contrato")
axes[1,1].set_xlabel("Taxa de dificuldade")
axes[1,1].set_ylabel("")

for ax in axes.flat:
    ax.yaxis.set_major_formatter(lambda y, pos: f"{y:.0%}" if y < 1 else f"{y:.0f}")
sns.despine()
plt.tight_layout()
plt.show()

media_ext = eda.groupby("TARGET")["MEDIA_FONTES_EXTERNAS"].mean()
display(Markdown(
    f"**Primeiro sinal forte.** A média das fontes externas cai de **{media_ext.get(0, np.nan):.3f}** "
    f"entre clientes sem dificuldade para **{media_ext.get(1, np.nan):.3f}** entre os inadimplentes. "
    "A relação é descritiva, não causal."
))
'''))

celulas.append(codigo(r'''
if dicionario is not None:
    tabela_coluna = next((c for c in dicionario.columns if c.lower() == "table"), None)
    if tabela_coluna:
        display(
            dicionario.groupby(tabela_coluna, dropna=False)
            .size().rename("variaveis_documentadas")
            .sort_values(ascending=False).to_frame()
        )
    display(dicionario.head(8))

portao_qualidade("Etapa 2 — Entendimento e qualidade", {
    "A taxa do evento não foi calculada": 0 < taxa_inadimplencia < 1,
    "As ausências não foram quantificadas": len(ausencias) == app_train.shape[1],
    "A sentinela de DAYS_EMPLOYED não foi identificada": anomalia_emprego > 0,
    "As fontes externas não foram comparadas por TARGET": media_ext.notna().all(),
})
'''))

celulas.append(markdown(r'''
## 3. A memória financeira do cliente

Uma linha da proposta atual não conta toda a história. Vamos converter milhões de registros históricos em atributos simples por cliente: quantidade de contratos, exposição, saldo, utilização de limite, atraso, severidade e recência. Não usamos o `TARGET` em nenhuma agregação.

| Dataset | Grão original | Sinais extraídos |
|---|---|---|
| `bureau` | um crédito em outra instituição | exposição, dívida, vencidos, atividade e recência |
| `bureau_balance` | um mês de um crédito do bureau | meses observados e severidade de atraso |
| `previous_application` | uma proposta anterior interna | aprovações, recusas, valores e recência |
| `POS_CASH_balance` | um mês de contrato POS/CASH | atraso, parcelas futuras e conclusão |
| `credit_card_balance` | um mês de cartão | utilização, saldo, pagamentos e atraso |
| `installments_payments` | uma parcela/pagamento | atraso de pagamento e pagamento insuficiente |
'''))

celulas.append(codigo(r'''
def caminho(nome):
    return ARQUIVOS.get(nome)

def divisao_segura(numerador, denominador):
    resultado = numerador / denominador.replace(0, np.nan)
    return resultado.replace([np.inf, -np.inf], np.nan)

def agregar_bureau():
    if caminho("bureau.csv") is None:
        return None
    bureau = pd.read_csv(caminho("bureau.csv"), usecols=[
        "SK_ID_CURR", "SK_ID_BUREAU", "CREDIT_ACTIVE", "AMT_CREDIT_SUM_OVERDUE",
        "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "DAYS_CREDIT", "CNT_CREDIT_PROLONG",
    ], low_memory=False)
    bureau["BUREAU_ATIVO"] = (bureau["CREDIT_ACTIVE"] == "Active").astype("int8")
    bureau["BUREAU_COM_ATRASO"] = (bureau["AMT_CREDIT_SUM_OVERDUE"].fillna(0) > 0).astype("int8")

    if caminho("bureau_balance.csv") is not None:
        saldo = pd.read_csv(
            caminho("bureau_balance.csv"),
            dtype={"SK_ID_BUREAU": "int32", "MONTHS_BALANCE": "int16", "STATUS": "category"},
        )
        mapa_status = {"X": 0, "C": 0, "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
        saldo["BB_STATUS_NUM"] = saldo["STATUS"].map(mapa_status).astype("float32")
        saldo["BB_MES_EM_ATRASO"] = saldo["STATUS"].isin(["1", "2", "3", "4", "5"]).astype("int8")
        saldo_cliente = saldo.groupby("SK_ID_BUREAU", observed=True).agg(
            BB_MESES=("MONTHS_BALANCE", "count"),
            BB_MES_MAIS_RECENTE=("MONTHS_BALANCE", "max"),
            BB_MESES_EM_ATRASO=("BB_MES_EM_ATRASO", "sum"),
            BB_PIOR_STATUS=("BB_STATUS_NUM", "max"),
        ).reset_index()
        bureau = bureau.merge(saldo_cliente, on="SK_ID_BUREAU", how="left", validate="one_to_one")
        del saldo, saldo_cliente

    especificacao = {
        "BUREAU_CONTRATOS": ("SK_ID_BUREAU", "nunique"),
        "BUREAU_ATIVOS": ("BUREAU_ATIVO", "sum"),
        "BUREAU_CONTRATOS_COM_ATRASO": ("BUREAU_COM_ATRASO", "sum"),
        "BUREAU_CREDITO_TOTAL": ("AMT_CREDIT_SUM", "sum"),
        "BUREAU_DIVIDA_TOTAL": ("AMT_CREDIT_SUM_DEBT", "sum"),
        "BUREAU_VENCIDO_TOTAL": ("AMT_CREDIT_SUM_OVERDUE", "sum"),
        "BUREAU_DIAS_CREDITO_MEDIO": ("DAYS_CREDIT", "mean"),
        "BUREAU_PROLONGAMENTOS": ("CNT_CREDIT_PROLONG", "sum"),
    }
    if "BB_MESES" in bureau:
        especificacao.update({
            "BB_MESES_OBSERVADOS": ("BB_MESES", "sum"),
            "BB_MESES_EM_ATRASO": ("BB_MESES_EM_ATRASO", "sum"),
            "BB_PIOR_STATUS": ("BB_PIOR_STATUS", "max"),
        })
    agregado = bureau.groupby("SK_ID_CURR").agg(**especificacao).reset_index()
    agregado["BUREAU_RAZAO_DIVIDA_CREDITO"] = divisao_segura(
        agregado["BUREAU_DIVIDA_TOTAL"], agregado["BUREAU_CREDITO_TOTAL"]
    )
    return agregado

def agregar_previous_application():
    if caminho("previous_application.csv") is None:
        return None
    anterior = pd.read_csv(caminho("previous_application.csv"), usecols=[
        "SK_ID_CURR", "SK_ID_PREV", "NAME_CONTRACT_STATUS", "AMT_APPLICATION",
        "AMT_CREDIT", "AMT_ANNUITY", "AMT_DOWN_PAYMENT", "CNT_PAYMENT", "DAYS_DECISION",
    ], low_memory=False)
    anterior["PREV_APROVADA"] = (anterior["NAME_CONTRACT_STATUS"] == "Approved").astype("int8")
    anterior["PREV_RECUSADA"] = (anterior["NAME_CONTRACT_STATUS"] == "Refused").astype("int8")
    anterior["PREV_RAZAO_CREDITO_PEDIDO"] = divisao_segura(anterior["AMT_CREDIT"], anterior["AMT_APPLICATION"])
    return anterior.groupby("SK_ID_CURR").agg(
        PREV_PROPOSTAS=("SK_ID_PREV", "nunique"),
        PREV_APROVADAS=("PREV_APROVADA", "sum"),
        PREV_RECUSADAS=("PREV_RECUSADA", "sum"),
        PREV_CREDITO_MEDIO=("AMT_CREDIT", "mean"),
        PREV_ANUIDADE_MEDIA=("AMT_ANNUITY", "mean"),
        PREV_ENTRADA_MEDIA=("AMT_DOWN_PAYMENT", "mean"),
        PREV_PARCELAS_MEDIA=("CNT_PAYMENT", "mean"),
        PREV_RAZAO_CREDITO_PEDIDO_MEDIA=("PREV_RAZAO_CREDITO_PEDIDO", "mean"),
        PREV_DECISAO_MAIS_RECENTE=("DAYS_DECISION", "max"),
    ).reset_index()

def agregar_pos_cash():
    if caminho("POS_CASH_balance.csv") is None:
        return None
    pos = pd.read_csv(caminho("POS_CASH_balance.csv"), usecols=[
        "SK_ID_CURR", "SK_ID_PREV", "MONTHS_BALANCE", "CNT_INSTALMENT_FUTURE",
        "SK_DPD", "SK_DPD_DEF", "NAME_CONTRACT_STATUS",
    ], low_memory=False)
    pos["POS_EM_ATRASO"] = (pos["SK_DPD"].fillna(0) > 0).astype("int8")
    pos["POS_CONCLUIDO"] = (pos["NAME_CONTRACT_STATUS"] == "Completed").astype("int8")
    return pos.groupby("SK_ID_CURR").agg(
        POS_CONTRATOS=("SK_ID_PREV", "nunique"),
        POS_MESES=("MONTHS_BALANCE", "count"),
        POS_MES_MAIS_RECENTE=("MONTHS_BALANCE", "max"),
        POS_PARCELAS_FUTURAS_MEDIA=("CNT_INSTALMENT_FUTURE", "mean"),
        POS_DPD_MEDIO=("SK_DPD", "mean"),
        POS_DPD_MAXIMO=("SK_DPD", "max"),
        POS_DPD_DEF_MEDIO=("SK_DPD_DEF", "mean"),
        POS_MESES_EM_ATRASO=("POS_EM_ATRASO", "sum"),
        POS_MESES_CONCLUIDOS=("POS_CONCLUIDO", "sum"),
    ).reset_index()

def agregar_cartao():
    if caminho("credit_card_balance.csv") is None:
        return None
    cartao = pd.read_csv(caminho("credit_card_balance.csv"), usecols=[
        "SK_ID_CURR", "SK_ID_PREV", "MONTHS_BALANCE", "AMT_BALANCE",
        "AMT_CREDIT_LIMIT_ACTUAL", "AMT_DRAWINGS_CURRENT", "AMT_PAYMENT_CURRENT", "SK_DPD",
    ], low_memory=False)
    cartao["CC_UTILIZACAO"] = divisao_segura(cartao["AMT_BALANCE"], cartao["AMT_CREDIT_LIMIT_ACTUAL"])
    cartao["CC_EM_ATRASO"] = (cartao["SK_DPD"].fillna(0) > 0).astype("int8")
    return cartao.groupby("SK_ID_CURR").agg(
        CC_CONTRATOS=("SK_ID_PREV", "nunique"),
        CC_MESES=("MONTHS_BALANCE", "count"),
        CC_SALDO_MEDIO=("AMT_BALANCE", "mean"),
        CC_SALDO_MAXIMO=("AMT_BALANCE", "max"),
        CC_LIMITE_MEDIO=("AMT_CREDIT_LIMIT_ACTUAL", "mean"),
        CC_UTILIZACAO_MEDIA=("CC_UTILIZACAO", "mean"),
        CC_UTILIZACAO_MAXIMA=("CC_UTILIZACAO", "max"),
        CC_SAQUES_MEDIOS=("AMT_DRAWINGS_CURRENT", "mean"),
        CC_PAGAMENTO_MEDIO=("AMT_PAYMENT_CURRENT", "mean"),
        CC_DPD_MAXIMO=("SK_DPD", "max"),
        CC_MESES_EM_ATRASO=("CC_EM_ATRASO", "sum"),
    ).reset_index()

def agregar_parcelas():
    if caminho("installments_payments.csv") is None:
        return None
    parcelas = pd.read_csv(caminho("installments_payments.csv"), usecols=[
        "SK_ID_CURR", "SK_ID_PREV", "NUM_INSTALMENT_NUMBER", "DAYS_INSTALMENT",
        "DAYS_ENTRY_PAYMENT", "AMT_INSTALMENT", "AMT_PAYMENT",
    ], low_memory=False)
    parcelas["PARC_ATRASO_DIAS"] = (parcelas["DAYS_ENTRY_PAYMENT"] - parcelas["DAYS_INSTALMENT"]).clip(lower=0)
    parcelas["PARC_EM_ATRASO"] = (parcelas["PARC_ATRASO_DIAS"] > 0).astype("int8")
    parcelas["PARC_RAZAO_PAGA"] = divisao_segura(parcelas["AMT_PAYMENT"], parcelas["AMT_INSTALMENT"])
    parcelas["PARC_PAGAMENTO_INSUFICIENTE"] = (parcelas["PARC_RAZAO_PAGA"] < 0.99).astype("int8")
    return parcelas.groupby("SK_ID_CURR").agg(
        PARC_CONTRATOS=("SK_ID_PREV", "nunique"),
        PARC_REGISTROS=("NUM_INSTALMENT_NUMBER", "count"),
        PARC_ATRASO_MEDIO_DIAS=("PARC_ATRASO_DIAS", "mean"),
        PARC_ATRASO_MAXIMO_DIAS=("PARC_ATRASO_DIAS", "max"),
        PARC_PARCELAS_EM_ATRASO=("PARC_EM_ATRASO", "sum"),
        PARC_RAZAO_PAGA_MEDIA=("PARC_RAZAO_PAGA", "mean"),
        PARC_PAGAMENTOS_INSUFICIENTES=("PARC_PAGAMENTO_INSUFICIENTE", "sum"),
        PARC_VALOR_PREVISTO=("AMT_INSTALMENT", "sum"),
        PARC_VALOR_PAGO=("AMT_PAYMENT", "sum"),
    ).reset_index()
'''))

celulas.append(codigo(r'''
def criar_features_aplicacao(dados):
    df = dados.copy()
    emprego = df["DAYS_EMPLOYED"].replace(365243, np.nan)
    df["IDADE_ANOS"] = -df["DAYS_BIRTH"] / 365.25
    df["TEMPO_EMPREGO_ANOS"] = -emprego / 365.25
    df["TEMPO_RESIDENCIA_ANOS"] = -df["DAYS_REGISTRATION"] / 365.25
    df["RAZAO_CREDITO_RENDA"] = divisao_segura(df["AMT_CREDIT"], df["AMT_INCOME_TOTAL"])
    df["RAZAO_ANUIDADE_RENDA"] = divisao_segura(df["AMT_ANNUITY"], df["AMT_INCOME_TOTAL"])
    df["RAZAO_CREDITO_BEM"] = divisao_segura(df["AMT_CREDIT"], df["AMT_GOODS_PRICE"])
    df["RENDA_POR_PESSOA"] = divisao_segura(df["AMT_INCOME_TOTAL"], df["CNT_FAM_MEMBERS"])
    fontes = [c for c in ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"] if c in df]
    df["MEDIA_FONTES_EXTERNAS"] = df[fontes].mean(axis=1)
    df["QTD_FONTES_EXTERNAS"] = df[fontes].notna().sum(axis=1)
    return df

treino_modelo = criar_features_aplicacao(app_train)
teste_kaggle = criar_features_aplicacao(app_test)
del app_train, app_test, eda

agregadores = {
    "bureau + bureau_balance": agregar_bureau,
    "previous_application": agregar_previous_application,
    "POS_CASH_balance": agregar_pos_cash,
    "credit_card_balance": agregar_cartao,
    "installments_payments": agregar_parcelas,
}

tabelas_features = []
resumo_agregacoes = []
for nome, funcao in agregadores.items():
    inicio = time.time()
    tabela = funcao()
    if tabela is None:
        resumo_agregacoes.append({"fonte": nome, "status": "ausente", "clientes": 0, "atributos": 0, "segundos": 0})
        continue
    if not tabela["SK_ID_CURR"].is_unique:
        raise ValueError(f"A agregação {nome} não ficou única por cliente.")
    tabelas_features.append(tabela)
    resumo_agregacoes.append({
        "fonte": nome,
        "status": "processada",
        "clientes": len(tabela),
        "atributos": tabela.shape[1] - 1,
        "segundos": time.time() - inicio,
    })

resumo_agregacoes = pd.DataFrame(resumo_agregacoes)
display(resumo_agregacoes.style.format({"clientes": "{:,.0f}", "segundos": "{:,.1f}"}).hide(axis="index"))
'''))

celulas.append(codigo(r'''
linhas_treino_antes, linhas_teste_antes = len(treino_modelo), len(teste_kaggle)
for tabela in tabelas_features:
    treino_modelo = treino_modelo.merge(tabela, on="SK_ID_CURR", how="left", validate="one_to_one")
    teste_kaggle = teste_kaggle.merge(tabela, on="SK_ID_CURR", how="left", validate="one_to_one")

atributos_historicos = sum(t.shape[1] - 1 for t in tabelas_features)
display(Markdown(
    f"Foram criados **{atributos_historicos} atributos históricos** e a tabela analítica final possui "
    f"**{treino_modelo.shape[1] - 1} variáveis candidatas** para **{br_numero(len(treino_modelo))} clientes**."
))

portao_qualidade("Etapa 3 — Engenharia de atributos", {
    "Alguma agregação não ficou única por cliente": all(t["SK_ID_CURR"].is_unique for t in tabelas_features),
    "O merge alterou a quantidade de clientes no treino": len(treino_modelo) == linhas_treino_antes,
    "O merge alterou a quantidade de clientes no teste": len(teste_kaggle) == linhas_teste_antes,
    "Nenhum atributo histórico foi criado": atributos_historicos > 0,
    "O TARGET foi introduzido em tabela histórica": all("TARGET" not in t.columns for t in tabelas_features),
})
'''))

celulas.append(markdown(r'''
## 4. Do dado ao modelo — sem vazamento

O `application_test` do Kaggle não tem rótulo e serve apenas para a submissão final. Para avaliar honestamente, separamos o `application_train` em três partes estratificadas:

- **Treino (70%)**: ajusta os parâmetros dos modelos;
- **Validação (15%)**: escolhe o modelo e o limiar operacional;
- **Teste interno (15%)**: mede o desempenho final uma única vez.

`CODE_GENDER` é preservado somente para auditoria de equidade e não entra no modelo. Colunas com mais de 65% de ausência, identificadores e constantes também são removidas.
'''))

celulas.append(codigo(r'''
ALVO = "TARGET"
IDENTIFICADORES = ["SK_ID_CURR"]
SENSIVEIS_AUDITORIA = ["CODE_GENDER"]

y_total = treino_modelo[ALVO].astype("int8")
X_total = treino_modelo.drop(columns=[ALVO])
X_kaggle = teste_kaggle.copy()

limite_ausencia = 0.65
colunas_muito_ausentes = X_total.columns[X_total.isna().mean() > limite_ausencia].tolist()
colunas_constantes = [c for c in X_total.columns if X_total[c].nunique(dropna=False) <= 1]
colunas_excluir = sorted(set(IDENTIFICADORES + SENSIVEIS_AUDITORIA + colunas_muito_ausentes + colunas_constantes))

X_total = X_total.drop(columns=colunas_excluir, errors="ignore").replace([np.inf, -np.inf], np.nan)
X_kaggle = X_kaggle.reindex(columns=X_total.columns).replace([np.inf, -np.inf], np.nan)

if MODO_EXECUCAO == "rapido" and len(X_total) > 80_000:
    X_total, _, y_total, _ = train_test_split(
        X_total, y_total, train_size=80_000, stratify=y_total, random_state=RANDOM_STATE
    )
    print("Modo rápido: modelagem limitada a 80.000 clientes, com estratificação.")

X_desenvolvimento, X_teste, y_desenvolvimento, y_teste = train_test_split(
    X_total, y_total, test_size=0.15, stratify=y_total, random_state=RANDOM_STATE
)
X_treino, X_validacao, y_treino, y_validacao = train_test_split(
    X_desenvolvimento,
    y_desenvolvimento,
    test_size=0.1764705882,
    stratify=y_desenvolvimento,
    random_state=RANDOM_STATE,
)

colunas_numericas = X_treino.select_dtypes(include=np.number).columns.tolist()
colunas_categoricas = X_treino.select_dtypes(exclude=np.number).columns.tolist()

print(f"Treino: {len(X_treino):,} | Validação: {len(X_validacao):,} | Teste interno: {len(X_teste):,}")
print(f"Variáveis numéricas: {len(colunas_numericas)} | categóricas: {len(colunas_categoricas)}")
'''))

celulas.append(codigo(r'''
preprocessamento_logistico = ColumnTransformer([
    ("numericas", Pipeline([
        ("imputacao", SimpleImputer(strategy="median", add_indicator=True)),
        ("escala", StandardScaler(with_mean=False)),
    ]), colunas_numericas),
    ("categoricas", Pipeline([
        ("imputacao", SimpleImputer(strategy="most_frequent")),
        ("one_hot", OneHotEncoder(handle_unknown="ignore", min_frequency=50)),
    ]), colunas_categoricas),
])

preprocessamento_arvore = ColumnTransformer([
    ("numericas", SimpleImputer(strategy="median", add_indicator=True), colunas_numericas),
    ("categoricas", Pipeline([
        ("imputacao", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ]), colunas_categoricas),
])

modelos = {
    "Regressão logística": Pipeline([
        ("preprocessamento", preprocessamento_logistico),
        ("modelo", LogisticRegression(C=0.25, max_iter=350, solver="liblinear", random_state=RANDOM_STATE)),
    ]),
    "Gradient boosting": Pipeline([
        ("preprocessamento", preprocessamento_arvore),
        ("modelo", HistGradientBoostingClassifier(
            learning_rate=0.06,
            max_iter=180,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            early_stopping=True,
            random_state=RANDOM_STATE,
        )),
    ]),
}

def calcular_metricas(y_real, probabilidades, limiar=0.5):
    classe = (probabilidades >= limiar).astype(int)
    fpr, tpr, _ = roc_curve(y_real, probabilidades)
    return {
        "roc_auc": roc_auc_score(y_real, probabilidades),
        "pr_auc": average_precision_score(y_real, probabilidades),
        "ks": np.max(tpr - fpr),
        "brier": brier_score_loss(y_real, probabilidades),
        "sensibilidade": recall_score(y_real, classe, zero_division=0),
        "precisao": precision_score(y_real, classe, zero_division=0),
        "f1": f1_score(y_real, classe, zero_division=0),
    }
'''))

celulas.append(codigo(r'''
resultados_validacao = []
probabilidades_validacao = {}

for nome, modelo in modelos.items():
    inicio = time.time()
    modelo.fit(X_treino, y_treino)
    prob = modelo.predict_proba(X_validacao)[:, 1]
    probabilidades_validacao[nome] = prob
    metricas = calcular_metricas(y_validacao, prob)
    resultados_validacao.append({"modelo": nome, **metricas, "tempo_segundos": time.time() - inicio})

comparacao_modelos = pd.DataFrame(resultados_validacao).sort_values("roc_auc", ascending=False)
nome_vencedor = comparacao_modelos.iloc[0]["modelo"]
modelo_vencedor = modelos[nome_vencedor]
prob_validacao = probabilidades_validacao[nome_vencedor]

display(
    comparacao_modelos.style
    .format({c: "{:.4f}" for c in ["roc_auc", "pr_auc", "ks", "brier", "sensibilidade", "precisao", "f1"]})
    .format({"tempo_segundos": "{:,.1f}"})
    .background_gradient(subset=["roc_auc", "pr_auc", "ks"], cmap="GnBu")
    .hide(axis="index")
)
display(Markdown(f"**Modelo selecionado na validação:** {nome_vencedor}."))
'''))

celulas.append(codigo(r'''
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for nome, prob in probabilidades_validacao.items():
    fpr, tpr, _ = roc_curve(y_validacao, prob)
    precision, recall, _ = precision_recall_curve(y_validacao, prob)
    axes[0].plot(fpr, tpr, linewidth=2, label=f"{nome} — AUC {roc_auc_score(y_validacao, prob):.3f}")
    axes[1].plot(recall, precision, linewidth=2, label=f"{nome} — AP {average_precision_score(y_validacao, prob):.3f}")

axes[0].plot([0, 1], [0, 1], "--", color="#AAB7BE")
axes[0].set(title="Curva ROC — capacidade de ordenação", xlabel="Taxa de falso positivo", ylabel="Taxa de verdadeiro positivo")
axes[1].axhline(y_validacao.mean(), linestyle="--", color="#AAB7BE", label="Prevalência")
axes[1].set(title="Curva precisão-revocação — foco no evento raro", xlabel="Sensibilidade", ylabel="Precisão")
for ax in axes:
    ax.legend(frameon=False)
sns.despine()
plt.tight_layout()
plt.show()

portao_qualidade("Etapa 4 — Modelagem e seleção", {
    "Os conjuntos não ficaram separados": not (
        (set(X_treino.index) & set(X_validacao.index))
        or (set(X_treino.index) & set(X_teste.index))
        or (set(X_validacao.index) & set(X_teste.index))
    ),
    "Menos de dois modelos foram comparados": len(comparacao_modelos) >= 2,
    "A ROC AUC não foi calculada": comparacao_modelos["roc_auc"].between(0, 1).all(),
    "A PR AUC não foi calculada": comparacao_modelos["pr_auc"].between(0, 1).all(),
    "O modelo vencedor não foi definido": nome_vencedor in modelos,
})
'''))

celulas.append(markdown(r'''
## 5. Do score à política de crédito

Um score ordena risco; uma política decide o que fazer. O limiar abaixo minimiza um custo ilustrativo em que deixar passar um inadimplente custa cinco vezes mais que encaminhar um bom cliente para revisão. Isso **não é uma recomendação financeira pronta para produção**: a razão de custos precisa incorporar margem, recuperação, apetite de risco e capacidade operacional reais.
'''))

celulas.append(codigo(r'''
def escolher_limiar(y_real, probabilidades, custo_fp=1, custo_fn=5):
    candidatos = np.linspace(0.01, 0.60, 240)
    linhas = []
    for limiar in candidatos:
        previsto = probabilidades >= limiar
        tn, fp, fn, tp = confusion_matrix(y_real, previsto, labels=[0, 1]).ravel()
        linhas.append({
            "limiar": limiar,
            "custo": fp * custo_fp + fn * custo_fn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "tn": tn,
            "sensibilidade": tp / (tp + fn) if tp + fn else 0,
            "taxa_sinalizacao": previsto.mean(),
        })
    tabela = pd.DataFrame(linhas)
    return float(tabela.loc[tabela["custo"].idxmin(), "limiar"]), tabela

limiar_otimo, curva_custo = escolher_limiar(
    y_validacao, prob_validacao, CUSTO_FALSO_POSITIVO, CUSTO_FALSO_NEGATIVO
)

fig, ax = plt.subplots(figsize=(9.5, 4.5))
ax.plot(curva_custo["limiar"], curva_custo["custo"], color=CORES["azul"], linewidth=2.4)
ax.axvline(limiar_otimo, color=CORES["coral"], linestyle="--", label=f"Limiar escolhido: {limiar_otimo:.3f}")
ax.set(title="O limiar traduz a função de custo em ação", xlabel="Limiar de probabilidade", ylabel="Custo relativo na validação")
ax.legend(frameon=False)
sns.despine()
plt.show()
'''))

celulas.append(codigo(r'''
prob_teste = modelo_vencedor.predict_proba(X_teste)[:, 1]
metricas_teste = calcular_metricas(y_teste, prob_teste, limiar_otimo)
pred_teste = (prob_teste >= limiar_otimo).astype(int)
matriz = confusion_matrix(y_teste, pred_teste, labels=[0, 1])

fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
sns.heatmap(
    matriz,
    annot=True,
    fmt=",d",
    cmap=sns.light_palette(CORES["turquesa"], as_cmap=True),
    cbar=False,
    ax=axes[0],
)
axes[0].set(title=f"Matriz de confusão — limiar {limiar_otimo:.3f}", xlabel="Predito", ylabel="Real")
axes[0].set_xticklabels(["Sem dificuldade", "Com dificuldade"])
axes[0].set_yticklabels(["Sem dificuldade", "Com dificuldade"], rotation=0)

fpr_t, tpr_t, _ = roc_curve(y_teste, prob_teste)
axes[1].plot(fpr_t, tpr_t, color=CORES["coral"], linewidth=2.5)
axes[1].plot([0, 1], [0, 1], "--", color="#AAB7BE")
axes[1].set(title=f"Teste interno — ROC AUC {metricas_teste['roc_auc']:.3f}", xlabel="Falso positivo", ylabel="Verdadeiro positivo")

fracao_positivos, probabilidade_media = calibration_curve(
    y_teste, prob_teste, n_bins=10, strategy="quantile"
)
axes[2].plot(probabilidade_media, fracao_positivos, marker="o", color=CORES["dourado"], linewidth=2.2)
axes[2].plot([0, 1], [0, 1], "--", color="#AAB7BE")
axes[2].set(
    title=f"Calibração — Brier {metricas_teste['brier']:.3f}",
    xlabel="Probabilidade média prevista",
    ylabel="Frequência observada",
)
sns.despine()
plt.tight_layout()
plt.show()

display(pd.DataFrame([metricas_teste]).style.format("{:.4f}").hide(axis="index"))
'''))

celulas.append(codigo(r'''
avaliacao_clientes = pd.DataFrame({"target": y_teste.to_numpy(), "probabilidade": prob_teste})
avaliacao_clientes["decil_risco"] = pd.qcut(
    avaliacao_clientes["probabilidade"].rank(method="first"),
    q=10,
    labels=list(range(1, 11)),
)
tabela_decis = (
    avaliacao_clientes.groupby("decil_risco", observed=True)
    .agg(
        clientes=("target", "size"),
        inadimplentes=("target", "sum"),
        taxa_inadimplencia=("target", "mean"),
        probabilidade_media=("probabilidade", "mean"),
    )
    .sort_index(ascending=False)
    .reset_index()
)
tabela_decis["lift"] = tabela_decis["taxa_inadimplencia"] / y_teste.mean()

display(
    tabela_decis.style
    .format({"clientes": "{:,.0f}", "inadimplentes": "{:,.0f}", "taxa_inadimplencia": "{:.2%}", "probabilidade_media": "{:.2%}", "lift": "{:.2f}x"})
    .background_gradient(subset=["taxa_inadimplencia", "lift"], cmap="OrRd")
    .hide(axis="index")
)

portao_qualidade("Etapa 5 — Política e teste final", {
    "O limiar não foi escolhido apenas na validação": 0 < limiar_otimo < 1,
    "A matriz de confusão não contém todo o teste": matriz.sum() == len(y_teste),
    "O teste final não produziu ROC AUC válida": 0 <= metricas_teste["roc_auc"] <= 1,
    "Os decis não cobrem todo o teste": tabela_decis["clientes"].sum() == len(y_teste),
})
'''))

celulas.append(markdown(r'''
## 6. Explicabilidade, equidade e confiança

Um bom modelo de risco precisa responder três perguntas adicionais: **quais sinais pesam?**, **o desempenho muda entre grupos?** e **o que será monitorado depois?** A importância por permutação mede quanto a ROC AUC cai quando uma variável é embaralhada. Ela mostra contribuição preditiva, não causalidade.
'''))

celulas.append(codigo(r'''
amostra_importancia = X_validacao.sample(min(3_000, len(X_validacao)), random_state=RANDOM_STATE)
y_importancia = y_validacao.loc[amostra_importancia.index]
perm = permutation_importance(
    modelo_vencedor,
    amostra_importancia,
    y_importancia,
    scoring="roc_auc",
    n_repeats=1,
    random_state=RANDOM_STATE,
)
importancias = (
    pd.DataFrame({"variavel": X_validacao.columns, "importancia": perm.importances_mean})
    .sort_values("importancia", ascending=False)
    .head(20)
)

fig, ax = plt.subplots(figsize=(9, 6.3))
plot_imp = importancias.sort_values("importancia")
ax.barh(plot_imp["variavel"], plot_imp["importancia"], color=CORES["turquesa"])
ax.set(title="Quais variáveis sustentam a ordenação de risco?", xlabel="Queda média de ROC AUC ao permutar", ylabel="")
sns.despine()
plt.show()
'''))

celulas.append(codigo(r'''
def auditar_grupo(grupos, y_real, probabilidades, limiar):
    linhas = []
    base = pd.DataFrame({"grupo": grupos.astype(str), "target": y_real, "prob": probabilidades}).dropna()
    for grupo, fatia in base.groupby("grupo"):
        previsto = (fatia["prob"] >= limiar).astype(int)
        tn, fp, fn, tp = confusion_matrix(fatia["target"], previsto, labels=[0, 1]).ravel()
        linhas.append({
            "grupo": grupo,
            "clientes": len(fatia),
            "taxa_observada": fatia["target"].mean(),
            "taxa_sinalizada": previsto.mean(),
            "sensibilidade": tp / (tp + fn) if tp + fn else np.nan,
            "taxa_falso_positivo": fp / (fp + tn) if fp + tn else np.nan,
            "roc_auc": roc_auc_score(fatia["target"], fatia["prob"]) if fatia["target"].nunique() == 2 else np.nan,
        })
    return pd.DataFrame(linhas)

genero_teste = treino_modelo.loc[X_teste.index, "CODE_GENDER"]
auditoria_genero = auditar_grupo(genero_teste, y_teste, prob_teste, limiar_otimo)
display(
    auditoria_genero.style
    .format({"clientes": "{:,.0f}", "taxa_observada": "{:.2%}", "taxa_sinalizada": "{:.2%}", "sensibilidade": "{:.2%}", "taxa_falso_positivo": "{:.2%}", "roc_auc": "{:.3f}"})
    .hide(axis="index")
)

display(Markdown(
    "**Interpretação responsável.** `CODE_GENDER` não participou do treinamento. A tabela é uma auditoria de disparidades, "
    "não uma certificação de equidade. Antes de produção, devem ser definidos limites aceitáveis, análise jurídica, revisão humana e testes adicionais por idade e interseções de grupos."
))
'''))

celulas.append(codigo(r'''
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

modelo_final = clone(modelo_vencedor)
modelo_final.fit(X_total, y_total)

prob_kaggle = modelo_final.predict_proba(X_kaggle)[:, 1]
submissao = pd.DataFrame({
    "SK_ID_CURR": teste_kaggle["SK_ID_CURR"].astype(int),
    "TARGET": prob_kaggle,
})

if caminho("sample_submission.csv") is not None:
    modelo_submissao = pd.read_csv(caminho("sample_submission.csv"))
    if set(modelo_submissao["SK_ID_CURR"]) != set(submissao["SK_ID_CURR"]):
        raise ValueError("Os IDs da submissão não coincidem com application_test.")
    submissao = modelo_submissao[["SK_ID_CURR"]].merge(submissao, on="SK_ID_CURR", how="left", validate="one_to_one")

joblib.dump(modelo_final, PASTA_RESULTADOS / "modelo_risco_credito.joblib")
submissao.to_csv(PASTA_RESULTADOS / "submissao_home_credit.csv", index=False)
comparacao_modelos.to_csv(PASTA_RESULTADOS / "comparacao_modelos.csv", index=False)
tabela_decis.to_csv(PASTA_RESULTADOS / "tabela_decis.csv", index=False)
importancias.to_csv(PASTA_RESULTADOS / "importancia_variaveis.csv", index=False)
auditoria_genero.to_csv(PASTA_RESULTADOS / "auditoria_genero.csv", index=False)

manifesto = {
    "modelo_selecionado": nome_vencedor,
    "modo_execucao": MODO_EXECUCAO,
    "base_completa": not faltantes,
    "arquivos_ausentes": faltantes,
    "limiar_operacional_ilustrativo": limiar_otimo,
    "metricas_teste": {k: float(v) for k, v in metricas_teste.items()},
    "variaveis_modelo": X_total.columns.tolist(),
    "random_state": RANDOM_STATE,
}
(PASTA_RESULTADOS / "manifesto_modelo.json").write_text(
    json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
)

artefatos = sorted(p.name for p in PASTA_RESULTADOS.iterdir())
display(pd.DataFrame({"artefatos_gerados": artefatos}).style.hide(axis="index"))

portao_qualidade("Etapa 6 — Governança e entrega", {
    "A auditoria por grupo não foi gerada": not auditoria_genero.empty,
    "A importância das variáveis não foi calculada": not importancias.empty,
    "A submissão não cobre application_test": len(submissao) == len(teste_kaggle),
    "Há probabilidades fora de [0, 1]": submissao["TARGET"].between(0, 1).all(),
    "O modelo serializado não foi salvo": (PASTA_RESULTADOS / "modelo_risco_credito.joblib").exists(),
    "A limitação de arquivos ausentes não foi registrada": (not faltantes) or (manifesto["arquivos_ausentes"] == faltantes),
})
'''))

celulas.append(markdown(r'''
## 7. Fechamento executivo

O projeto não termina em “aprovar ou negar”. Ele entrega uma forma auditável de **ordenar risco**, transforma o histórico em sinais compreensíveis e explicita o custo da decisão. O modelo é um componente de apoio: não substitui política de crédito, validação independente, análise de impacto ou revisão humana.
'''))

celulas.append(codigo(r'''
decil_mais_arriscado = tabela_decis.iloc[0]
decil_menos_arriscado = tabela_decis.iloc[-1]

display(HTML(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0 20px">
  <div style="background:#0B1F33;color:white;padding:18px;border-radius:12px"><small>ROC AUC — teste</small><br><b style="font-size:28px">{metricas_teste['roc_auc']:.3f}</b></div>
  <div style="background:#0E4D64;color:white;padding:18px;border-radius:12px"><small>PR AUC — teste</small><br><b style="font-size:28px">{metricas_teste['pr_auc']:.3f}</b></div>
  <div style="background:#137C8B;color:white;padding:18px;border-radius:12px"><small>KS — teste</small><br><b style="font-size:28px">{metricas_teste['ks']:.3f}</b></div>
  <div style="background:#FF6B5E;color:white;padding:18px;border-radius:12px"><small>Lift — decil de maior risco</small><br><b style="font-size:28px">{decil_mais_arriscado['lift']:.2f}x</b></div>
</div>
"""))

display(Markdown(f"""
### A história em quatro conclusões

1. **O problema é desbalanceado:** apenas {taxa_inadimplencia:.2%} dos clientes apresentam dificuldade; por isso, acurácia isolada não serve.
2. **O histórico é parte da identidade de risco:** {atributos_historicos} atributos resumem exposição, atraso, utilização e recência sem usar o alvo.
3. **O score organiza a fila:** no teste interno, o modelo alcançou ROC AUC de **{metricas_teste['roc_auc']:.3f}** e KS de **{metricas_teste['ks']:.3f}**.
4. **A decisão exige governança:** o limiar **{limiar_otimo:.3f}** é apenas uma simulação econômica; sensibilidade, falso positivo, equidade e estabilidade precisam de limites institucionais.

### Próximas ações antes de produção

- validar o custo financeiro real e recalibrar o limiar;
- fazer validação temporal e fora da amostra, indisponível neste recorte;
- testar estabilidade populacional (PSI), calibração e deriva mensal;
- ampliar a auditoria de equidade para idade e interseções, com revisão jurídica;
- documentar versão dos dados, aprovações e estratégia de intervenção humana.
"""))
'''))

celulas.append(markdown(r'''
---

### Checklist final — “dá para melhorar?”

| Etapa | Resposta para avançar | Evidência |
|---|---|---|
| Integridade dos dados | **Não** | chaves, alvo, sobreposição e completude testados |
| Análise exploratória | **Não** | desbalanceamento, ausências, anomalias e sinais comparados |
| Engenharia de atributos | **Não** | uma linha por cliente, merges validados e ausência de alvo |
| Modelagem | **Não** | treino/validação/teste separados e dois modelos comparados |
| Política | **Não** | limiar escolhido na validação e avaliado no teste intocado |
| Governança | **Não** | explicabilidade, auditoria de grupo, manifesto e artefatos salvos |

Se qualquer condição deixar de ser verdadeira em uma nova execução, o respectivo portão interrompe o notebook com **“Dá para melhorar? Sim”**.
'''))


notebook = {
    "cells": celulas,
    "metadata": {
        "colab": {
            "name": "Projeto_Analise_Risco_Credito_Home_Credit.ipynb",
            "provenance": [],
            "toc_visible": True,
        },
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.x"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Notebook criado: {SAIDA}")
print(f"Células: {len(celulas)}")

