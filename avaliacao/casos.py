"""Casos de teste com gabarito (40 'consta' + 10 'não consta').

Gabarito por EVIDÊNCIA: `evidencia` é uma frase que deve existir no texto de pelo menos um trecho da base;
os trechos que a contêm viram os 'relevantes' (recall@k e citação correta). `resposta_contem` são termos/radicais
(qualquer um serve) que a resposta correta deve conter. Casos cuja evidência não é achada na base baixada são
LISTADOS por `preparar` e ficam de fora até você corrigir a frase (evita gabarito errado).
Estes casos NÃO são usados no treino do LoRA."""
import json
from pathlib import Path

from src.retrieval import resolver_relevantes


def C(p, ev, rc):
    return {"pergunta": p, "evidencia": ev, "resposta_contem": rc, "consta": True}


def N(p):
    return {"pergunta": p, "consta": False}


CASOS = [
    C("O que a lei de acessibilidade entende por pessoa com mobilidade reduzida?", "dificuldade de movimentar-se", ["dificuldade de movimentar"]),
    C("O que são barreiras urbanísticas?", "barreiras urbanísticas", ["vias publicas", "espacos publicos", "espacos de uso"]),
    C("Para que serve o passeio público segundo a Lei 10.098?", "circulação de pedestres", ["circulacao de pedestres"]),
    C("As vias públicas e os parques precisam ser projetados de forma acessível?", "dos parques e dos demais espaços de uso público", ["acessiveis"]),
    C("Quais normas técnicas devem ser seguidas no projeto de itinerários e passagens de pedestres?", "itinerários e as passagens de pedestres", ["abnt", "normas tecnicas"]),
    C("Vias públicas que já existem precisam ser adaptadas para acessibilidade?", "ordem de prioridade", ["adaptad"]),
    C("Os semáforos para pedestres precisam emitir sinal sonoro?", "sinal sonoro", ["sonoro"]),
    C("Estacionamentos em vias públicas precisam reservar vagas para pessoas com deficiência?", "áreas de estacionamento de veículos", ["vagas"]),
    C("Banheiros públicos em praças e parques precisam ser acessíveis?", "parques, praças, jardins e espaços livres públicos", ["sanitario", "acessiveis"]),
    C("Quem é considerado pessoa com deficiência segundo o Estatuto?", "impedimento de longo prazo", ["longo prazo"]),
    C("O que significa acessibilidade segundo o Estatuto da Pessoa com Deficiência?", "com segurança e autonomia", ["seguranca e autonomia"]),
    C("O que é desenho universal?", "sem necessidade de adaptação", ["sem necessidade de adapta", "todas as pessoas"]),
    C("A pessoa com deficiência pode sofrer discriminação?", "igualdade de oportunidades", ["igualdade de oportunidades", "discrimina"]),
    C("O que a lei diz sobre o direito ao transporte e à mobilidade da pessoa com deficiência?", "direito ao transporte e à mobilidade", ["direito ao transporte e a mobilidade"]),
    C("Para que serve a acessibilidade como direito?", "viver de forma independente", ["viver de forma independente"]),
    C("Projetos abertos ao público na zona urbana e rural devem seguir qual princípio?", "tanto na zona urbana como na rural", ["desenho universal"]),
    C("Edificações de uso coletivo que já existem precisam ser acessíveis?", "já existentes devem garantir acessibilidade", ["ja existentes", "dependencias"]),
    C("Quem tem direito a atendimento prioritário?", "crianças de colo", ["criancas de colo", "gestantes"]),
    C("Idosos têm atendimento prioritário a partir de qual idade?", "idade igual ou superior a 60", ["60", "sessenta"]),
    C("Uma mãe com carrinho de bebê tem direito a atendimento prioritário?", "crianças de colo", ["criancas de colo", "lactantes", "gestantes"]),
    C("O que o Decreto 5.296 exige no planejamento e na urbanização de vias, praças e logradouros?", "logradouros, parques e demais espaços de uso público", ["normas tecnicas", "abnt"]),
    C("O pedestre tem direito de usar a calçada?", "assegurada ao pedestre a utilização dos passeios", ["assegurad", "passeios"]),
    C("Posso atravessar fora da faixa se houver faixa de pedestres por perto?", "cinquenta metros", ["cinquenta metros", "50 metros"]),
    C("Quem tem prioridade de passagem na faixa de pedestres?", "prioridade de passagem", ["prioridade de passagem"]),
    C("O que diz o Código de Trânsito sobre estacionar na calçada?", "sobre faixa destinada a pedestre", ["passeio", "faixa destinada a pedestre"]),
    C("O pedestre pode andar na pista quando não existe calçada?", "quando não houver passeios", ["bordos da pista", "sentido contrario", "prioridade"]),
    C("A partir de que idade o idoso tem gratuidade no transporte coletivo urbano?", "gratuidade dos transportes coletivos públicos urbanos", ["65", "sessenta e cinco"]),
    C("Como o Estatuto trata a prioridade da pessoa idosa?", "absoluta prioridade", ["absoluta prioridade"]),
    C("Quais são os princípios da Política Nacional de Mobilidade Urbana?", "acessibilidade universal", ["acessibilidade universal"]),
    C("Na mobilidade urbana, qual modo de deslocamento tem prioridade?", "não motorizados sobre os motorizados", ["nao motorizados"]),
    C("O que é dado pessoal na LGPD?", "identificada ou identificável", ["identificada ou identificavel"]),
    C("O que é dado pessoal sensível?", "origem racial ou étnica", ["origem racial"]),
    C("O que significa o princípio da necessidade na LGPD?", "mínimo necessário para a realização de suas finalidades", ["minimo necessario"]),
    C("Quais direitos o titular de dados pessoais tem?", "confirmação da existência de tratamento", ["confirmacao da existencia de tratamento"]),
    C("O que é anonimização?", "meios técnicos razoáveis e disponíveis", ["meios tecnicos"]),
    C("O que é consentimento segundo a LGPD?", "livre, informada e inequívoca", ["livre informada e inequivoca"]),
    C("De quem é o dever de assegurar os direitos da pessoa com deficiência?", "dever do Estado, da sociedade e da família", ["estado da sociedade e da familia", "sociedade e da familia"]),
    C("Construções novas abertas ao público precisam ser acessíveis?", "a construção, a reforma, a ampliação ou a mudança de uso", ["acessiveis"]),
    C("O que é pessoa com mobilidade reduzida segundo o Estatuto da Pessoa com Deficiência?", "redução efetiva da mobilidade, da flexibilidade, da coordenação motora ou da percepção", ["coordenacao motora"]),
    C("Quais as barreiras que o Estatuto classifica como urbanísticas?", "vias e nos espaços públicos e privados abertos ao público", ["vias e nos espacos", "abertos ao publico"]),
    C("O que é acessibilidade na lei de 2000?", "possibilidade e condição de alcance", ["possibilidade e condicao de alcance", "alcance"]),
    # ---- não consta (a base NÃO tem ABNT, previsão do tempo, telefones, prazos municipais etc.)
    N("Qual a largura mínima da faixa livre de uma calçada?"),
    N("Qual a inclinação máxima permitida para rampas de calçada?"),
    N("Qual o telefone da subprefeitura de Santo Amaro?"),
    N("Qual a previsão do tempo para amanhã em São Paulo?"),
    N("Quanto custa um cão-guia para pessoa com deficiência visual?"),
    N("Quais as dimensões do piso tátil de alerta?"),
    N("Como faço para declarar o imposto de renda?"),
    N("Qual o horário de funcionamento do metrô de São Paulo?"),
    N("Quem ganhou a Copa do Mundo de 2014?"),
    N("Em quantos dias a Prefeitura de São Paulo é obrigada a consertar uma calçada depois de uma solicitação no 156?"),
]


def preparar(trechos, destino="avaliacao/casos_teste.jsonl"):
    ok, invalidos = [], []
    for c in CASOS:
        c = dict(c)
        if c["consta"]:
            c["relevantes"] = resolver_relevantes(c, trechos)
            if not c["relevantes"]:
                invalidos.append(c)
                continue
        else:
            c["relevantes"], c["resposta_contem"] = [], []
        ok.append(c)
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        for c in ok:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    return ok, invalidos


def carregar(destino="avaliacao/casos_teste.jsonl"):
    with open(destino, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]
