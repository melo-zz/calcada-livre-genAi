"""Busca semântica (embeddings multilíngues) + recall@k + escolha de limiar para 'não consta'."""
import numpy as np

from .textutil import norm

MODELO_EMB = "intfloat/multilingual-e5-small"


class Retriever:
    def __init__(self, trechos, modelo=MODELO_EMB, cache=None, device=None):
        from sentence_transformers import SentenceTransformer
        self.trechos = trechos
        self.modelo = SentenceTransformer(modelo, device=device)
        self.emb = None
        if cache:
            try:
                e = np.load(cache)
                if len(e) == len(trechos):
                    self.emb = e
            except OSError:
                pass
        if self.emb is None:
            self.emb = self.modelo.encode(["passage: " + t["texto"] for t in trechos], batch_size=32,
                                          normalize_embeddings=True, show_progress_bar=True)
            if cache:
                np.save(cache, self.emb)

    def buscar(self, pergunta, k=3):
        q = self.modelo.encode(["query: " + pergunta], normalize_embeddings=True)[0]
        sc = self.emb @ q
        idx = np.argsort(-sc)[:k]
        return [(self.trechos[i], float(sc[i])) for i in idx]


def resolver_relevantes(caso, trechos):
    """Gabarito por evidência: trechos cujo texto contém a frase-evidência do caso."""
    ev = norm(caso["evidencia"])
    return [t["id"] for t in trechos if ev in norm(t["texto"])]


def recall_at_k(casos, retriever, ks=(1, 3)):
    res, n, detalhes = {k: 0 for k in ks}, 0, []
    for c in casos:
        if not c["consta"]:
            continue
        n += 1
        hits = retriever.buscar(c["pergunta"], k=max(ks))
        ids = [t["id"] for t, _ in hits]
        rel = set(c["relevantes"])
        for k in ks:
            if rel & set(ids[:k]):
                res[k] += 1
        detalhes.append({"pergunta": c["pergunta"], "top1": ids[0], "score_top1": hits[0][1], "ok@1": ids[0] in rel,
                         "ok@3": bool(rel & set(ids[:3])), "relevantes": sorted(rel)[:5]})
    return {f"recall@{k}": res[k] / n for k in ks}, detalhes


def escolher_limiar(casos, retriever):
    """Limiar de score top-1 que melhor separa 'consta' de 'não consta' (acurácia balanceada)."""
    pos, neg = [], []
    for c in casos:
        s = retriever.buscar(c["pergunta"], k=1)[0][1]
        (pos if c["consta"] else neg).append(s)
    melhor, tabela = (-1, None), []
    for thr in sorted(set(pos + neg)):
        tpr, tnr = sum(s >= thr for s in pos) / len(pos), sum(s < thr for s in neg) / len(neg)
        bal = (tpr + tnr) / 2
        tabela.append((thr, tpr, tnr, bal))
        if bal > melhor[0]:
            melhor = (bal, thr)
    return {"limiar": float(melhor[1]), "acuracia_balanceada": float(melhor[0]),
            "scores_consta": pos, "scores_nao_consta": neg, "tabela": tabela}
