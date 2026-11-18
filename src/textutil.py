import re
import unicodedata


def norm(s: str) -> str:
    """minúsculas, sem acento, só letras/números separados por espaço."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


_PII = [
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b"), "[TELEFONE]"),
]


def mascarar_pii(texto: str) -> str:
    """LGPD: remove CPF, e-mail e telefone antes de processar ou registrar a pergunta."""
    for rx, rep in _PII:
        texto = rx.sub(rep, texto)
    return texto
