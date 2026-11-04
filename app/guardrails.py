"""
Guardrails do Assistente ByteCare.

Camadas aplicadas em todas as mensagens, nos modos mock e gemini:

1. Entrada: bloqueia tentativas de alterar as regras do assistente
   (prompt injection) e assuntos claramente fora de saúde e cuidado animal,
   sem chamar o LLM.
2. Saída: o LLM marca respostas fora do escopo; respostas com dose de
   medicamento são substituídas por uma orientação segura.
3. Risco: o motor determinístico define o nível mínimo de atenção
   (aplicado no chat_service).
"""

import re

from .risk_engine import _normalize, contains_term

MENSAGEM_FORA_DO_ESCOPO = (
    "Eu sou o Assistente ByteCare e só consigo ajudar com saúde, bem-estar "
    "e cuidados dos seus animais, como sintomas, vacinas, alimentação, "
    "comportamento e o histórico registrado no app. Como posso ajudar com o seu pet?"
)

MENSAGEM_SEM_DOSE = (
    "Não posso indicar medicamentos nem doses. Alguns remédios de uso humano "
    "são tóxicos para animais. Converse com o médico-veterinário antes de dar "
    "qualquer medicação e siga apenas o que ele prescrever."
)

TENTATIVAS_DE_MANIPULACAO = [
    "ignore as instrucoes",
    "ignore suas instrucoes",
    "ignore todas as instrucoes",
    "ignore as regras",
    "esqueca as instrucoes",
    "esqueca suas regras",
    "desconsidere as instrucoes",
    "ignore previous instructions",
    "ignore all previous",
    "system prompt",
    "prompt do sistema",
    "suas instrucoes internas",
    "modo desenvolvedor",
    "developer mode",
    "jailbreak",
    "finja que voce",
    "aja como se",
    "voce agora e",
    "a partir de agora voce",
    "sem restricoes",
]

# Assuntos que claramente não são sobre animais.
FORA_DO_ESCOPO = [
    "futebol", "campeonato", "politica", "eleicao", "presidente", "bitcoin",
    "criptomoeda", "acoes da bolsa", "investimento", "codigo em", "programar",
    "python", "javascript", "html", "receita de bolo", "receita de", "piada",
    "poema", "redacao", "dever de casa", "trabalho escolar", "matematica",
    "equacao", "filme", "serie", "novela", "musica", "letra da musica",
    "horoscopo", "signo", "namorad", "relacionamento", "viagem", "hotel",
    "previsao do tempo", "clima amanha", "noticia", "jogo de", "videogame",
    "minha saude", "remedio para mim", "estou doente", "eu estou com",
]

# Indicam que a conversa é sobre animais (prevalecem sobre a lista acima).
TERMOS_ANIMAIS = [
    "pet", "animal", "animais", "cachorr", "cao", "caes", "cadel", "filhote",
    "gato", "gata", "felino", "ave", "passaro", "papagaio", "calopsita",
    "canario", "galinha", "peixe", "aquario", "coelho", "cavalo", "equino",
    "egua", "boi", "vaca", "bovino", "bezerro", "veterinari", "vacina",
    "vermifug", "racao", "tutor", "clinica", "pulga", "carrapato", "latindo",
    "miando",
]

PADRAO_DOSE = re.compile(
    r"\b\d+([.,]\d+)?\s?(mg|ml|mcg|g|gotas?|comprimidos?|capsulas?|cps|ui)\b"
    r"|\bmg/kg\b|\bde \d+ em \d+ horas\b|\b\d+ ?vezes ao dia\b",
)


def _tem(texto: str, termos: list[str]) -> bool:
    return any(contains_term(texto, t.strip()) for t in termos)


def texto_simples(texto: str) -> str:
    """Remove marcações de Markdown: o app mostra o texto puro."""
    texto = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), texto)
    texto = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", texto)
    texto = re.sub(r"^\s{0,3}#{1,6}\s*", "", texto, flags=re.M)
    texto = re.sub(r"^(\s*)[*•]\s+", r"\1- ", texto, flags=re.M)
    texto = re.sub(r"`([^`]*)`", r"\1", texto)
    # Datas no formato brasileiro: 2026-11-06 -> 06/11/2026
    texto = re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", r"\3/\2/\1", texto)
    return texto.replace("**", "").strip()


def tentativa_de_manipulacao(mensagem: str) -> bool:
    texto = _normalize(mensagem)
    return any(t in texto for t in TENTATIVAS_DE_MANIPULACAO)


def fora_do_escopo(mensagem: str) -> bool:
    """
    Bloqueio conservador: só barra quando há um assunto claramente externo
    e nenhuma referência a animais. Casos ambíguos seguem para o assistente,
    que também é instruído a recusar temas fora do escopo.
    """
    texto = _normalize(mensagem)
    if not _tem(texto, FORA_DO_ESCOPO):
        return False
    if _tem(texto, TERMOS_ANIMAIS):
        return False
    return True


def contem_dose(resposta: str) -> bool:
    return PADRAO_DOSE.search(_normalize(resposta)) is not None
