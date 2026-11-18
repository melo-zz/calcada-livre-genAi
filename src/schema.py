import json
import re

RECUSA = "Não encontrei essa informação na base consultada."


def parse_resposta(texto: str):
    """Extrai e valida {"resposta": str, "fontes": [str], "consta": bool}. Devolve (obj|None, motivo_erro|None)."""
    if not texto:
        return None, "vazio"
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return None, "sem_json"
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, "json_invalido"
    if not isinstance(obj, dict):
        return None, "nao_objeto"
    if not isinstance(obj.get("resposta"), str) or not obj["resposta"].strip():
        return None, "resposta_ausente"
    if not isinstance(obj.get("fontes"), list) or not all(isinstance(x, str) for x in obj["fontes"]):
        return None, "fontes_invalidas"
    if not isinstance(obj.get("consta"), bool):
        return None, "consta_invalido"
    return {"resposta": obj["resposta"].strip(), "fontes": obj["fontes"], "consta": obj["consta"]}, None
