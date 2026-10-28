from .risk_engine import evaluate_risk
from .schemas import AnaliseIA, AnaliseRequest, RegistrosAnalisados


def create_mock_analysis(request: AnaliseRequest) -> AnaliseIA:
    risk = evaluate_risk(request.model_dump())
    animal = request.animal

    fatores = list(risk.reasons)
    if request.preventivos:
        fatores.append(f"{len(request.preventivos)} registro(s) preventivo(s) disponível(is)")
    if request.terapeuticos:
        fatores.append(f"{len(request.terapeuticos)} acompanhamento(s) terapêutico(s) cadastrado(s)")
    if request.bem_estar:
        fatores.append(f"{len(request.bem_estar)} registro(s) de bem-estar disponível(is)")
    if not fatores:
        fatores.append("há poucos registros disponíveis; a análise é limitada ao contexto cadastrado")

    passos = [
        "Mantenha os registros do ByteCare atualizados para melhorar o acompanhamento longitudinal.",
    ]
    if request.preventivos:
        passos.append("Confira os próximos eventos preventivos cadastrados e seus prazos.")
    if request.terapeuticos:
        passos.append("Siga somente as orientações terapêuticas já prescritas pelo profissional responsável.")
    if request.bem_estar:
        passos.append("Continue registrando mudanças de alimentação, comportamento e atividade para comparação ao longo do tempo.")
    if risk.seek_vet:
        passos.append("Considere avaliação veterinária, especialmente se os sinais persistirem, piorarem ou forem intensos.")

    return AnaliseIA(
        animal_id=animal.id,
        nome_animal=animal.nome,
        prioridade=risk.minimum_priority,
        resumo=(
            f"A análise de {animal.nome} consolida os dados cadastrados nos módulos Preventivo, Terapêutico e Bem-estar. "
            "O resultado organiza o acompanhamento sem realizar diagnóstico."
        ),
        fatores_relevantes=fatores[:6],
        proximos_passos=passos[:6],
        sinais_atencao=risk.red_flags,
        procurar_veterinario=risk.seek_vet,
        aviso_seguranca=(
            "Esta análise é um apoio de organização do histórico e não substitui consulta, diagnóstico ou conduta de um médico-veterinário."
        ),
        registros_analisados=RegistrosAnalisados(
            preventivos=len(request.preventivos),
            terapeuticos=len(request.terapeuticos),
            bem_estar=len(request.bem_estar),
        ),
        modo="mock",
    )
