# Relatório — Generative AI for Engineering (Calçada Livre)

## 01. Integrantes
| Nome completo | RM |
|---|---|
| Carlos Ganzerli | 99840 |
| Paulo Lopes | 551137 |
| Lucas Bandeira | 98640 |
| Gustavo Melo Namura | 98809 |

## 02. Ficha Técnica
- **Produto:** Calçada Livre (mapa de barreiras de acessibilidade em calçadas de São Paulo).
- **O que a IA resolve (mobilidade):** assistente que responde dúvidas do cidadão sobre acessibilidade e calçadas com base em leis federais, **cita o trecho**, **recusa** quando não consta e explica a ocorrência detectada pelo carrinho ou pela foto.
- **Modelos:** `Qwen/Qwen2.5-1.5B-Instruct` (gerador, local) e `intfloat/multilingual-e5-small` (busca). Confira as licenças nos *model cards* antes de entregar.
- **Segurança/LGPD:** PII mascarada antes de processar; saída validada por schema; humano no circuito quando "não consta".

## 03. Diagrama do pipeline de IA
Ver o diagrama em `README.md` (Mermaid renderizado no GitHub). Fluxo: leis → trechos por artigo → embeddings → limiar → prompt → modelo (base ou + LoRA) → validação de JSON → resposta com citação / "não consta".

## 04. Tabela da base
COLE_AQUI o conteúdo de `base/tabela_fontes.md` (gerado pelo notebook 01: fonte, formato, licença e nº de trechos).

## 05. Performance das configurações
**Busca:** COLE_AQUI `avaliacao/recall.json` (recall@1 e recall@3) e a imagem `avaliacao/limiar.png` com a justificativa do limiar (notebook 02).

**Placar** (50 casos: 40 "consta" + 10 "não consta"; mesmo modelo, mesma seed): COLE_AQUI `avaliacao/placar.md` e `avaliacao/placar.png`.

**Interpretação:** COLE_AQUI `avaliacao/interpretacao.md` e acrescente 2 ou 3 frases suas (por que o RAG reduz alucinação; o que o LoRA melhorou: formato JSON, citação e recusa; o que não melhorou).

**Demonstração de alucinações:** COLE_AQUI `avaliacao/alucinacoes.md` (exemplos reais do modelo sem contexto).

**Definições das métricas:** `src/avaliacao.py` (acerto é conservador: exige termo-chave do gabarito).

## 06. Os 5 erros, a causa e a correção
COLE_AQUI `avaliacao/erros.md` (gerado pelo notebook 04 a partir de erros reais).

## 07. Conclusão técnica e links
- Conclusão (escreva com seus números): o que funcionou, limitações (modelo de 1,5B, base só com leis, avaliação por termo-chave) e próximos passos (busca híbrida BM25, mais casos, juiz humano).
- Repositório: COLE_AQUI · Vídeo: COLE_AQUI
