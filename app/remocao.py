"""
Pedidos sobre os pets do usuário pelo chat: apagar um pet e listar os pets.

Exemplos: "apaga o Draco", "quero excluir o cadastro dele", "remove esse pet".
A IA só reconhece o pedido; o app pede a confirmação e a API principal decide
se o usuário pode apagar (a clínica apaga qualquer pet; o tutor, só os seus).
"""

import re

from .risk_engine import _normalize
from .schemas import ChatRequest

VERBOS = r"(apag\w*|exclu\w*|delet\w*|remov\w*)"

# O que pode ser apagado pelo chat: o pet, o cadastro dele ou um pronome logo após o verbo.
ALVOS = r"(animal|animais|pet|bicho|cachorr\w*|gat[oa]|cadastro|perfil|ficha)"

# Pedidos de remoção de outras coisas não apagam o pet.
OUTROS = re.compile(
    r"\b(agendament\w*|consulta\w*|horario\w*|vacina\w*|registro\w*|observac\w*|condic\w*|"
    r"notificac\w*|mensage\w*|conversa\w*|historico|tratament\w*|carrapat\w*|pulga\w*|"
    r"sujeira|mancha\w*|pelos?)\b"
)


def pede_remocao_animal(texto: str, nome_pet: str | None = None) -> bool:
    normalizado = _normalize(texto)
    if not re.search(rf"\b{VERBOS}\b", normalizado):
        return False
    if OUTROS.search(normalizado) and not re.search(r"\bcadastro\b", normalizado):
        return False
    alvos = [rf"\b{VERBOS}\b.*\b{ALVOS}\b", rf"\b{VERBOS}\s+(ele|ela|esse|essa|este|esta)\b"]
    if nome_pet:
        alvos.append(rf"\b{VERBOS}\b.*\b{re.escape(_normalize(nome_pet))}\b")
    return any(re.search(padrao, normalizado) for padrao in alvos)


def pedido_remocao(request: ChatRequest) -> bool:
    nome = request.animal.nome if request.animal else None
    return pede_remocao_animal(request.mensagem, nome)


# "quais são meus pets", "lista meus animais", "quantos pets eu tenho".
PETS = r"(pets?|animais|bichos?|cachorros|gatos)"
LISTA = re.compile(
    rf"\b(quais|quantos|que|list\w*|mostr\w*|ver|exib\w*|tod[oa]s)\b.*\b{PETS}\b"
)
SO_MEUS_PETS = re.compile(rf"^\s*(e\s+)?(os\s+)?(meus|minhas)\s+{PETS}\s*\??\s*$")


def pede_lista_pets(texto: str) -> bool:
    normalizado = _normalize(texto)
    if re.search(rf"\b{VERBOS}\b", normalizado):
        return False
    if SO_MEUS_PETS.search(normalizado):
        return True
    # Precisa falar dos pets do usuário: "meus", "tenho", "eu" ou "cadastrados".
    return bool(LISTA.search(normalizado)) and bool(
        re.search(r"\b(meus|minhas|tenho|eu|cadastrad\w*)\b", normalizado)
    )
