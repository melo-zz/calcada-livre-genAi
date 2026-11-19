# 5 erros reais, causa e correção proposta

(Total de erros encontrados nas configs B e C: 32)

## Erro 1 (B. RAG simples)
- **Pergunta:** O que a lei de acessibilidade entende por pessoa com mobilidade reduzida?
- **Gabarito:** consta ['dificuldade de movimentar']
- **Resposta do sistema:** Não encontrei essa informação na base consultada.
- **Fontes citadas:** []
- **Trechos recuperados:** l13146_art53 (0.9187), l13146_art46_p1 (0.9024), l13146_art112_p1 (0.8909)
- **Causa:** O modelo não respeitou o formato JSON pedido.
- **Correção proposta:** Treinar com LoRA em exemplos no formato correto, usar decodificação restrita (JSON schema/grammar) ou uma tentativa de reparo.

## Erro 2 (B. RAG simples)
- **Pergunta:** As vias públicas e os parques precisam ser projetados de forma acessível?
- **Gabarito:** consta ['acessiveis']
- **Resposta do sistema:** Sim, as vias públicas e os parques devem ser projetados de forma acessível conforme determina a legislação brasileira.
- **Fontes citadas:** ['l10098_art3', 'l13146_art112_p6']
- **Trechos recuperados:** l10098_art3 (0.9094), l13146_art112_p6 (0.8971), d5296_art15_p1 (0.8943)
- **Causa:** A resposta parece correta, mas não usa os termos do gabarito (paráfrase) ou omite o ponto central.
- **Correção proposta:** Melhorar o gabarito com sinônimos ou avaliar com um juiz (LLM/humano); pedir resposta mais extrativa.

## Erro 3 (B. RAG simples)
- **Pergunta:** O que significa acessibilidade segundo o Estatuto da Pessoa com Deficiência?
- **Gabarito:** consta ['seguranca e autonomia']
- **Resposta do sistema:** A acessibilidade é direito que garante à pessoa com deficiência ou com mobilidade reduzida viver de forma independente e exercer seus direitos de cidadania e de participação social.
- **Fontes citadas:** ['l13146_art53', 'l13146_art1']
- **Trechos recuperados:** l13146_art53 (0.9102), l13146_art1 (0.8981), l13146_art79 (0.8856)
- **Causa:** A busca não trouxe o trecho certo no top-3, então o modelo não tinha a informação.
- **Correção proposta:** Melhorar a recuperação: trocar/ajustar o modelo de embeddings, aumentar k, adicionar busca lexical (BM25) híbrida ou revisar o chunking.

## Erro 4 (B. RAG simples)
- **Pergunta:** Quais as barreiras que o Estatuto classifica como urbanísticas?
- **Gabarito:** consta ['vias e nos espacos', 'abertos ao publico']
- **Resposta do sistema:** Não encontrei essa informação na base consultada.
- **Fontes citadas:** []
- **Trechos recuperados:** l10098_art2_p2 (0.8542), ctb_art2 (0.8501), l13146_art112_p2 (0.8492)
- **Causa:** O modelo recusou mesmo com o trecho certo no contexto.
- **Correção proposta:** Reforçar no prompt/treino que, havendo trecho relevante, deve responder; revisar o limiar.

## Erro 5 (B. RAG simples)
- **Pergunta:** Quanto custa um cão-guia para pessoa com deficiência visual?
- **Gabarito:** não consta []
- **Resposta do sistema:** O custo de um cão-guia para pessoa com deficiência visual pode variar dependendo da região e do tipo de cão escolhido. Em geral, o custo inclui o adquirement, alimentação, cuidados veterinários e possíveis tratamentos para doenças específicas. Recomenda-se buscar informações diretamente com clínicos veterinários ou instituições de apoio aos deficientes visuais para obter mais detalhes e orçamentos específicos.
- **Fontes citadas:** ['l13146_art117']
- **Trechos recuperados:** l13146_art117 (0.8889), d5296_art6_p2 (0.8749), d5296_art61 (0.8697)
- **Causa:** A pergunta não está na base, mas o sistema respondeu como se estivesse.
- **Correção proposta:** Calibrar o limiar de similaridade com mais casos 'não consta' e exigir que a resposta cite um trecho.

