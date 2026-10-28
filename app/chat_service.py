import json
import os

from google import genai
from google.genai import types

from .prompt import CHAT_SYSTEM_PROMPT
from .risk_engine import (
    evaluate_chat_risk,
    has_urgent_signal,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
)

def create_mock_chat_response(
    request: ChatRequest,
) -> ChatResponse:

    risk = evaluate_chat_risk(
        request.mensagem
    )

    animal = getattr(
        request,
        "animal",
        None,
    )

    nome_animal = (
        animal.nome
        if animal
        else "o animal"
    )

    if risk.minimum_priority == "urgente":

        return ChatResponse(
            resposta=(
                f"Pelo que você descreveu sobre {nome_animal}, "
                "existe um sinal que pode representar uma "
                "situação de urgência. Mantenha o animal em "
                "segurança e procure atendimento veterinário "
                "o quanto antes. Não ofereça medicamentos "
                "por conta própria."
            ),
            nivel_atencao="urgente",
            procurar_veterinario=True,
            modo="mock",
        )

    if risk.minimum_priority == "alta":

        return ChatResponse(
            resposta=(
                "Entendi. Quero compreender melhor o que está "
                f"acontecendo com {nome_animal}. "
                "Há quanto tempo você percebeu essa mudança? "
                "Ele está comendo, bebendo água e se "
                "movimentando normalmente?"
            ),
            nivel_atencao="atencao",
            procurar_veterinario=False,
            modo="mock",
        )

    nome_usuario = (
        request.usuario or ""
    ).strip()

    inicio = (
        f"Entendi, {nome_usuario}. "
        if nome_usuario
        else "Entendi. "
    )

    return ChatResponse(
        resposta=(
            inicio
            + "Pode me contar um pouco mais sobre o animal "
            "e o que você observou? Informações sobre quando "
            "começou e mudanças recentes ajudam a entender "
            "melhor a situação."
        ),
        nivel_atencao="normal",
        procurar_veterinario=False,
        modo="mock",
    )

