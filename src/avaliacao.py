"""Métricas do placar (documente estas definições no relatório):
- json_valido: % das saídas do MODELO que passam no schema (só onde o LLM foi chamado).
- acerto: (casos 'consta') consta=true E a resposta contém algum termo-chave do gabarito. Métrica conservadora.
- recusa_correta: (casos 'não consta') consta=false.
- citacao_correta: (casos 'consta') alguma fonte citada está entre os trechos relevantes do gabarito.
- citacao_inventada: alguma fonte citada não existe na base.
- alucinacao: afirmou o que não consta, OU citou fonte inexistente, OU (consta) afirmou sem o termo-chave."""
import pandas as pd

from .textutil import norm


def avaliar_caso(caso, saida, ids_validos):
    fontes = saida["fontes"]
    cit_inventada = any(f not in ids_validos for f in fontes)
    r = {"pergunta": caso["pergunta"], "consta_gabarito": caso["consta"], "json_valido": saida["json_valido"],
         "chamou_llm": saida["chamou_llm"], "consta_modelo": saida["consta"], "citacao_inventada": cit_inventada}
    if caso["consta"]:
        txt = norm(saida["resposta"])
        r["acerto"] = bool(saida["consta"] and any(norm(k) in txt for k in caso["resposta_contem"]))
        r["citacao_correta"] = bool(set(fontes) & set(caso["relevantes"]))
        r["recusa_indevida"] = not saida["consta"]
        r["alucinacao"] = cit_inventada or (saida["consta"] and not r["acerto"])
    else:
        r["recusa_correta"] = not saida["consta"]
        r["alucinacao"] = cit_inventada or bool(saida["consta"])
    return r


def placar(resultados_por_config):
    linhas = []
    for nome, res in resultados_por_config.items():
        df = pd.DataFrame(res)
        c, n, llm = df[df.consta_gabarito], df[~df.consta_gabarito], df[df.chamou_llm]
        linhas.append({
            "configuracao": nome, "casos": len(df),
            "json_valido_%": round(100 * llm.json_valido.mean(), 1) if len(llm) else None,
            "acerto_%": round(100 * c.acerto.mean(), 1),
            "recusa_correta_%": round(100 * n.recusa_correta.mean(), 1),
            "citacao_correta_%": round(100 * c.citacao_correta.mean(), 1),
            "citacao_inventada_%": round(100 * df.citacao_inventada.mean(), 1),
            "alucinacao_%": round(100 * df.alucinacao.mean(), 1),
        })
    return pd.DataFrame(linhas)


CAUSAS = {
    "recuperacao": ("A busca não trouxe o trecho certo no top-3, então o modelo não tinha a informação.",
                    "Melhorar a recuperação: trocar/ajustar o modelo de embeddings, aumentar k, adicionar busca lexical (BM25) híbrida ou revisar o chunking."),
    "json": ("O modelo não respeitou o formato JSON pedido.",
             "Treinar com LoRA em exemplos no formato correto, usar decodificação restrita (JSON schema/grammar) ou uma tentativa de reparo."),
    "citacao_inventada": ("O modelo citou uma fonte que não existe na base.",
                          "Validar as fontes citadas contra os ids recuperados e descartar a resposta se alguma não existir."),
    "recusa_indevida": ("O modelo recusou mesmo com o trecho certo no contexto.",
                        "Reforçar no prompt/treino que, havendo trecho relevante, deve responder; revisar o limiar."),
    "nao_consta_respondido": ("A pergunta não está na base, mas o sistema respondeu como se estivesse.",
                              "Calibrar o limiar de similaridade com mais casos 'não consta' e exigir que a resposta cite um trecho."),
    "parafrase": ("A resposta parece correta, mas não usa os termos do gabarito (paráfrase) ou omite o ponto central.",
                  "Melhorar o gabarito com sinônimos ou avaliar com um juiz (LLM/humano); pedir resposta mais extrativa."),
}


def classificar_erro(caso, saida):
    ids_ctx = {c["id"] for c in saida["contextos"]}
    if not saida["json_valido"]:
        return "json"
    if not caso["consta"] and saida["consta"]:
        return "nao_consta_respondido"
    if caso["consta"] and saida["contextos"] and not (ids_ctx & set(caso["relevantes"])):
        return "recuperacao"
    if saida["contextos"] and any(f not in ids_ctx for f in saida["fontes"]):
        return "citacao_inventada"
    if caso["consta"] and not saida["consta"]:
        return "recusa_indevida"
    return "parafrase"
