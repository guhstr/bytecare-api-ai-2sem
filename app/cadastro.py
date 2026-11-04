"""
Cadastro de animal pelo chat.

Lê as mensagens do tutor e identifica nome, espécie, raça e idade do animal.
Funciona nos dois modos (Gemini e mock): no modo Gemini serve de conferência
e completa o que o modelo não preencheu; no mock conduz a conversa sozinho.
A IA só sugere o cadastro; quem grava é a API principal, depois que o tutor
confirma no app.
"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from .observacao import PERMANENTES, _categoria, _titulo, pede_registro_observacao
from .risk_engine import _normalize
from .schemas import ChatAnimalCadastro, ChatObservacaoCadastro, ChatRequest, ChatVacinaCadastro

INTENCAO = re.compile(r"\b(cadastr\w*|registr\w*|adicion\w*|inclu\w*|salv\w*)\b")
PALAVRAS_ANIMAL = re.compile(
    r"\b(pet|animal|bicho|cao|caes|cachorr[oa]s?|cadela|filhote|gat[oa]s?|peixe|cavalo|egua|"
    r"vaca|boi|galinha|papagaio|canario|calopsita)\b"
)
PALAVRAS_VACINA = re.compile(r"\b(vacin\w*|antirrabica|v8|v10|v3|v4|v5)\b")

# Mensagens do app que encerram um cadastro (salvo ou cancelado).
FIM_CADASTRO = ("foi cadastrad", "cadastro cancelado")

ESPECIE_POR_PALAVRA = {
    "cao": "CACHORRO", "caes": "CACHORRO", "cachorro": "CACHORRO", "cachorra": "CACHORRO",
    "cachorros": "CACHORRO", "cadela": "CACHORRO", "dog": "CACHORRO",
    "gato": "GATO", "gata": "GATO", "gatos": "GATO", "felino": "GATO",
    "peixe": "PEIXE",
    "cavalo": "EQUINO", "egua": "EQUINO", "equino": "EQUINO",
    "vaca": "BOVINO", "boi": "BOVINO", "bezerro": "BOVINO", "bovino": "BOVINO",
    "galinha": "GALINHA",
    "papagaio": "PAPAGAIO",
    "canario": "CANARIO",
    "calopsita": "CALOPSITA",
}

# Raças mais comuns: termo normalizado -> (nome exibido, espécie)
RACAS = {
    "husky siberiano": ("Husky Siberiano", "CACHORRO"),
    "husky": ("Husky Siberiano", "CACHORRO"),
    "golden retriever": ("Golden Retriever", "CACHORRO"),
    "golden": ("Golden Retriever", "CACHORRO"),
    "labrador": ("Labrador", "CACHORRO"),
    "poodle": ("Poodle", "CACHORRO"),
    "shih tzu": ("Shih Tzu", "CACHORRO"),
    "shitzu": ("Shih Tzu", "CACHORRO"),
    "yorkshire": ("Yorkshire", "CACHORRO"),
    "bulldog frances": ("Bulldog Francês", "CACHORRO"),
    "bulldog ingles": ("Bulldog Inglês", "CACHORRO"),
    "bulldog": ("Bulldog", "CACHORRO"),
    "pug": ("Pug", "CACHORRO"),
    "beagle": ("Beagle", "CACHORRO"),
    "pastor alemao": ("Pastor Alemão", "CACHORRO"),
    "rottweiler": ("Rottweiler", "CACHORRO"),
    "pinscher": ("Pinscher", "CACHORRO"),
    "dachshund": ("Dachshund", "CACHORRO"),
    "salsicha": ("Dachshund", "CACHORRO"),
    "border collie": ("Border Collie", "CACHORRO"),
    "chihuahua": ("Chihuahua", "CACHORRO"),
    "spitz alemao": ("Spitz Alemão", "CACHORRO"),
    "lulu da pomerania": ("Spitz Alemão", "CACHORRO"),
    "maltes": ("Maltês", "CACHORRO"),
    "akita": ("Akita", "CACHORRO"),
    "schnauzer": ("Schnauzer", "CACHORRO"),
    "boxer": ("Boxer", "CACHORRO"),
    "pitbull": ("Pitbull", "CACHORRO"),
    "pit bull": ("Pitbull", "CACHORRO"),
    "lhasa apso": ("Lhasa Apso", "CACHORRO"),
    "dalmata": ("Dálmata", "CACHORRO"),
    "doberman": ("Doberman", "CACHORRO"),
    "persa": ("Persa", "GATO"),
    "siames": ("Siamês", "GATO"),
    "maine coon": ("Maine Coon", "GATO"),
    "angora": ("Angorá", "GATO"),
    "ragdoll": ("Ragdoll", "GATO"),
    "sphynx": ("Sphynx", "GATO"),
    "bengal": ("Bengal", "GATO"),
    "sem raca definida": ("Sem raça definida", None),
    "srd": ("Sem raça definida", None),
    "vira lata": ("Sem raça definida", None),
    "viralata": ("Sem raça definida", None),
}

NUMEROS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12,
}

NAO_SAO_NOMES = {
    "de", "do", "da", "que", "um", "uma", "meu", "minha", "ele", "ela", "e", "o", "a",
    "filhote", "macho", "femea", "novo", "nova", "pet", "animal", "raca", "com", "tem",
    "cachorro", "cachorra", "cao", "gato", "gata", "cadela", "sim", "nao", "ok",
    *ESPECIE_POR_PALAVRA,
}

PERGUNTAS = {
    "nome": "qual é o nome dele",
    "especie": "qual é a espécie (cão, gato, etc.)",
    "raca": "qual é a raça (se não tiver, pode ser sem raça definida)",
    "idade": "qual é a idade aproximada",
}


@dataclass
class EstadoCadastro:
    ativo: bool = False
    nome: str | None = None
    especie: str | None = None
    raca: str | None = None
    idade_meses: int | None = None
    faltando: list[str] = field(default_factory=list)
    # Informações extras ditas durante o cadastro, registradas depois de salvar o pet.
    vacinas: list[ChatVacinaCadastro] = field(default_factory=list)
    observacao: ChatObservacaoCadastro | None = None

    @property
    def pronto(self) -> bool:
        return self.ativo and not self.faltando

    def para_cadastro(self) -> ChatAnimalCadastro:
        return ChatAnimalCadastro(
            nome=self.nome,
            especie=self.especie,
            raca=self.raca,
            idade=self.idade_meses // 12,
            idade_meses=self.idade_meses,
        )


NOVO_ANIMAL = re.compile(r"\b(novo|nova|outro|outra|se chama|chamad[oa]|nome)\b")


def quer_cadastrar_animal(texto: str) -> bool:
    texto = _normalize(texto)
    # "registra que meu cachorro tem uma pata a menos" é observação, não cadastro.
    if pede_registro_observacao(texto) and not (NOVO_ANIMAL.search(texto) or _idade_meses(texto)):
        return False
    return bool(
        INTENCAO.search(texto)
        and PALAVRAS_ANIMAL.search(texto)
        and not PALAVRAS_VACINA.search(texto)
    )


def _idade_meses(texto: str) -> int | None:
    numero = r"(\d+|" + "|".join(NUMEROS) + r")"
    achado = re.search(rf"\b{numero}\s*(mes|meses|ano|anos)\b", texto)
    if not achado:
        return None
    valor = achado.group(1)
    quantidade = int(valor) if valor.isdigit() else NUMEROS[valor]
    return quantidade if achado.group(2).startswith("mes") else quantidade * 12


def _raca(texto: str) -> tuple[str | None, str | None]:
    for termo in sorted(RACAS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(termo)}\b", texto):
            return RACAS[termo]
    achado = re.search(r"\braca\s+(?:e\s+|eh\s+|dele\s+e\s+)?([a-z]+(?:\s+[a-z]+)?)", texto)
    if achado:
        palavras = [p for p in achado.group(1).split() if p not in {"de", "e", "com", "que"}]
        if palavras:
            return " ".join(palavras).title(), None
    return None, None


def _especie(texto: str) -> str | None:
    for palavra, especie in ESPECIE_POR_PALAVRA.items():
        if re.search(rf"\b{palavra}\b", texto):
            return especie
    return None


def _nome(texto: str) -> str | None:
    padroes = [
        r"\b(?:se chama|chama|chamad[oa]|nome dele e|nome dela e|nome e|nome)\s+([a-z]+)",
        r"\b(?:cao|cachorr[oa]|cadela|gat[oa]|pet|filhote|animal)\s*,?\s+(?:o|a)\s+([a-z]+)",
        r"\b(?:o|a)\s+([a-z]+)\s*,?\s+(?:de\s+)?\d+\s*(?:mes|meses|ano|anos)\b",
    ]
    for padrao in padroes:
        achado = re.search(padrao, texto)
        if achado and achado.group(1) not in NAO_SAO_NOMES and len(achado.group(1)) > 1:
            return achado.group(1).capitalize()
    return None


def _nome_em_lista(texto: str) -> str | None:
    """Primeiro item de uma resposta em lista: "Thor, sem raça definida, 5 anos"."""
    primeiro = re.split(r"[,;\n]", texto)[0].strip(" .!?")
    palavras = primeiro.split()
    if not 1 <= len(palavras) <= 2 or re.search(r"\d", primeiro):
        return None
    if any(p in NAO_SAO_NOMES for p in palavras) or _raca(primeiro)[0] or _especie(primeiro):
        return None
    return " ".join(p.capitalize() for p in palavras)


# ---------------------------------------------------------------------------
# Extras do cadastro: vacinas já aplicadas e observações de saúde.
# ---------------------------------------------------------------------------

VACINAS_CONHECIDAS = [
    ("v10", "V10"), ("v11", "V11"), ("v8", "V8"), ("v5", "V5"), ("v4", "V4"), ("v3", "V3"),
    ("antirrabica", "Antirrábica"), ("raiva", "Antirrábica"), ("giardia", "Giárdia"),
    ("gripe", "Gripe canina"), ("tosse dos canis", "Gripe canina"),
    ("leishmaniose", "Leishmaniose"), ("felv", "FeLV"),
]
JA_TOMOU = re.compile(r"\b(tem|tomou|toma|tomad\w*|aplic\w*|vacinad\w*|fez|recebeu|esta com)\b")

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Termos de saúde e comportamento que valem uma observação no histórico.
TERMOS_OBSERVACAO = re.compile(
    r"\b(ganh\w*|perd\w*|peso|gord\w*|obes\w*|magr\w*|cans\w*|tosse\w*|tossind\w*|vomit\w*|"
    r"diarr\w*|coc\w*|manc\w*|dor|alergi\w*|alergic\w*|come\w*|comendo|bebe\w*|dorm\w*|agressiv\w*|"
    r"medo|ansios\w*|pata|patas|ceg[oa]|surd[oa]|respir\w*|febre|ferid\w*|queda|xixi|"
    r"cronic\w*|diabet\w*|epilep\w*|castrad\w*|ofeg\w*|fraco|fraca|desanimad\w*)\b"
)


def _data_proxima(texto: str, hoje: date) -> str | None:
    """Data da próxima dose ("2 de novembro", "02/11", "02/11/2026") em AAAA-MM-DD."""
    achado = re.search(r"\b(\d{1,2})\s+de\s+(" + "|".join(MESES) + r")(?:\s+de\s+(\d{4}))?", texto)
    if achado:
        dia, mes, ano = int(achado.group(1)), MESES[achado.group(2)], achado.group(3)
    else:
        achado = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", texto)
        if not achado:
            return None
        dia, mes, ano = int(achado.group(1)), int(achado.group(2)), achado.group(3)
    if ano:
        ano = int(ano) + (2000 if len(ano) == 2 else 0)
    else:
        # Sem ano: o deste ano; se já passou há muito tempo, o do ano que vem.
        ano = hoje.year
        try:
            if date(ano, mes, dia) < hoje - timedelta(days=180):
                ano += 1
        except ValueError:
            return None
    try:
        return date(ano, mes, dia).isoformat()
    except ValueError:
        return None


def vacinas_do_texto(texto: str, hoje: date | None = None) -> list[ChatVacinaCadastro]:
    """Vacinas que o tutor diz que o pet já tomou, com a próxima dose se informada."""
    normalizado = _normalize(texto)
    if not JA_TOMOU.search(normalizado):
        return []
    nomes = []
    for termo, nome in VACINAS_CONHECIDAS:
        if re.search(rf"\b{termo}\b", normalizado) and nome not in nomes:
            nomes.append(nome)
    if not nomes:
        return []
    trecho_data = normalizado[normalizado.find("proxim"):] if "proxim" in normalizado else ""
    proxima = _data_proxima(trecho_data, hoje or date.today()) if trecho_data else None
    return [
        ChatVacinaCadastro(
            nome_vacina=nome,
            descricao="Informada pelo tutor no cadastro pelo Assistente ByteCare",
            proximo_previsto=proxima,
        )
        for nome in nomes
    ]


def observacao_do_texto(texto: str) -> ChatObservacaoCadastro | None:
    """Trechos de saúde ou comportamento ditos no meio do cadastro."""
    partes = []
    for trecho in re.split(r"[,;]|\.\s", texto):
        normalizado = _normalize(trecho)
        if (
            not TERMOS_OBSERVACAO.search(normalizado)
            or re.search(r"\bvacin\w*|\bproxim\w*", normalizado)
            or _idade_meses(normalizado)
        ):
            continue
        limpo = re.sub(r"^\s*(e|mas|tambem)\s+", "", trecho.strip(), flags=re.I)
        limpo = re.sub(r"^(ele|ela)\s+", "", limpo, flags=re.I).strip(" .!")
        if len(limpo.split()) >= 2:
            partes.append(limpo)
    if not partes:
        return None
    descricao = "; ".join(partes)
    descricao = descricao[0].upper() + descricao[1:]
    texto_norm = _normalize(descricao)
    categoria = _categoria(texto_norm + " ")
    return ChatObservacaoCadastro(
        titulo=_titulo(descricao, categoria),
        descricao=descricao[:450],
        categoria=categoria,
        permanente=any(t in texto_norm for t in PERMANENTES),
    )


def _resposta_curta(texto: str) -> str | None:
    palavras = texto.strip(" .!?").split()
    if 1 <= len(palavras) <= 3:
        return " ".join(palavras)
    return None


def estado_cadastro(request: ChatRequest) -> EstadoCadastro:
    """Reconstrói o cadastro em andamento a partir da conversa."""
    originais = [(m.role, m.content) for m in request.historico]
    if not originais or originais[-1] != ("user", request.mensagem):
        originais.append(("user", request.mensagem))
    turnos = [(papel, _normalize(texto)) for papel, texto in originais]

    inicio = None
    for i, (papel, texto) in enumerate(turnos):
        if papel == "user" and quer_cadastrar_animal(texto):
            inicio = i
        elif papel == "assistant" and inicio is not None and any(f in texto for f in FIM_CADASTRO):
            inicio = None

    estado = EstadoCadastro()
    if inicio is None:
        return estado
    estado.ativo = True

    pergunta_anterior = ""
    for (papel, texto), (_, original) in zip(turnos[inicio:], originais[inicio:]):
        if papel == "assistant":
            pergunta_anterior = texto
            continue

        for vacina in vacinas_do_texto(original):
            estado.vacinas = [v for v in estado.vacinas if v.nome_vacina != vacina.nome_vacina] + [vacina]
        estado.observacao = observacao_do_texto(original) or estado.observacao

        estado.idade_meses = _idade_meses(texto) or estado.idade_meses
        raca, especie_da_raca = _raca(texto)
        estado.raca = raca or estado.raca
        estado.especie = _especie(texto) or especie_da_raca or estado.especie
        estado.nome = _nome(texto) or estado.nome
        nome_da_lista = None
        if not estado.nome and "nome" in pergunta_anterior:
            nome_da_lista = _nome_em_lista(texto)
            estado.nome = nome_da_lista

        # Resposta curta a uma pergunta do assistente ("Draco", "Husky").
        curta = _resposta_curta(texto)
        if (
            curta
            and not nome_da_lista
            and curta not in NAO_SAO_NOMES
            and not re.search(r"\d", curta)
            and _idade_meses(texto) is None
            and _especie(texto) is None
        ):
            if "nome" in pergunta_anterior and not estado.nome and not raca:
                estado.nome = curta.split()[0].capitalize()
            elif "raca" in pergunta_anterior and not raca and not estado.raca:
                estado.raca = curta.title()

    estado.faltando = [
        campo for campo, valor in [
            ("nome", estado.nome),
            ("especie", estado.especie),
            ("raca", estado.raca),
            ("idade", estado.idade_meses),
        ]
        if valor is None
    ]
    return estado


def pergunta_faltando(estado: EstadoCadastro) -> str:
    perguntas = [PERGUNTAS[c] for c in estado.faltando]
    if len(perguntas) == 1:
        return f"Para concluir o cadastro, me diga {perguntas[0]}."
    return f"Para concluir o cadastro, me diga {', '.join(perguntas[:-1])} e {perguntas[-1]}."


def resumo_cadastro(estado: EstadoCadastro) -> str:
    meses = estado.idade_meses
    idade = f"{meses} {'mês' if meses == 1 else 'meses'}" if meses < 12 else (
        f"{meses // 12} {'ano' if meses // 12 == 1 else 'anos'}"
    )
    especie = {"CACHORRO": "cão", "GATO": "gato"}.get(estado.especie, estado.especie.lower())
    return f"{estado.nome}, {especie}, {estado.raca}, {idade}"


def especie_do_texto(texto: str) -> str | None:
    return _especie(_normalize(texto)) or _raca(_normalize(texto))[1]


def idade_meses_do_texto(texto: str) -> int | None:
    return _idade_meses(_normalize(texto))
