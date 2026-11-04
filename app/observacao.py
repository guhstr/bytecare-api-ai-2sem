"""
Registro de condições e observações no histórico do pet pelo chat.

Exemplos: "registra que ele tem uma pata a menos", "anota no histórico que
ela é alérgica a frango". A IA só sugere o registro; o app pede a confirmação
e a API principal grava (bem-estar do pet e, para condições permanentes,
também as observações do cadastro).
"""

import re

from .risk_engine import _normalize
from .schemas import ChatObservacaoCadastro, ChatRequest

VERBOS = r"(registr\w*|anot\w*|salv\w*|coloc\w*|adicion\w*|inclu\w*|cadastr\w*|acrescent\w*|bot\w*)"

PEDIDO = re.compile(
    rf"\b{VERBOS}\b.*?(\bque\b|\bhistorico\b|\bficha\b|\bprontuario\b|\bobservac\w*|\bcondic\w*|\bproblema\w*)"
)

PALAVRAS_VACINA = re.compile(r"\b(vacin\w*|antirrabica)\b")

CATEGORIAS = [
    ("COMPORTAMENTO", ["comport", "agressiv", "medo", "ansios", "ansiedade", "late muito", "morde", "estress"]),
    ("ALIMENTACAO", ["come ", "comida", "racao", "aliment", "dieta", "peso", "obes", "magro"]),
    ("SAUDE", []),
]

# Condições que não mudam com o tempo vão também para o cadastro do animal.
PERMANENTES = [
    "pata a menos", "sem uma pata", "sem a pata", "nao tem uma pata", "nao tem pata",
    "tres patas", "amput", "membro", "cego", "cega", "cegueira", "surdo", "surda",
    "alergi", "alergic", "cronic", "diabet", "epilep", "displasia", "cardiopat",
    "renal", "castrad", "deficien", "paralis", "paraplegi", "sem rabo", "um olho",
]

PRONOMES = re.compile(r"^(ele|ela|o pet|a pet|meu pet|meu cachorro|minha cachorra|meu gato|minha gata)\s+", re.I)


def pede_registro_observacao(texto: str) -> bool:
    normalizado = _normalize(texto)
    return bool(PEDIDO.search(normalizado)) and not PALAVRAS_VACINA.search(normalizado)


def _conteudo(mensagem: str, nome_pet: str | None) -> str | None:
    """Tira o pedido ('registra que', 'anota no histórico:') e deixa a condição."""
    texto = mensagem.strip()
    corte = re.search(r"\bque\b\s+", texto, re.I)
    if not corte:
        corte = re.search(
            r"(hist[oó]rico|ficha|prontu[aá]rio)(\s+(dele|dela|do\s+\w+|da\s+\w+))?\s*[:,\-]?\s*",
            texto,
            re.I,
        )
    if not corte:
        return None
    conteudo = texto[corte.end():].strip(" .!:,-")
    conteudo = PRONOMES.sub("", conteudo)
    if nome_pet:
        conteudo = re.sub(rf"^(o|a)?\s*{re.escape(nome_pet)}\s+", "", conteudo, flags=re.I)
    conteudo = conteudo.strip(" .!:,-")
    if len(conteudo) < 3:
        return None
    return conteudo[0].upper() + conteudo[1:]


def _categoria(texto: str) -> str:
    for categoria, termos in CATEGORIAS:
        if any(t in texto for t in termos):
            return categoria
    return "SAUDE"


def _titulo(descricao: str, categoria: str) -> str:
    texto = _normalize(descricao)
    if any(t in texto for t in ["pata", "membro", "amput"]):
        return "Condição física: ausência de membro"
    if any(t in texto for t in ["alergi", "alergic"]):
        return "Alergia informada pelo tutor"
    rotulo = {"COMPORTAMENTO": "Comportamento", "ALIMENTACAO": "Alimentação"}.get(categoria, "Saúde")
    return f"{rotulo}: relato do tutor"


def observacao_da_mensagem(request: ChatRequest) -> ChatObservacaoCadastro | None:
    if not pede_registro_observacao(request.mensagem):
        return None
    nome = request.animal.nome if request.animal else None
    descricao = _conteudo(request.mensagem, nome)
    if not descricao:
        return None
    texto = _normalize(descricao)
    categoria = _categoria(texto + " ")
    return ChatObservacaoCadastro(
        titulo=_titulo(descricao, categoria),
        descricao=descricao[:450],
        categoria=categoria,
        permanente=any(t in texto for t in PERMANENTES),
    )
