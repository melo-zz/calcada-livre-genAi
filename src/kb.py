"""Base de conhecimento: baixa leis federais do planalto.gov.br e quebra em trechos por artigo.

Licença: textos de leis e decretos não têm proteção autoral (art. 8º, IV, Lei 9.610/1998).
Normas da ABNT (ex.: NBR 9050) NÃO são usadas: não têm licença aberta. Perguntas que dependem
delas são casos de teste de "não consta"."""
import csv
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LIC = "Domínio público (art. 8º, IV, Lei 9.610/1998: textos de leis e decretos)"
P = "https://www.planalto.gov.br/ccivil_03/"
FONTES = [
    {"sigla": "l10098", "rotulo": "Lei 10.098/2000", "nome": "Lei 10.098/2000 - Acessibilidade", "url": P + "leis/l10098.htm"},
    {"sigla": "l13146", "rotulo": "Lei 13.146/2015", "nome": "Lei 13.146/2015 - Estatuto da Pessoa com Deficiência", "url": P + "_ato2015-2018/2015/lei/l13146.htm"},
    {"sigla": "l10048", "rotulo": "Lei 10.048/2000", "nome": "Lei 10.048/2000 - Atendimento prioritário", "url": P + "leis/l10048.htm"},
    {"sigla": "d5296", "rotulo": "Decreto 5.296/2004", "nome": "Decreto 5.296/2004 - Regulamenta as Leis 10.048 e 10.098", "url": P + "_ato2004-2006/2004/decreto/d5296.htm"},
    {"sigla": "ctb", "rotulo": "CTB (Lei 9.503/1997)", "nome": "Código de Trânsito Brasileiro", "url": P + "leis/l9503compilado.htm"},
    {"sigla": "l10741", "rotulo": "Lei 10.741/2003", "nome": "Lei 10.741/2003 - Estatuto da Pessoa Idosa", "url": P + "leis/2003/l10.741.htm"},
    {"sigla": "l12587", "rotulo": "Lei 12.587/2012", "nome": "Lei 12.587/2012 - Política Nacional de Mobilidade Urbana", "url": P + "_ato2011-2014/2012/lei/l12587.htm"},
    {"sigla": "l13709", "rotulo": "Lei 13.709/2018 (LGPD)", "nome": "Lei 13.709/2018 - LGPD", "url": P + "_ato2015-2018/2018/lei/l13709.htm"},
]

MAX_CHARS = 900
RE_ART = re.compile(r"^Art\.?\s*(\d+)\s*(?:º|°|o\b)?\s*(?:-\s*([A-Z])\b)?(?=[\s\.\-–:]|$)")
RE_ESTRUTURA = re.compile(r"^(CAP[ÍI]TULO|T[ÍI]TULO|SE[ÇC][ÃA]O|SUBSE[ÇC][ÃA]O|LIVRO|PARTE)\b", re.I)
RE_ANOTACAO = re.compile(r"\((?:Reda[çc][ãa]o dada|Inclu[ií]d|Vide|Regulamento|Vig[êe]ncia|Revogad|Renumerad|Promulga|Produ[çc][ãa]o de efeito|Vetad|Veto|Regulamentado|Obs)[^)]*\)", re.I)


def _decodificar(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def html_para_paragrafos(html: str):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(["strike", "s", "del"]):  # texto revogado
        t.decompose()
    for sup in soup.find_all("sup"):
        txt = sup.get_text(strip=True)
        sup.replace_with("º" if txt in ("o", "O", "º", "°") else txt)
    ps = soup.find_all("p")
    textos = [" ".join(p.get_text(" ", strip=True).split()) for p in ps] if len(ps) >= 15 else \
             [" ".join(l.split()) for l in soup.get_text("\n").splitlines()]
    out = []
    for t in textos:
        t = re.sub(r"(\d)\s+([º°])", r"\1\2", RE_ANOTACAO.sub("", t)).strip()
        if not t or RE_ESTRUTURA.match(t) or re.match(r"^\(?Revogad", t, re.I):
            continue
        out.append(t)
    return out


def _partir(paragrafos, limite=MAX_CHARS):
    partes, atual = [], ""
    for par in paragrafos:
        while len(par) > limite:  # parágrafo gigante: corta na última frase/espaço
            corte = max(par.rfind(". ", 0, limite), par.rfind("; ", 0, limite), par.rfind(" ", 0, limite))
            corte = corte if corte > 200 else limite
            if atual:
                partes.append(atual); atual = ""
            partes.append(par[:corte + 1].strip()); par = par[corte + 1:].strip()
        if len(atual) + len(par) + 1 > limite and atual:
            partes.append(atual); atual = par
        else:
            atual = (atual + "\n" + par).strip()
    if atual:
        partes.append(atual)
    return partes


def chunkear(paragrafos, fonte):
    artigos, atual = [], None
    for t in paragrafos:
        m = RE_ART.match(t)
        if m:
            atual = {"n": m.group(1), "letra": (m.group(2) or "").lower(), "paras": [t]}
            artigos.append(atual)
        elif atual is not None:
            atual["paras"].append(t)
    trechos, vistos = [], {}
    for a in artigos:
        base_id = f"{fonte['sigla']}_art{a['n']}{a['letra']}"
        vistos[base_id] = vistos.get(base_id, 0) + 1
        if vistos[base_id] > 1:  # artigo repetido na página
            base_id += f"_v{vistos[base_id]}"
        partes = _partir(a["paras"])
        for k, corpo in enumerate(partes, 1):
            trechos.append({
                "id": base_id if len(partes) == 1 else f"{base_id}_p{k}",
                "fonte": fonte["nome"], "sigla": fonte["sigla"], "artigo": f"Art. {a['n']}{a['letra'].upper()}", "parte": k,
                "url": fonte["url"], "licenca": LIC, "texto": f"{fonte['rotulo']}, {corpo}",
            })
    return trechos


def baixar_fonte(fonte, timeout=60):
    r = requests.get(fonte["url"], timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (GS-FIAP)"})
    r.raise_for_status()
    return _decodificar(r.content)


def construir_base(destino="base", fontes=FONTES):
    destino = Path(destino); destino.mkdir(parents=True, exist_ok=True)
    todos, resumo = [], []
    for f in fontes:
        try:
            tr = chunkear(html_para_paragrafos(baixar_fonte(f)), f)
            print(f"{f['sigla']:<8} {len(tr):>5} trechos")
        except Exception as e:  # noqa: BLE001
            print(f"ATENÇÃO: falha em {f['sigla']} ({f['url']}): {e}")
            tr = []
        todos += tr
        resumo.append({"fonte": f["nome"], "formato": "HTML (planalto.gov.br)", "licenca": LIC, "url": f["url"], "n_trechos": len(tr)})
    with (destino / "trechos.jsonl").open("w", encoding="utf-8") as fh:
        for t in todos:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    with (destino / "fontes.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(resumo[0].keys())); w.writeheader(); w.writerows(resumo)
    print(f"Total: {len(todos)} trechos em {destino}/trechos.jsonl")
    return todos, resumo


def carregar_trechos(caminho="base/trechos.jsonl"):
    with open(caminho, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]
