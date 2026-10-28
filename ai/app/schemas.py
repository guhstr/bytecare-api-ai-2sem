from typing import Any, Literal

from pydantic import BaseModel, Field


class AnimalContext(BaseModel):
    id: int | str
    nome: str
    tipo: str
    raca: str | None = None
    dataNascimento: str | None = None
    idade: str | int | None = None
    observacaoGeral: str | None = None
    subcategoria: str | None = None


class AnaliseRequest(BaseModel):
    animal: AnimalContext
    preventivos: list[dict[str, Any]] = Field(
        default_factory=list
    )
    terapeuticos: list[dict[str, Any]] = Field(
        default_factory=list
    )
    bem_estar: list[dict[str, Any]] = Field(
        default_factory=list
    )


class RegistrosAnalisados(BaseModel):
    preventivos: int
    terapeuticos: int
    bem_estar: int


class AnaliseIA(BaseModel):
    animal_id: int | str
    nome_animal: str
    prioridade: Literal[
        "baixa",
        "moderada",
        "alta",
        "urgente",
    ]
    resumo: str
    fatores_relevantes: list[str]
    proximos_passos: list[str]
    sinais_atencao: list[str]
    procurar_veterinario: bool
    aviso_seguranca: str
    registros_analisados: RegistrosAnalisados
    modo: Literal[
        "gemini",
        "mock",
    ] = "gemini"


class ChatMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]
    content: str


class ChatAnimalCadastro(BaseModel):
    nome: str
    especie: Literal[
        "CACHORRO",
        "GATO",
        "PEIXE",
        "BOVINO",
        "EQUINO",
        "GALINHA",
        "PAPAGAIO",
        "CANARIO",
        "CALOPSITA",
    ]
    raca: str
    idade: int
    observacao_geral: str | None = None


class ChatVacinaCadastro(BaseModel):
    nome_vacina: str
    descricao: str | None = None
    proximo_previsto: str | None = None


class ChatRequest(BaseModel):
    usuario: str | None = None
    mensagem: str

    historico: list[ChatMessage] = Field(
        default_factory=list
    )

    animal: AnimalContext | None = None

    preventivos: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    terapeuticos: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    bem_estar: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):
    resposta: str

    nivel_atencao: Literal[
        "normal",
        "atencao",
        "urgente",
    ] = "normal"

    procurar_veterinario: bool = False

    aviso_seguranca: str = (
        "As orientações do Assistente ByteCare "
        "não substituem avaliação de um "
        "médico-veterinário."
    )

    modo: Literal[
        "gemini",
        "mock",
    ] = "gemini"

    acao: Literal[
        "nenhuma",
        "cadastrar_animal",
        "cadastrar_vacina",
    ] = "nenhuma"

    animal_cadastro: (
        ChatAnimalCadastro | None
    ) = None

    vacina_cadastro: (
        ChatVacinaCadastro | None
    ) = None