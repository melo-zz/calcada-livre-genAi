# Passo a passo — Generative AI for Engineering (prazo: 19/11 às 23h55)

## 0. Hoje à noite (30 min)
1. Crie o repositório público no GitHub e suba esta pasta inteira. Troque `SEU_USUARIO/SEU_REPOSITORIO` e `COLE_AQUI` no `README.md`.
2. **Confirme com o grupo os nomes completos** (README pede nome completo; faltar nome/RM custa −0,5 em Big Data e zera o Maker Lab).

## 2. Generative AI (11 e 12/11)
1. Abra `notebooks/01_base_e_casos.ipynb` no Google Colab (upload ou "abrir do GitHub"), GPU T4. Troque `REPO` na 1ª célula. Rode.
2. **Veja a saída "casos SEM evidência".** Se sobrarem menos de ~35 casos "consta", me mande a lista: eu ajusto as frases-evidência.
3. Rode 02 (recall e limiar), depois 03 (LoRA, ~30 min) e 04 (placar e erros), na mesma sessão.
4. Baixe os 4 notebooks **com saídas** e as pastas `base/` e `avaliacao/` geradas; faça commit no GitHub.
5. Preencha `docs/RELATORIO.md` colando os arquivos de `avaliacao/` (tudo marcado com COLE_AQUI) e grave um vídeo curto (2–3 min) do assistente respondendo 1 pergunta que consta, 1 que não consta e 1 explicação de ocorrência; link no relatório.
6. Se o Colab não aguentar o LoRA: avise, o plano B é agente com ferramentas (vale os mesmos 2 pontos).

## 4. Fechamento (18 e 19/11)
1. Rode `python scripts/checar_entrega.py` na raiz (confere nomes/RMs, segredos, arquivos proibidos e notebooks sem saída). Corrija tudo que for ERRO.
2. Abra o repositório numa **janela anônima** (tem que estar público até uma semana depois da entrega).
3. Um integrante envia no Teams de Generative AI até **19/11, 23h55** (de preferência até o meio-dia): links do repositório e do vídeo.

## O que tira pontos
Nome/RM faltando · chave, senha ou dado pessoal real no repositório (−1,0) · prints sem legenda/fora de ordem (até −1,0) · repositório privado/vazio (zera os itens) · exemplo do enunciado sem adaptar (zera itens 01 e 07 de Big Data).
