import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .care_engine import catalogo_servicos
from .guardrails import (
    MENSAGEM_FORA_DO_ESCOPO,
    fora_do_escopo,
    tentativa_de_manipulacao,
)
from .mock_service import (
    build_care_plan,
    create_mock_analysis,
    prioritize_patients,
)
from .risk_engine import has_urgent_signal
from .schemas import (
    AnaliseIA,
    AnaliseRequest,
    ChatRequest,
    ChatResponse,
    PlanoCuidado,
    PlanoCuidadoRequest,
    PriorizacaoClinica,
    PriorizacaoClinicaRequest,
    ServicoCatalogo,
)

load_dotenv()

logger = logging.getLogger("bytecare")

VERSION = "2.0.0"

app = FastAPI(
    title="ByteCare Intelligence API",
    version=VERSION,
    description=(
        "Componente de Inteligência Artificial do ByteCare para a CLYVO VET. "
        "Gera planos de cuidado personalizados, recomenda serviços da clínica, "
        "prioriza pacientes, analisa o histórico do pet e oferece o "
        "Assistente ByteCare conversacional."
    ),
)

cors_env = os.getenv(
    "CORS_ORIGINS",
    "*",
).strip()

if cors_env == "*":
    origins = ["*"]
    allow_credentials = False
else:
    origins = [
        origin.strip()
        for origin in cors_env.split(",")
        if origin.strip()
    ]
    allow_credentials = True


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _mode() -> str:
    """Usa Gemini somente quando o modo pede e a chave existe."""
    mode = os.getenv(
        "BYTECARE_AI_MODE",
        "mock",
    ).strip().lower()

    if mode == "gemini" and os.getenv("GEMINI_API_KEY", "").strip():
        return "gemini"

    return "mock"


@app.get("/")
def root():
    return {
        "service": "ByteCare Intelligence API",
        "status": "online",
        "version": VERSION,
        "docs": "/docs",
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "service": "bytecare-intelligence",
        "version": VERSION,
        "mode": _mode(),
        "gemini_key_configured": bool(
            os.getenv("GEMINI_API_KEY", "").strip()
        ),
    }


@app.get(
    "/api/v1/servicos",
    response_model=list[ServicoCatalogo],
)
def listar_servicos():
    return catalogo_servicos()


@app.post(
    "/api/v1/plano-cuidado",
    response_model=PlanoCuidado,
)
def gerar_plano_cuidado(
    payload: PlanoCuidadoRequest,
):
    if _mode() == "gemini":
        try:
            from .gemini_service import GeminiCarePlanService

            return GeminiCarePlanService().build(payload)

        except Exception as exc:
            # O plano é determinístico; sem o LLM, só os textos mudam.
            logger.warning("Gemini indisponível, usando textos padrão: %s", exc)

    return build_care_plan(payload)


@app.post(
    "/api/v1/clinica/priorizacao",
    response_model=PriorizacaoClinica,
)
def priorizar_pacientes(
    payload: PriorizacaoClinicaRequest,
):
    return prioritize_patients(payload)


@app.post(
    "/api/v1/analises",
    response_model=AnaliseIA,
)
def analisar(
    payload: AnaliseRequest,
):
    if _mode() == "gemini":
        try:
            from .gemini_service import GeminiAnalysisService

            return GeminiAnalysisService().analyze(payload)

        except Exception as exc:
            logger.warning("Gemini indisponível na análise, usando modo mock: %s", exc)

    return create_mock_analysis(payload)


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
)
def conversar(
    payload: ChatRequest,
):
    from .chat_service import (
        GeminiChatService,
        apply_output_guardrails,
        create_mock_chat_response,
    )

    # Guardrail de entrada: não chama o LLM para manipulação ou assunto externo.
    # Um sinal de urgência sempre prevalece.
    if not has_urgent_signal(payload.mensagem) and (
        tentativa_de_manipulacao(payload.mensagem)
        or fora_do_escopo(payload.mensagem)
    ):
        return ChatResponse(
            resposta=MENSAGEM_FORA_DO_ESCOPO,
            fora_do_escopo=True,
            modo=_mode(),
        )

    response = None

    if _mode() == "gemini":
        try:
            response = GeminiChatService().chat(payload)

        except Exception as exc:
            logger.warning("Gemini indisponível no chat, usando modo mock: %s", exc)

    if response is None:
        response = create_mock_chat_response(payload)

    return apply_output_guardrails(response, payload)
