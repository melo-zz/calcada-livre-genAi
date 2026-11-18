import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.avaliacao import avaliar_caso, classificar_erro, placar
from src.kb import chunkear, html_para_paragrafos, FONTES
from src.lora_data import construir
from src.pipeline import Assistente
from src.schema import RECUSA, parse_resposta
from src.textutil import mascarar_pii

T = [
    {"id": "a_art1", "sigla": "a", "artigo": "Art. 1", "fonte": "Lei A", "texto": "Lei A, Art. 1º O passeio público destina-se à circulação de pedestres. " + "x " * 80},
    {"id": "b_art2", "sigla": "b", "artigo": "Art. 2", "fonte": "Lei B", "texto": "Lei B, Art. 2º O pedestre tem prioridade de passagem na faixa. " + "y " * 80},
]


class FakeR:
    def __init__(self, score):
        self.score = score

    def buscar(self, q, k=3):
        return [(T[0], self.score), (T[1], self.score - 0.1)][:k]


CPF = "123.456" + ".789-" + "09"  # CPF inventado, montado em runtime
OK = '{"resposta": "circulação de pedestres", "fontes": ["a_art1"], "consta": true}'


def test_schema():
    assert parse_resposta(OK)[0]["consta"] is True
    assert parse_resposta("texto solto")[1] == "sem_json"
    assert parse_resposta('{"resposta": "x", "fontes": "a", "consta": true}')[1] == "fontes_invalidas"
    assert parse_resposta('{"resposta": "x", "fontes": [], "consta": "sim"}')[1] == "consta_invalido"


def test_limiar_recusa_sem_chamar_llm():
    chamadas = []
    a = Assistente(FakeR(0.5), lambda m: chamadas.append(1) or OK, limiar=0.8)
    s = a.perguntar("qualquer coisa")
    assert s["consta"] is False and s["resposta"] == RECUSA and not chamadas and s["encaminhar_humano"]


def test_json_invalido_falha_segura():
    s = Assistente(FakeR(0.9), lambda m: "não sei", 0.8).perguntar("p")
    assert s["json_valido"] is False and s["consta"] is False and s["resposta"] == RECUSA


def test_pii_mascarada_antes_do_llm():
    vistos = []
    Assistente(FakeR(0.9), lambda m: vistos.append(json.dumps(m)) or OK, 0.8).perguntar(f"meu cpf {CPF} e a@b.com")
    assert CPF not in vistos[0] and "a@b.com" not in vistos[0]
    assert "[CPF]" in mascarar_pii(CPF) and "[EMAIL]" in mascarar_pii("a@b.com")


def test_metricas_e_erros():
    caso = {"pergunta": "p", "consta": True, "relevantes": ["a_art1"], "resposta_contem": ["circulacao de pedestres"]}
    s = Assistente(FakeR(0.9), lambda m: OK, 0.8).perguntar("p")
    r = avaliar_caso(caso, s, {"a_art1", "b_art2"})
    assert r["acerto"] and r["citacao_correta"] and not r["alucinacao"]
    nc = {"pergunta": "q", "consta": False, "relevantes": [], "resposta_contem": []}
    r2 = avaliar_caso(nc, s, {"a_art1", "b_art2"})
    assert r2["alucinacao"] and not r2["recusa_correta"]
    assert classificar_erro(nc, s) == "nao_consta_respondido"
    assert placar({"x": [r, r2]}).shape[0] == 1


def test_chunker():
    html = ("<html><body><p>Art. 1<sup>o</sup> Esta Lei. (Redação dada pela Lei nº 1, de 2015)</p><p>§ 1<sup>o</sup> Texto.</p>"
            "<p>Art. 3º-A Novo.</p>" + "<p>x</p>" * 20 + "</body></html>")
    tr = chunkear(html_para_paragrafos(html), FONTES[0])
    assert [t["id"] for t in tr] == ["l10098_art1", "l10098_art3a"]
    assert "Redação dada" not in tr[0]["texto"] and "Art. 1º" in tr[0]["texto"]


def test_lora_data():
    ex = construir(T * 40, None, n_consta=4, n_nc=3, por_fonte=40)
    alvos = [json.loads(e["alvo"]) for e in ex]
    assert sum(a["consta"] for a in alvos) == 4 and all(a["fontes"] == [] for a in alvos if not a["consta"])
