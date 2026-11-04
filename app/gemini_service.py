import json

from google.genai import types

from .care_engine import condicoes_registradas
from .guardrails import texto_simples
from .llm import generate, get_client

from .mock_service import build_care_plan
from .prompt import CARE_PLAN_PROMPT, SYSTEM_PROMPT
from .risk_engine import enforce_minimum_priority, evaluate_risk
from .schemas import (
    AnaliseIA,
    AnaliseRequest,
    PersonalizacaoTexto,
    PlanoCuidado,
    PlanoCuidadoRequest,
    RegistrosAnalisados,
)


class GeminiAnalysisService:
    def __init__(self) -> None:
        self.client = get_client()

    def analyze(self, request: AnaliseRequest) -> AnaliseIA:
        payload = request.model_dump()
        risk = evaluate_risk(payload)
        condicoes = condicoes_registradas(request.animal, request.bem_estar)

        user_prompt = f"""
PRIORIDADE MÍNIMA DEFINIDA PELO MOTOR DE SEGURANÇA: {risk.minimum_priority}
MOTIVOS DO MOTOR: {json.dumps(risk.reasons, ensure_ascii=False)}
RED FLAGS DETERMINÍSTICAS: {json.dumps(risk.red_flags, ensure_ascii=False)}
CONDIÇÕES REGISTRADAS NO PERFIL (cite todas no resumo e nos fatores): {json.dumps(condicoes, ensure_ascii=False)}

DADOS DO BYTECARE:
{json.dumps(payload, ensure_ascii=False, indent=2, default=str)}

Gere uma análise estruturada usando SOMENTE os dados acima.
O campo registros_analisados deve refletir exatamente as quantidades recebidas.
O aviso_seguranca deve explicar que a análise não substitui médico-veterinário.
""".strip()

        response = generate(
            self.client,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=AnaliseIA,
            ),
        )

        if response.parsed:
            result = response.parsed
            if not isinstance(result, AnaliseIA):
                result = AnaliseIA.model_validate(result)
        else:
            result = AnaliseIA.model_validate_json(response.text)

        result.prioridade = enforce_minimum_priority(result.prioridade, risk.minimum_priority)
        result.procurar_veterinario = bool(result.procurar_veterinario or risk.seek_vet)
        result.sinais_atencao = list(dict.fromkeys([*risk.red_flags, *result.sinais_atencao]))
        result.registros_analisados = RegistrosAnalisados(
            preventivos=len(request.preventivos),
            terapeuticos=len(request.terapeuticos),
            bem_estar=len(request.bem_estar),
        )
        # Condições registradas sempre aparecem, mesmo se o modelo esquecer.
        for condicao in reversed(condicoes):
            if not any(condicao.lower() in f.lower() for f in result.fatores_relevantes):
                result.fatores_relevantes.insert(0, f"Condição registrada: {condicao}")
        faltando = [c for c in condicoes if c.lower() not in result.resumo.lower()]
        if faltando:
            result.resumo = f"{result.resumo.rstrip()} Condições registradas no perfil: {'; '.join(faltando)}."
        result.resumo = texto_simples(result.resumo)
        result.animal_id = request.animal.id
        result.nome_animal = request.animal.nome
        result.modo = "gemini"
        return result


class GeminiCarePlanService:
    """
    O motor determinístico decide ações, prazos, serviços e prioridade.
    O Gemini só personaliza os textos para o tutor e para a clínica.
    """

    def __init__(self) -> None:
        self.client = get_client()

    def build(self, request: PlanoCuidadoRequest) -> PlanoCuidado:
        rascunho = build_care_plan(request)

        user_prompt = f"""
PLANO CALCULADO PELO MOTOR DE RECOMENDAÇÃO:
{rascunho.model_dump_json(indent=2, exclude={"mensagem_tutor", "resumo_clinica", "modo"})}

DADOS DO PET:
{json.dumps(request.animal.model_dump(), ensure_ascii=False, default=str)}

Escreva mensagem_tutor e resumo_clinica seguindo as regras.
""".strip()

        response = generate(
            self.client,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=CARE_PLAN_PROMPT,
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=PersonalizacaoTexto,
            ),
        )

        textos = response.parsed
        if not isinstance(textos, PersonalizacaoTexto):
            textos = PersonalizacaoTexto.model_validate_json(response.text)

        rascunho.mensagem_tutor = texto_simples(textos.mensagem_tutor)
        rascunho.resumo_clinica = texto_simples(textos.resumo_clinica)
        rascunho.modo = "gemini"
        return rascunho
