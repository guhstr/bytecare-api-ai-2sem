import json
import os
from google import genai
from google.genai import types

from .prompt import SYSTEM_PROMPT
from .risk_engine import enforce_minimum_priority, evaluate_risk
from .schemas import AnaliseIA, AnaliseRequest, RegistrosAnalisados


class GeminiAnalysisService:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def analyze(self, request: AnaliseRequest) -> AnaliseIA:
        payload = request.model_dump()
        risk = evaluate_risk(payload)

        user_prompt = f"""
PRIORIDADE MÍNIMA DEFINIDA PELO MOTOR DE SEGURANÇA: {risk.minimum_priority}
MOTIVOS DO MOTOR: {json.dumps(risk.reasons, ensure_ascii=False)}
RED FLAGS DETERMINÍSTICAS: {json.dumps(risk.red_flags, ensure_ascii=False)}

DADOS DO BYTECARE:
{json.dumps(payload, ensure_ascii=False, indent=2, default=str)}

Gere uma análise estruturada usando SOMENTE os dados acima.
O campo registros_analisados deve refletir exatamente as quantidades recebidas.
O aviso_seguranca deve explicar que a análise não substitui médico-veterinário.
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
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
        result.animal_id = request.animal.id
        result.nome_animal = request.animal.nome
        result.modo = "gemini"
        return result