class GeminiChatService:

    def __init__(self) -> None:

        api_key = os.getenv(
            "GEMINI_API_KEY",
            "",
        ).strip()

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não configurada."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        ).strip()

    def _build_history(
        self,
        request: ChatRequest,
    ) -> list[types.Content]:

        history: list[
            types.Content
        ] = []

        recent_history = (
            request.historico[-16:]
        )

        for message in recent_history:

            role = (
                "model"
                if message.role
                == "assistant"
                else "user"
            )

            content = (
                message.content or ""
            ).strip()

            if not content:
                continue

            history.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(
                            text=content
                        )
                    ],
                )
            )

        return history

    def _build_context(
        self,
        request: ChatRequest,
    ) -> str:

        context: list[str] = []

        animal = getattr(
            request,
            "animal",
            None,
        )

        preventivos = (
            getattr(
                request,
                "preventivos",
                None,
            )
            or []
        )

        terapeuticos = (
            getattr(
                request,
                "terapeuticos",
                None,
            )
            or []
        )

        bem_estar = (
            getattr(
                request,
                "bem_estar",
                None,
            )
            or []
        )

        if request.usuario:

            context.append(
                "RESPONSÁVEL PELO ANIMAL:"
            )

            context.append(
                f"- Nome: {request.usuario}"
            )

        if animal:

            context.append(
                "\nANIMAL IDENTIFICADO "
                "NO BYTECARE:"
            )

            context.append(
                f"- ID: {animal.id}"
            )

            context.append(
                f"- Nome: {animal.nome}"
            )

            context.append(
                f"- Espécie/tipo: "
                f"{animal.tipo}"
            )

            if animal.raca:

                context.append(
                    f"- Raça: "
                    f"{animal.raca}"
                )

            if (
                animal.idade
                is not None
            ):

                context.append(
                    f"- Idade aproximada: "
                    f"{animal.idade} anos"
                )

            if animal.dataNascimento:

                context.append(
                    "- Data de nascimento: "
                    f"{animal.dataNascimento}"
                )

            if animal.subcategoria:

                context.append(
                    "- Categoria: "
                    f"{animal.subcategoria}"
                )

            if animal.observacaoGeral:

                context.append(
                    "- Observações cadastradas: "
                    f"{animal.observacaoGeral}"
                )

        if preventivos:

            context.append(
                "\nREGISTROS PREVENTIVOS "
                "DO BYTECARE:"
            )

            context.append(
                json.dumps(
                    preventivos[-10:],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        if terapeuticos:

            context.append(
                "\nREGISTROS TERAPÊUTICOS "
                "DO BYTECARE:"
            )

            context.append(
                json.dumps(
                    terapeuticos[-10:],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        if bem_estar:

            context.append(
                "\nREGISTROS DE BEM-ESTAR "
                "DO BYTECARE:"
            )

            context.append(
                json.dumps(
                    bem_estar[-10:],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        if animal:

            context.append(
                "\nREGRAS PARA USO DO "
                "CONTEXTO DO BYTECARE:\n"

                "- Os dados acima pertencem "
                "ao animal identificado na "
                "conversa.\n"

                "- Use esses dados para "
                "personalizar a orientação.\n"

                "- Não invente doenças, "
                "diagnósticos, porte, exames "
                "ou tratamentos que não "
                "estejam registrados.\n"

                "- Observações e tratamentos "
                "podem indicar condições "
                "anteriores, mas não devem "
                "ser transformados em "
                "diagnóstico atual.\n"

                "- Se o usuário disser "
                "'ele', 'ela' ou utilizar "
                "pronomes semelhantes, "
                "mantenha esse animal como "
                "referência até que outro "
                "animal seja claramente "
                "mencionado.\n"

                "- Se algum registro estiver "
                "antigo ou não possuir data "
                "clara, trate como histórico."
            )


        return "\n".join(
            context
        ).strip()

    def _build_current_message(
        self,
        request: ChatRequest,
    ) -> str:

        context = self._build_context(
            request
        )

        if not context:
            return request.mensagem

        return (
            f"{context}\n\n"
            "MENSAGEM ATUAL DO USUÁRIO:\n"
            f"{request.mensagem}"
        )

    def _apply_risk_guardrail(
        self,
        response: ChatResponse,
        request: ChatRequest,
    ) -> ChatResponse:

        risk = evaluate_chat_risk(
            request.mensagem
        )

        if (
            risk.minimum_priority
            == "urgente"
            or has_urgent_signal(
                request.mensagem
            )
        ):

            response.nivel_atencao = (
                "urgente"
            )

            response.procurar_veterinario = (
                True
            )

            return response


        if (
            risk.minimum_priority
            == "alta"
            and response.nivel_atencao
            == "normal"
        ):

            response.nivel_atencao = (
                "atencao"
            )


        return response

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        history = self._build_history(
            request
        )

        current_message = (
            self._build_current_message(
                request
            )
        )

        chat = self.client.chats.create(
            model=self.model,
            history=history,
            config=types.GenerateContentConfig(
                system_instruction=(
                    CHAT_SYSTEM_PROMPT
                ),
                temperature=0.35,
                response_mime_type=(
                    "application/json"
                ),
                response_schema=(
                    ChatResponse
                ),
            ),
        )

        gemini_response = (
            chat.send_message(
                current_message
            )
        )

        if gemini_response.parsed:

            parsed = (
                gemini_response.parsed
            )

            if isinstance(
                parsed,
                ChatResponse,
            ):

                response = parsed

            else:

                response = (
                    ChatResponse
                    .model_validate(
                        parsed
                    )
                )

        else:

            if not gemini_response.text:

                raise RuntimeError(
                    "Gemini retornou uma "
                    "resposta vazia."
                )

            response = (
                ChatResponse
                .model_validate_json(
                    gemini_response.text
                )
            )


        response = (
            self._apply_risk_guardrail(
                response,
                request,
            )
        )

        response.modo = "gemini"

        return response