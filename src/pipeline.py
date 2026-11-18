"""Assistente: recuperação + limiar (não consta) + LLM + validação. Mesmo código no notebook e na API."""
import time

from .prompts import montar_mensagens
from .schema import RECUSA, parse_resposta
from .textutil import mascarar_pii


class Assistente:
    def __init__(self, retriever, gerar, limiar, k=3):
        """gerar: função (mensagens) -> texto bruto (HF ou Ollama)."""
        self.r, self.gerar, self.limiar, self.k = retriever, gerar, limiar, k

    def perguntar(self, pergunta, usar_contexto=True):
        pergunta = mascarar_pii(pergunta)  # LGPD: nunca processa/registra PII
        t0 = time.time()
        if not usar_contexto:
            bruto = self.gerar(montar_mensagens(pergunta, None))
            obj, erro = parse_resposta(bruto)
            return self._saida(obj, erro, bruto, [], "sem_contexto", True, t0)
        hits = self.r.buscar(pergunta, k=self.k)
        if hits[0][1] < self.limiar:  # recusa antes de gastar o LLM
            obj = {"resposta": RECUSA, "fontes": [], "consta": False}
            return self._saida(obj, None, "", hits, "abaixo_do_limiar", False, t0)
        bruto = self.gerar(montar_mensagens(pergunta, [h[0] for h in hits]))
        obj, erro = parse_resposta(bruto)
        return self._saida(obj, erro, bruto, hits, "llm", True, t0)

    def _saida(self, obj, erro, bruto, hits, caminho, chamou_llm, t0):
        valido = obj is not None
        if not valido:  # falha segura: nunca devolve texto solto ao cidadão
            obj = {"resposta": RECUSA, "fontes": [], "consta": False}
        return {**obj, "json_valido": valido, "erro_json": erro, "bruto": bruto, "caminho": caminho,
                "chamou_llm": chamou_llm, "encaminhar_humano": not obj["consta"],
                "contextos": [{"id": t["id"], "score": round(s, 4), "trecho": t["texto"]} for t, s in hits],
                "segundos": round(time.time() - t0, 2)}
