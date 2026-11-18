"""API do assistente (FastAPI + Ollama): RAG + limiar de 'não consta' + validação de JSON + LGPD.
Rodar: uvicorn api.main:app --port 8000  (Ollama rodando: ollama pull qwen2.5:1.5b)"""
import json
import os
import sys
from pathlib import Path

import requests
from fastapi import FastAPI
from pydantic import BaseModel, Field

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.kb import carregar_trechos  # noqa: E402
from src.pipeline import Assistente  # noqa: E402
from src.retrieval import Retriever  # noqa: E402

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
_lim = RAIZ / "avaliacao" / "limiar.json"
LIMIAR = float(os.getenv("LIMIAR", json.loads(_lim.read_text())["limiar"] if _lim.exists() else 0.80))

TIPOS = {"buraco": "um buraco na calçada", "obstaculo": "um obstáculo no passeio", "piso_quebrado": "piso quebrado ou irregular",
         "degrau_sem_rampa": "um degrau sem rampa", "trecho_escuro": "um trecho sem iluminação"}


def gerar_ollama(mensagens):
    r = requests.post(f"{OLLAMA_URL}/api/chat", timeout=120, json={
        "model": OLLAMA_MODEL, "messages": mensagens, "stream": False, "format": "json",
        "options": {"temperature": 0, "num_predict": 256}})
    r.raise_for_status()
    return r.json()["message"]["content"]


app = FastAPI(title="Calçada Livre - Assistente", version="1.0")
_assistente = None


def assistente():
    global _assistente
    if _assistente is None:
        (RAIZ / ".cache").mkdir(exist_ok=True)
        trechos = carregar_trechos(str(RAIZ / "base" / "trechos.jsonl"))
        _assistente = Assistente(Retriever(trechos, cache=str(RAIZ / ".cache" / "emb.npy")), gerar_ollama, LIMIAR)
    return _assistente


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=3, max_length=500)


class OcorrenciaIn(BaseModel):
    tipo_barreira: str
    local: str = Field(default="", max_length=120)


@app.get("/saude")
def saude():
    return {"status": "ok", "modelo": OLLAMA_MODEL, "limiar": LIMIAR}


def _publico(s):  # nunca devolve o texto bruto do modelo nem PII
    return {k: s[k] for k in ("resposta", "fontes", "consta", "encaminhar_humano", "contextos", "caminho")}


@app.post("/perguntar")
def perguntar(p: Pergunta):
    return _publico(assistente().perguntar(p.pergunta))


@app.post("/explicar-ocorrencia")
def explicar(o: OcorrenciaIn):
    """Explica uma ocorrência (do carrinho, da visão ou do app): que direito/norma se aplica."""
    desc = TIPOS.get(o.tipo_barreira, "uma barreira de acessibilidade")
    return _publico(assistente().perguntar(f"Uma pessoa encontrou {desc} em uma calçada. Quais direitos e normas de acessibilidade se aplicam?"))
