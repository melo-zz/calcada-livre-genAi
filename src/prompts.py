from .schema import RECUSA

FORMATO = '{"resposta": "...", "fontes": ["id_do_trecho"], "consta": true}'

SYSTEM_RAG = (
    "Você é o assistente do Calçada Livre, que ajuda cidadãos com dúvidas sobre acessibilidade e calçadas no Brasil. "
    f"Responda SOMENTE com um objeto JSON no formato {FORMATO}. "
    "Use apenas os trechos fornecidos; cite em \"fontes\" os ids dos trechos usados. "
    f"Se a resposta não estiver nos trechos, responda {{\"resposta\": \"{RECUSA}\", \"fontes\": [], \"consta\": false}}. "
    "Nunca invente números de artigos, medidas ou valores. Não peça nem repita dados pessoais."
)

SYSTEM_SEM_CONTEXTO = (
    "Você é o assistente do Calçada Livre, que ajuda cidadãos com dúvidas sobre acessibilidade e calçadas no Brasil. "
    f"Responda SOMENTE com um objeto JSON no formato {FORMATO}. "
    "Em \"fontes\" cite as leis ou artigos em que você se baseou. Se não souber, responda "
    f"{{\"resposta\": \"{RECUSA}\", \"fontes\": [], \"consta\": false}}."
)


def montar_mensagens(pergunta: str, trechos=None):
    """trechos: lista de dicts com 'id' e 'texto'. None = configuração sem contexto."""
    if trechos is None:
        return [{"role": "system", "content": SYSTEM_SEM_CONTEXTO}, {"role": "user", "content": f"Pergunta: {pergunta}"}]
    ctx = "\n".join(f"[{t['id']}] {t['texto']}" for t in trechos)
    return [{"role": "system", "content": SYSTEM_RAG}, {"role": "user", "content": f"Trechos:\n{ctx}\n\nPergunta: {pergunta}"}]
