"""
Cliente Gemini com modelos reserva.

Tenta o modelo principal (GEMINI_MODEL) e, se ele estiver indisponível
(sobrecarga, modelo descontinuado, limite de uso), tenta os modelos de
GEMINI_FALLBACK_MODELS na ordem. Erros de requisição inválida não trocam
de modelo, pois falhariam em todos.
"""

import logging
import os
import time

from google import genai
from google.genai import errors, types

logger = logging.getLogger("bytecare")

DEFAULT_MODEL = "gemini-3.5-flash"
# Ordem: primeiro os que falham rápido quando sem cota, por último os que
# costumam demorar para responder com erro (504). A cota é separada por modelo.
DEFAULT_FALLBACKS = (
    "gemini-3.6-flash,gemini-3.7-flash,gemini-3.8-flash,gemini-3-flash-preview,"
    "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-flash-latest"
)

# Limites para o app (timeout de 45 s) nunca ficar esperando demais.
TIMEOUT_POR_MODELO_MS = 15_000
ORCAMENTO_TOTAL_S = 30

# Códigos em que vale tentar outro modelo.
RETRY_CODES = {404, 429, 500, 503, 504}


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=TIMEOUT_POR_MODELO_MS,
            # A troca de modelo substitui as novas tentativas do SDK.
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def candidate_models() -> list[str]:
    principal = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    reservas = os.getenv("GEMINI_FALLBACK_MODELS", DEFAULT_FALLBACKS).split(",")
    return list(dict.fromkeys(m.strip() for m in [principal, *reservas] if m.strip()))


def generate(
    client: genai.Client,
    contents,
    config: types.GenerateContentConfig,
):
    ultimo_erro: Exception | None = None
    inicio = time.monotonic()

    for model in candidate_models():
        if time.monotonic() - inicio > ORCAMENTO_TOTAL_S - TIMEOUT_POR_MODELO_MS / 1000:
            break
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except errors.APIError as exc:
            if exc.code not in RETRY_CODES:
                raise
            logger.warning("Modelo %s indisponível (%s), tentando o próximo.", model, exc.code)
            ultimo_erro = exc
        except Exception as exc:  # timeout de rede
            logger.warning("Modelo %s sem resposta (%s), tentando o próximo.", model, type(exc).__name__)
            ultimo_erro = exc

    raise RuntimeError(f"Nenhum modelo Gemini disponível: {ultimo_erro}")
