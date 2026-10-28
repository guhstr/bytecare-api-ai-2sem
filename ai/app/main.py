import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    AnaliseIA,
    AnaliseRequest,
    ChatRequest,
    ChatResponse,
)

from .mock_service import create_mock_analysis

load_dotenv()

app = FastAPI(
    title="ByteCare Intelligence API",
    version="1.1.0",
    description=(
        "Serviço de Inteligência Artificial do ByteCare. "
        "Realiza análise de histórico animal e oferece o "
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

@app.get("/")
def root():
    return {
        "service": "ByteCare Intelligence API",
        "status": "online",
        "version": "1.1.0",
    }

@app.get("/api/v1/health")
def health():

    mode = os.getenv(
        "BYTECARE_AI_MODE",
        "mock",
    ).strip().lower()

    return {
        "status": "ok",
        "service": "bytecare-intelligence",
        "mode": mode,
        "gemini_key_configured": bool(
            os.getenv("GEMINI_API_KEY")
        ),
    }

@app.post(
    "/api/v1/analises",
    response_model=AnaliseIA,
)
def analisar(
    payload: AnaliseRequest,
):

    mode = os.getenv(
        "BYTECARE_AI_MODE",
        "mock",
    ).strip().lower()

    try:

        if mode == "gemini":

            from .gemini_service import (
                GeminiAnalysisService,
            )

            service = (
                GeminiAnalysisService()
            )

            return service.analyze(
                payload
            )

        return create_mock_analysis(
            payload
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Falha ao gerar análise "
                f"de IA: {exc}"
            ),
        ) from exc

@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
)
def conversar(
    payload: ChatRequest,
):

    mode = os.getenv(
        "BYTECARE_AI_MODE",
        "mock",
    ).strip().lower()

    try:

        from .chat_service import (
            GeminiChatService,
            create_mock_chat_response,
        )

        if mode == "gemini":

            service = (
                GeminiChatService()
            )

            return service.chat(
                payload
            )

        return create_mock_chat_response(
            payload
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Falha no Assistente "
                f"ByteCare: {exc}"
            ),
        ) from exc