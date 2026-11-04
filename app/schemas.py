from typing import Any, Literal

from pydantic import BaseModel, Field


Prioridade = Literal[
    "baixa",
    "moderada",
    "alta",
    "urgente",
]


class AnimalContext(BaseModel):
    id: int | str
    nome: str
    tipo: str
    raca: str | None = None
    dataNascimento: str | None = None
    idade: str | int | None = None
    observacaoGeral: str | None = None
    subcategoria: str | None = None
    sexo: str | None = None
    peso: float | str | None = None
    castrado: bool | None = None


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
    consultas: list[dict[str, Any]] = Field(
        default_factory=list
    )
    comportamento: list[dict[str, Any]] = Field(
        default_factory=list
    )


class RegistrosAnalisados(BaseModel):
    preventivos: int
    terapeuticos: int
    bem_estar: int


class AnaliseIA(BaseModel):
    animal_id: int | str
    nome_animal: str
    prioridade: Prioridade
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


# ---------------------------------------------------------------------------
# Plano de Cuidado Personalizado (Sprint 3 - CLYVO VET)
# ---------------------------------------------------------------------------


class PlanoCuidadoRequest(AnaliseRequest):
    data_referencia: str | None = Field(
        default=None,
        description=(
            "Data usada como 'hoje' no cálculo de prazos "
            "(YYYY-MM-DD). Opcional; útil para testes."
        ),
    )


class AcaoCuidado(BaseModel):
    titulo: str
    descricao: str
    categoria: Literal[
        "urgencia",
        "preventivo",
        "terapeutico",
        "consulta",
        "bem_estar",
        "comportamento",
    ]
    prioridade: Prioridade
    prazo_dias: int
    motivo: str
    origem_dados: list[str]


class ServicoRecomendado(BaseModel):
    codigo: str
    nome: str
    motivo: str
    prioridade: Prioridade
    score: int


class PerfilPersonalizacao(BaseModel):
    especie: str
    fase_vida: Literal[
        "filhote",
        "adulto",
        "senior",
        "indefinida",
    ]
    idade_anos: float | None
    vacinas_essenciais: list[str]
    vacinas_registradas: list[str]
    vacinas_pendentes: list[str]
    condicoes: list[str] = Field(
        default_factory=list,
        description="Condições de saúde registradas pelo tutor (ex.: ausência de um membro).",
    )


class PlanoCuidado(BaseModel):
    animal_id: int | str
    nome_animal: str
    perfil: PerfilPersonalizacao
    score_risco: int
    prioridade: Prioridade
    acoes: list[AcaoCuidado]
    servicos_recomendados: list[ServicoRecomendado]
    mensagem_tutor: str
    resumo_clinica: str
    procurar_veterinario: bool
    aviso_seguranca: str
    modo: Literal[
        "gemini",
        "mock",
    ] = "mock"


class PersonalizacaoTexto(BaseModel):
    """Único trecho gerado pelo LLM no plano de cuidado."""

    mensagem_tutor: str
    resumo_clinica: str


class PriorizacaoClinicaRequest(BaseModel):
    pacientes: list[PlanoCuidadoRequest] = Field(
        min_length=1,
    )
    data_referencia: str | None = None


class PacientePriorizado(BaseModel):
    posicao: int
    animal_id: int | str
    nome_animal: str
    especie: str
    score_risco: int
    prioridade: Prioridade
    motivo_principal: str
    acao_principal: str | None = None
    motivo: str | None = None
    acao_sugerida_clinica: str
    servicos_recomendados: list[str]


class PriorizacaoClinica(BaseModel):
    total_pacientes: int
    distribuicao: dict[str, int]
    pacientes: list[PacientePriorizado]
    aviso_seguranca: str


class ServicoCatalogo(BaseModel):
    codigo: str
    nome: str
    descricao: str


# ---------------------------------------------------------------------------
# Assistente conversacional
# ---------------------------------------------------------------------------


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
    idade: int = Field(0, description="Idade em anos completos.")
    idade_meses: int | None = Field(
        None, description="Idade total em meses. Use para filhotes (ex.: 10 meses = 10)."
    )
    observacao_geral: str | None = None


class ChatVacinaCadastro(BaseModel):
    nome_vacina: str
    descricao: str | None = None
    proximo_previsto: str | None = None


class ChatObservacaoCadastro(BaseModel):
    titulo: str = Field(description="Título curto do registro, ex.: 'Condição física: ausência de membro'.")
    descricao: str = Field(description="O que o tutor relatou, com as palavras dele.")
    categoria: Literal["SAUDE", "COMPORTAMENTO", "ALIMENTACAO"] = "SAUDE"
    permanente: bool = Field(
        False, description="True para condições que não mudam (amputação, cegueira, alergia, doença crônica)."
    )


class ChatAgendamento(BaseModel):
    servicos: list[str] = Field(description="Ex.: ['Consulta de rotina', 'Vacinação'].")
    data_preferida: str | None = Field(None, description="Data no formato AAAA-MM-DD. Null se o tutor aceitar qualquer dia.")
    horario: str | None = Field(None, description="Horário preferido no formato HH:MM.")
    periodo: Literal["manha", "tarde", "noite"] | None = None
    observacao: str | None = Field(None, description="Detalhes úteis para a clínica, ex.: vacinas a avaliar.")


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

    fora_do_escopo: bool = False

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
        "registrar_observacao",
        "agendar",
        "apagar_animal",
        "listar_animais",
    ] = "nenhuma"

    animal_cadastro: (
        ChatAnimalCadastro | None
    ) = None

    vacina_cadastro: (
        ChatVacinaCadastro | None
    ) = None

    observacao_cadastro: (
        ChatObservacaoCadastro | None
    ) = None

    # Só com acao = cadastrar_animal: vacinas que o pet já tomou, registradas
    # no histórico logo depois do cadastro (junto com observacao_cadastro).
    vacinas_cadastro: list[ChatVacinaCadastro] = Field(default_factory=list)

    agendamento: (
        ChatAgendamento | None
    ) = None
