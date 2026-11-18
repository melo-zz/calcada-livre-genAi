"""Dados de treino do LoRA (gerados dos trechos da base; NÃO usam os casos de teste).
O LoRA ensina FORMATO (JSON válido), CITAÇÃO do id do trecho e RECUSA quando o contexto não responde.
O conhecimento continua vindo da base via RAG. Perguntas de treino são templates por artigo, diferentes das do teste."""
import json
import random
import re

from .prompts import montar_mensagens
from .schema import RECUSA

TEMPLATES = [
    "O que diz o {art} da {rotulo}?", "Explique o {art} da {rotulo}.", "{rotulo}: o que estabelece o {art}?",
    "Pode resumir o {art} da {rotulo}?", "Qual é o conteúdo do {art} ({rotulo})?",
    "Em linguagem simples, o que o {art} da {rotulo} determina?", "Resuma o {art} da {rotulo} para um cidadão.",
    "Segundo a {rotulo}, o que prevê o {art}?",
]

PERGUNTAS_NC = [
    "Qual o melhor restaurante do centro de São Paulo?", "Como faço um bolo de cenoura?", "Quem é o presidente do Brasil?",
    "Qual a cotação do dólar hoje?", "Como trocar o pneu de um carro?", "Qual a capital da Austrália?",
    "Qual o preço da passagem de ônibus?", "Quando é o próximo feriado?", "Como declarar o imposto de renda?",
    "Qual o telefone da prefeitura?", "Qual a largura exata da calçada em metros?", "Qual a altura do meio-fio?",
    "Qual é a inclinação máxima de uma rampa em porcentagem?", "Quanto custa reformar uma calçada?",
    "Qual o prazo para a prefeitura consertar um buraco?", "Qual o valor da multa por estacionar na calçada em reais?",
    "Onde comprar uma cadeira de rodas barata?", "Qual a previsão do tempo para o fim de semana?",
    "Como instalar um piso tátil em casa?", "Qual a cor oficial do piso tátil?", "Qual o endereço da subprefeitura da Mooca?",
    "Como funciona o IPTU?", "Quais são os melhores aplicativos de mapas?", "Quantos habitantes tem São Paulo?",
    "Qual a velocidade máxima da Marginal Pinheiros?", "Como abrir uma empresa?", "Qual o horário do metrô no domingo?",
    "Como se cadastrar no Bilhete Único?", "Qual a distância entre dois semáforos?", "Qual a espessura do concreto de uma calçada?",
    "Quais materiais usar em uma calçada ecológica?", "Como funciona um sensor ultrassônico?", "Quem inventou a cadeira de rodas?",
    "Qual time ganhou o campeonato paulista?", "Qual a melhor época para viajar ao Nordeste?", "Quanto tempo leva para tirar passaporte?",
    "Como pedir a segunda via do RG?", "Qual a largura do piso tátil direcional?", "Quantas pessoas usam cadeira de rodas no Brasil?",
    "Qual o limite de peso de um carrinho de bebê?",
]


def _rotulo(t):
    return t["texto"].split(", ")[0] if ", " in t["texto"] else t["fonte"]


def _extrato(t, limite=380):
    corpo = t["texto"].split(", ", 1)[1] if ", " in t["texto"] else t["texto"]
    corpo = re.sub(r"\s+", " ", corpo).strip()
    if len(corpo) <= limite:
        return corpo
    corte = max(corpo.rfind(". ", 0, limite), corpo.rfind("; ", 0, limite), corpo.rfind(": ", 0, limite))
    return corpo[: corte + 1] if corte > 120 else corpo[:limite].rsplit(" ", 1)[0] + "..."


def _contexto(pergunta, gold, trechos, retriever, rnd, k=3):
    outros = []
    if retriever is not None:
        outros = [h[0] for h in retriever.buscar(pergunta, k=k + 1) if gold is None or h[0]["id"] != gold["id"]]
    if len(outros) < k:
        outros += rnd.sample(trechos, k)
    ctx = (([gold] if gold else []) + outros)[:k]
    rnd.shuffle(ctx)
    return ctx


def construir(trechos, retriever=None, n_consta=360, n_nc=120, por_fonte=60, seed=42):
    rnd = random.Random(seed)
    por = {}
    for t in trechos:
        if len(t["texto"]) > 150:
            por.setdefault(t["sigla"], []).append(t)
    escolhidos = []
    for lst in por.values():
        escolhidos += rnd.sample(lst, min(por_fonte, len(lst)))
    rnd.shuffle(escolhidos)
    exemplos = []
    for t in escolhidos[:n_consta]:
        q = rnd.choice(TEMPLATES).format(art=t["artigo"], rotulo=_rotulo(t))
        saida = {"resposta": _extrato(t), "fontes": [t["id"]], "consta": True}
        exemplos.append({"messages": montar_mensagens(q, _contexto(q, t, trechos, retriever, rnd)),
                         "alvo": json.dumps(saida, ensure_ascii=False)})
    for i in range(n_nc):
        q = PERGUNTAS_NC[i % len(PERGUNTAS_NC)]
        saida = {"resposta": RECUSA, "fontes": [], "consta": False}
        exemplos.append({"messages": montar_mensagens(q, _contexto(q, None, trechos, retriever, rnd)),
                         "alvo": json.dumps(saida, ensure_ascii=False)})
    rnd.shuffle(exemplos)
    return exemplos


def salvar(exemplos, caminho="avaliacao/treino_lora.jsonl"):
    with open(caminho, "w", encoding="utf-8") as fh:
        for e in exemplos:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
