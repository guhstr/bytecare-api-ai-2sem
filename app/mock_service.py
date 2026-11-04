from .care_engine import AVISO_SEGURANCA, ResultadoMotor, condicoes_registradas, gerar_plano
from .risk_engine import PRIORITY_ORDER, evaluate_risk
from .schemas import (
    AnaliseIA,
    AnaliseRequest,
    PacientePriorizado,
    PersonalizacaoTexto,
    PlanoCuidado,
    PlanoCuidadoRequest,
    PriorizacaoClinica,
    PriorizacaoClinicaRequest,
    RegistrosAnalisados,
)


def create_mock_analysis(request: AnaliseRequest) -> AnaliseIA:
    risk = evaluate_risk(request.model_dump())
    animal = request.animal

    condicoes = condicoes_registradas(animal, request.bem_estar)
    fatores = [f"Condição registrada: {c}" for c in condicoes] + list(risk.reasons)
    if request.preventivos:
        fatores.append(f"{len(request.preventivos)} registro(s) preventivo(s) disponível(is)")
    if request.terapeuticos:
        fatores.append(f"{len(request.terapeuticos)} acompanhamento(s) terapêutico(s) cadastrado(s)")
    if request.bem_estar:
        fatores.append(f"{len(request.bem_estar)} registro(s) de bem-estar disponível(is)")
    if not fatores:
        fatores.append("há poucos registros disponíveis; a análise é limitada ao contexto cadastrado")

    passos = [
        f"Adaptar rotina e exercícios à condição registrada ({c}) e levá-la à próxima consulta."
        for c in condicoes
    ] + [
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
            + (f"Condições registradas no perfil: {'; '.join(condicoes)}. " if condicoes else "")
            + "O resultado organiza o acompanhamento sem realizar diagnóstico."
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


# ---------------------------------------------------------------------------
# Plano de Cuidado Personalizado e Priorização da Clínica
# ---------------------------------------------------------------------------

FASE_LABEL = {
    "filhote": "filhote",
    "adulto": "adulto",
    "senior": "sênior",
    "indefinida": "",
}

ACAO_CLINICA = {
    "urgente": "Contatar o tutor imediatamente e orientar atendimento de urgência.",
    "alta": "Contatar o tutor em até 48h e oferecer agendamento.",
    "moderada": "Enviar lembrete e oferecer agendamento nos próximos dias.",
    "baixa": "Manter na régua de relacionamento com lembretes automáticos.",
}


def build_care_plan(request: PlanoCuidadoRequest, textos: PersonalizacaoTexto | None = None) -> PlanoCuidado:
    """Monta o plano a partir do motor; `textos` vem do LLM quando disponível."""
    resultado = gerar_plano(request)
    if textos is None:
        textos = create_mock_texts(request, resultado)
        modo = "mock"
    else:
        modo = "gemini"

    return PlanoCuidado(
        animal_id=request.animal.id,
        nome_animal=request.animal.nome,
        perfil=resultado.perfil,
        score_risco=resultado.score_risco,
        prioridade=resultado.prioridade,
        acoes=resultado.acoes,
        servicos_recomendados=resultado.servicos,
        mensagem_tutor=textos.mensagem_tutor,
        resumo_clinica=textos.resumo_clinica,
        procurar_veterinario=resultado.procurar_veterinario,
        aviso_seguranca=AVISO_SEGURANCA,
        modo=modo,
    )


def create_mock_texts(request: PlanoCuidadoRequest, resultado: ResultadoMotor) -> PersonalizacaoTexto:
    nome = request.animal.nome
    fase = FASE_LABEL[resultado.perfil.fase_vida]
    perfil = f"{nome} ({request.animal.tipo.lower()}{' ' + fase if fase else ''})"
    principais = resultado.acoes[:3]

    if resultado.prioridade == "urgente":
        abertura = (
            f"Atenção: o histórico recente de {nome} tem sinais que merecem "
            "atendimento veterinário o quanto antes."
        )
    elif principais:
        abertura = f"Preparamos o plano de cuidado de {perfil}."
    else:
        abertura = f"O cuidado de {perfil} está em dia. Continue registrando a rotina."

    itens = " ".join(
        f"{i}. {a.titulo} ({'hoje' if a.prazo_dias == 0 else f'em até {a.prazo_dias} dias'})."
        for i, a in enumerate(principais, start=1)
    )

    servicos = ", ".join(s.nome for s in resultado.servicos[:3]) or "nenhum serviço no momento"
    pendentes = ", ".join(resultado.perfil.vacinas_pendentes) or "nenhuma"

    return PersonalizacaoTexto(
        mensagem_tutor=f"{abertura} {itens}".strip(),
        resumo_clinica=(
            f"Paciente {perfil}. Prioridade {resultado.prioridade} "
            f"(score {resultado.score_risco}/100). Vacinas essenciais pendentes: "
            f"{pendentes}. Serviços sugeridos: {servicos}. "
            f"Registros: {len(request.preventivos)} preventivo(s), "
            f"{len(request.terapeuticos)} terapêutico(s), "
            f"{len(request.consultas)} consulta(s), "
            f"{len(request.bem_estar) + len(request.comportamento)} de bem-estar/comportamento."
        ),
    )


def prioritize_patients(request: PriorizacaoClinicaRequest) -> PriorizacaoClinica:
    """Fila de prioridade da clínica: quem precisa de contato primeiro."""
    avaliados = []
    for paciente in request.pacientes:
        if request.data_referencia and not paciente.data_referencia:
            paciente = paciente.model_copy(update={"data_referencia": request.data_referencia})
        avaliados.append((paciente, gerar_plano(paciente)))

    avaliados.sort(
        key=lambda item: (
            -PRIORITY_ORDER[item[1].prioridade],
            -item[1].score_risco,
        )
    )

    pacientes = []
    distribuicao = {p: 0 for p in PRIORITY_ORDER}
    for posicao, (paciente, resultado) in enumerate(avaliados, start=1):
        distribuicao[resultado.prioridade] += 1
        principal = resultado.acoes[0] if resultado.acoes else None
        pacientes.append(
            PacientePriorizado(
                posicao=posicao,
                animal_id=paciente.animal.id,
                nome_animal=paciente.animal.nome,
                especie=resultado.perfil.especie,
                score_risco=resultado.score_risco,
                prioridade=resultado.prioridade,
                motivo_principal=(
                    f"{principal.titulo}: {principal.motivo}" if principal else "Cuidado em dia."
                ),
                acao_principal=principal.titulo if principal else None,
                motivo=principal.motivo if principal else None,
                acao_sugerida_clinica=ACAO_CLINICA[resultado.prioridade],
                servicos_recomendados=[s.nome for s in resultado.servicos[:3]],
            )
        )

    return PriorizacaoClinica(
        total_pacientes=len(pacientes),
        distribuicao=distribuicao,
        pacientes=pacientes,
        aviso_seguranca=(
            "A priorização apoia a organização da agenda da clínica e não "
            "substitui a triagem feita por um profissional."
        ),
    )
