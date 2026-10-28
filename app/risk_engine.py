import json
import unicodedata
from dataclasses import dataclass
from typing import Any


PRIORITY_ORDER = {
    "baixa": 0,
    "moderada": 1,
    "alta": 2,
    "urgente": 3,
}

URGENT_TERMS = {
    "dificuldade para respirar": "menção a dificuldade respiratória",
    "nao consegue respirar": "menção a dificuldade respiratória",
    "sem respirar": "menção a ausência de respiração",
    "nao respira": "menção a ausência/dificuldade de respiração",

    "desmaio": "menção a desmaio",
    "desmaiou": "menção a desmaio",
    "inconsciente": "menção a perda de consciência",
    "perdeu a consciencia": "menção a perda de consciência",

    "convuls": "menção a convulsão",

    "sangramento intenso": "menção a sangramento intenso",
    "muito sangue": "menção a sangramento importante",

    "nao consegue ficar em pe": "menção a incapacidade de ficar em pé",
    "nao consegue levantar": "menção a incapacidade de se levantar",

    "dor muito forte": "menção a dor muito intensa",
    "dor insuportavel": "menção a dor muito intensa",

    "barriga muito inchada": "menção a distensão abdominal importante",
    "barriga endurecida": "menção a abdômen endurecido",
    "barriga dura": "menção a abdômen endurecido",

    "tentando vomitar sem conseguir": (
        "menção a tentativas de vômito sem conseguir"
    ),
    "tenta vomitar e nao consegue": (
        "menção a tentativas de vômito sem conseguir"
    ),

    "envenenado": "menção a possível intoxicação",
    "envenenamento": "menção a possível intoxicação",
    "veneno": "menção a possível intoxicação",
    "intoxic": "menção a possível intoxicação",

    "atropelado": "menção a trauma grave",
    "atropelamento": "menção a trauma grave",
}


ATTENTION_TERMS = {
    "vomit": "menção a vômito",
    "diarre": "menção a diarreia",
    "apatia": "menção a apatia",

    "nao come": "menção a recusa alimentar",
    "nao quer comer": "menção a recusa alimentar",
    "sem comer": "menção a recusa alimentar",
    "perda de apetite": "menção a redução de apetite",

    "dor": "menção a dor",

    "ferid": "menção a ferimento",
    "sangr": "menção a sangramento",

    "manco": "menção a alteração na locomoção",
    "mancando": "menção a alteração na locomoção",

    "inquieto": "menção a inquietação",
    "inquieta": "menção a inquietação",

    "fraco": "menção a fraqueza",
    "fraqueza": "menção a fraqueza",

    "tremendo": "menção a tremores",
    "tremor": "menção a tremores",
}

@dataclass
class RiskResult:
    minimum_priority: str
    reasons: list[str]
    red_flags: list[str]
    seek_vet: bool

def _normalize(value: str) -> str:
    """
    Remove acentos e transforma o texto em minúsculas.

    Exemplo:
    'Não está respirando' -> 'nao esta respirando'
    """
    value = unicodedata.normalize("NFKD", value or "")

    return "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    ).lower()


def _flatten_text(data: Any) -> str:
    """
    Converte qualquer payload para texto normalizado para permitir
    a análise determinística dos termos.
    """
    return _normalize(
        json.dumps(
            data,
            ensure_ascii=False,
            default=str,
        )
    )


def _find_terms(
    text: str,
    terms: dict[str, str],
) -> list[str]:
    """
    Procura os termos de risco dentro de um texto normalizado.
    """
    return [
        label
        for term, label in terms.items()
        if term in text
    ]

def has_urgent_signal(text: str) -> bool:
    """
    Usado pelo Assistente ByteCare.

    Retorna True caso a mensagem atual contenha algum sinal
    potencialmente urgente.

    Esta função é usada como guardrail determinístico para impedir
    que o LLM diminua indevidamente a prioridade de uma situação.
    """

    if not text:
        return False

    normalized_text = _normalize(text)

    return any(
        term in normalized_text
        for term in URGENT_TERMS
    )


def evaluate_chat_risk(message: str) -> RiskResult:
    """
    Analisa somente a mensagem enviada pelo usuário no chatbot.

    Não diagnostica doenças.
    Apenas classifica sinais descritos na conversa.
    """

    text = _normalize(message)

    urgent_hits = _find_terms(
        text,
        URGENT_TERMS,
    )

    if urgent_hits:
        return RiskResult(
            minimum_priority="urgente",
            reasons=urgent_hits,
            red_flags=urgent_hits,
            seek_vet=True,
        )

    attention_hits = _find_terms(
        text,
        ATTENTION_TERMS,
    )

    if attention_hits:
        return RiskResult(
            minimum_priority="alta",
            reasons=attention_hits,
            red_flags=[],
            seek_vet=False,
        )

    return RiskResult(
        minimum_priority="baixa",
        reasons=[],
        red_flags=[],
        seek_vet=False,
    )

def evaluate_risk(
    payload: dict[str, Any],
) -> RiskResult:
    """
    Guardrail conservador utilizado pela análise do histórico
    do ByteCare.

    Não diagnostica.

    Apenas detecta informações que podem aumentar a prioridade
    mínima da análise.
    """

    text = _flatten_text(payload)

    urgent_hits = _find_terms(
        text,
        URGENT_TERMS,
    )

    attention_hits = _find_terms(
        text,
        ATTENTION_TERMS,
    )

    if urgent_hits:
        return RiskResult(
            minimum_priority="urgente",
            reasons=urgent_hits,
            red_flags=urgent_hits,
            seek_vet=True,
        )

    if attention_hits:
        return RiskResult(
            minimum_priority="alta",
            reasons=attention_hits,
            red_flags=attention_hits,
            seek_vet=True,
        )

    therapeutic = (
        payload.get("terapeuticos")
        or []
    )

    preventives = (
        payload.get("preventivos")
        or []
    )

    wellbeing = (
        payload.get("bem_estar")
        or []
    )

    reasons: list[str] = []

    minimum = "baixa"

    if therapeutic:
        minimum = "moderada"

        reasons.append(
            "há acompanhamento terapêutico cadastrado"
        )

    if len(wellbeing) >= 3:
        minimum = "moderada"

        reasons.append(
            "há múltiplos registros recentes de bem-estar "
            "para contextualização"
        )

    if preventives and minimum == "baixa":
        reasons.append(
            "há histórico preventivo disponível para acompanhamento"
        )

    return RiskResult(
        minimum_priority=minimum,
        reasons=reasons,
        red_flags=[],
        seek_vet=False,
    )

def enforce_minimum_priority(
    candidate: str,
    minimum: str,
) -> str:
    """
    Impede que uma resposta gerada por IA diminua a prioridade
    calculada pelo motor determinístico.

    Exemplo:

    Motor determinístico -> urgente
    Gemini -> moderada

    Resultado final -> urgente
    """

    candidate = (
        candidate
        if candidate in PRIORITY_ORDER
        else minimum
    )

    return (
        candidate
        if PRIORITY_ORDER[candidate]
        >= PRIORITY_ORDER[minimum]
        else minimum
    )