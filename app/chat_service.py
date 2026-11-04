import json
import re
from datetime import date

from google.genai import types

from .llm import generate, get_client

from .cadastro import (
    EstadoCadastro,
    especie_do_texto,
    estado_cadastro,
    idade_meses_do_texto,
    pergunta_faltando,
    quer_cadastrar_animal,
    resumo_cadastro,
)
from .agendamento import (
    EstadoAgendamento,
    descrever_quando,
    estado_agendamento,
    pergunta_quando,
    juntar,
)
from .observacao import PRONOMES, observacao_da_mensagem, pede_registro_observacao
from .remocao import pede_lista_pets, pedido_remocao
from .care_engine import (
    VACINAS_ESSENCIAIS,
    calendario_vacinas,
    especie_detalhada,
    descrever_idade,
    especie_grupo,
    fase_vida,
    gerar_plano,
    idade_em_anos,
)
from .guardrails import MENSAGEM_FORA_DO_ESCOPO, MENSAGEM_SEM_DOSE, contem_dose, texto_simples
from .prompt import CHAT_SYSTEM_PROMPT
from .risk_engine import (
    _normalize,
    contains_term,
    evaluate_chat_risk,
    has_urgent_signal,
)
from .schemas import (
    ChatRequest,
    PlanoCuidadoRequest,
    ChatResponse,
)

# ---------------------------------------------------------------------------
# Modo mock do Assistente ByteCare
#
# Conversa de triagem com memória: lê todas as mensagens do usuário
# (histórico + mensagem atual), identifica o que já foi informado e
# pergunta apenas o que ainda falta. Com informação suficiente, devolve
# um resumo e a orientação.
# ---------------------------------------------------------------------------

TRIAGEM = [
    (
        "inicio",
        ["desde", "ha ", "faz ", "ontem", "hoje", "dias", "dia ", "horas", "semana", "comecou", "manha", "noite"],
        "Isso começou há quanto tempo?",
    ),
    (
        "alimentacao",
        ["come", "comer", "comendo", "comida", "racao", "apetite", "fome"],
        "Ele está comendo normalmente?",
    ),
    (
        "agua",
        ["agua", "bebe", "beber", "bebendo", "hidrat"],
        "E está bebendo água?",
    ),
    (
        "digestivo",
        ["vomit", "diarre", "fezes", "coco", "intestino"],
        "Teve vômito ou diarreia?",
    ),
    (
        "disposicao",
        ["desanim", "apati", "parado", "quieto", "cansad", "brincando", "ativo", "disposto", "energia", "deitado", "prostrad"],
        "Como está a disposição dele: está brincando ou mais quieto e deitado?",
    ),
]

TERMOS_QUEIXA = [
    "doente", "mal", "estranho", "dor", "vomit", "diarre", "espirr",
    "febre", "manc", "ferid", "coceira", "cocando", "desanim", "apati", "toss",
    "nao come", "nao quer comer", "sem comer", "fraco", "tremendo", "tremor",
    "sangr", "inchad", "machuc", "triste", "nao bebe", "parado",
]

# Sinais relatados que indicam avaliação veterinária em até 24h.
SINAIS_PIORA = {
    "nao come": "não está comendo",
    "nao quer comer": "não está comendo",
    "sem comer": "não está comendo",
    "nao bebe": "não está bebendo água",
    "nao quer beber": "não está bebendo água",
    "vomit": "vômito",
    "diarre": "diarreia",
    "sangr": "sangramento",
    "apati": "apatia",
    "prostrad": "prostração",
    "fraco": "fraqueza",
    "nao levanta": "dificuldade para levantar",
}

# Sinais leves: entram no resumo, mas sozinhos pedem observação.
SINAIS_LEVES = {
    "quieto": "mais quieto que o normal",
    "desanim": "desânimo",
    "deitado": "mais tempo deitado",
    "toss": "tosse",
    "espirr": "espirros",
    "cocando": "coceira",
    "coceira": "coceira",
    "manc": "mancando",
}

ENCERRAMENTOS = ["obrigad", "valeu", "ok", "entendi", "beleza", "certo"]


def _texto_usuario(request: ChatRequest) -> list[str]:
    mensagens = [
        _normalize(m.content)
        for m in request.historico
        if m.role == "user"
    ]
    atual = _normalize(request.mensagem)
    if not mensagens or mensagens[-1] != atual:
        mensagens.append(atual)
    return mensagens


def _afirmado(texto: str, termo: str) -> bool:
    """Ignora o termo quando vem logo depois de 'não' (ex.: 'não vomitou')."""
    for match in re.finditer(rf"\b{re.escape(termo)}", texto):
        antes = texto[max(0, match.start() - 12):match.start()]
        if termo.startswith("nao ") or not re.search(r"\b(nao|sem)\b", antes):
            return True
    return False


def _sinais(conversa: str, tabela: dict[str, str]) -> list[str]:
    return list(dict.fromkeys(
        rotulo for termo, rotulo in tabela.items()
        if _afirmado(conversa, termo)
    ))


def _tem(texto: str, termos: list[str]) -> bool:
    """Termos curtos (até 3 letras) só valem como palavra inteira."""
    for termo in termos:
        termo = termo.strip()
        if len(termo) <= 3:
            if re.search(rf"\b{re.escape(termo)}\b", texto):
                return True
        elif contains_term(texto, termo):
            return True
    return False


def _resumo_plano(request: ChatRequest) -> str:
    """Resultado do motor de recomendação, para o chat e a análise concordarem."""
    plano = gerar_plano(
        PlanoCuidadoRequest(
            animal=request.animal,
            preventivos=request.preventivos,
            terapeuticos=request.terapeuticos,
            bem_estar=request.bem_estar,
        )
    )
    perfil = plano.perfil
    linhas = [
        "\nPLANO DE CUIDADO CALCULADO PELO BYTECARE (use como referência):",
        f"- Fase de vida: {perfil.fase_vida}",
        f"- Vacinas essenciais da espécie: {', '.join(perfil.vacinas_essenciais) or 'definidas pelo veterinário'}",
        f"- Vacinas registradas: {', '.join(perfil.vacinas_registradas) or 'nenhuma'}",
        f"- Vacinas sem registro: {', '.join(perfil.vacinas_pendentes) or 'nenhuma'}",
        f"- Prioridade atual: {plano.prioridade}",
        "- Ações prioritárias:",
        *[f"  * {a.titulo} (prazo: {a.prazo_dias} dias) - {a.motivo}" for a in plano.acoes[:4]],
    ]
    return "\n".join(linhas)


DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]

NOME_ESPECIE = {
    "cao": "cão", "gato": "gato", "equino": "equino", "bovino": "bovino",
    "ave": "ave", "peixe": "peixe", "coelho": "coelho",
}


def _perfil_vacinal(request: ChatRequest, estado: EstadoCadastro):
    """Nome, grupo, idade e espécie exata: do pet aberto ou do cadastro em andamento."""
    conversa = list(reversed(_texto_usuario(request)))
    if request.animal:
        animal = request.animal
        grupo = especie_grupo(animal.tipo)
        especie = None
        # Espécie exata só para aves (o tipo PASSARO reúne papagaio, canário etc.).
        if grupo in ("ave", "outro"):
            especie = especie_detalhada(
                animal.subcategoria, animal.raca, animal.tipo, animal.observacaoGeral, *conversa
            )
            if especie:
                grupo = "ave"
        return animal.nome, grupo, idade_em_anos(animal, date.today()), especie
    especie, meses = estado.especie, estado.idade_meses
    if not especie:
        # Sem cadastro: usa o que o tutor contou na conversa ("meu gato de 2 anos").
        for texto in reversed(_texto_usuario(request)):
            especie = especie or especie_do_texto(texto)
            meses = meses if meses is not None else idade_meses_do_texto(texto)
    if especie:
        idade = meses / 12 if meses is not None else None
        grupo = especie_grupo(especie)
        detalhe = especie_detalhada(estado.raca, especie, *conversa) if grupo == "ave" else None
        return estado.nome or "seu pet", grupo, idade, detalhe
    return None


def _referencia_vacinas(request: ChatRequest, estado: EstadoCadastro) -> str:
    """Calendário de referência enviado ao Gemini junto com a mensagem."""
    perfil = _perfil_vacinal(request, estado)
    if not perfil:
        return ""
    nome, grupo, idade, especie = perfil
    vacinas, opcionais, observacao = calendario_vacinas(grupo, idade, especie)
    rotulo = especie or NOME_ESPECIE.get(grupo, grupo)
    if not vacinas:
        if not observacao:
            return ""
        return (
            f"\nVACINAS PARA {nome.upper()} ({rotulo}, {descrever_idade(idade)}):\n"
            f"- {observacao}\n"
            f"- Use esta orientação: a espécie já é conhecida ({rotulo}); não diga que depende da espécie."
        )
    linhas = [
        f"\nCALENDÁRIO DE VACINAS DE REFERÊNCIA PARA {nome.upper()} "
        f"({rotulo}, {descrever_idade(idade)}, fase {fase_vida(grupo, idade)}):",
        *[f"- {v}" for v in vacinas],
    ]
    if opcionais:
        linhas.append(f"- Opcionais, a critério do veterinário: {opcionais}")
    if observacao:
        linhas.append(f"- Observação: {observacao}")
    return "\n".join(linhas)


def _resposta_vacinas(request: ChatRequest, estado: EstadoCadastro) -> str:
    perfil = _perfil_vacinal(request, estado)
    if not perfil:
        return (
            "Para indicar as vacinas recomendadas, me diga a espécie e a idade "
            "do seu pet."
        )

    nome, grupo, idade, especie = perfil
    vacinas, opcionais, observacao = calendario_vacinas(grupo, idade, especie)
    descricao = f"{especie or NOME_ESPECIE.get(grupo, grupo)}, {descrever_idade(idade)}"
    if not vacinas:
        if observacao:
            return (
                f"Sobre {nome} ({descricao}): {observacao}\n"
                "Se quiser, posso pedir um check-up na clínica."
            )
        return (
            f"Para {nome}, o protocolo de vacinas é definido pelo veterinário na "
            "consulta. Posso te lembrar de agendar uma avaliação."
        )

    linhas = [f"Vacinas recomendadas para {nome} ({descricao}):"]
    linhas += [f"- {v}" for v in vacinas]
    if opcionais:
        linhas.append(f"- Opcionais, a critério do veterinário: {opcionais}.")
    if observacao:
        linhas.append(observacao)

    # Compara com o histórico quando o pet já está no ByteCare.
    essenciais = VACINAS_ESSENCIAIS.get(grupo, {})
    if request.animal and essenciais:
        textos = [
            " ".join(_normalize(str(v)) for v in p.values() if v)
            for p in request.preventivos
        ]
        registradas = [
            vacina for vacina, termos in essenciais.items()
            if any(_tem(t, termos) for t in textos)
        ]
        pendentes = [v for v in essenciais if v not in registradas]
        if registradas:
            linhas.append(f"No ByteCare já constam: {', '.join(registradas)}.")
        if pendentes:
            linhas.append(
                f"Sem registro no ByteCare: {', '.join(pendentes)}. Vale confirmar "
                "com a clínica e registrar a aplicação."
            )

    linhas.append("O calendário final é definido pelo médico-veterinário.")
    return "\n".join(linhas)


PERGUNTA_VACINA = re.compile(r"\b(qua(l|is)|recomend\w*|precis\w*|devo|tem que|falt\w*|indic\w*)\b")


def _pergunta_sobre_vacinas(texto: str) -> bool:
    texto = _normalize(texto)
    return bool(re.search(r"\bvacin\w*", texto) and PERGUNTA_VACINA.search(texto))


def _observacao_agendamento(request: ChatRequest, agenda: EstadoAgendamento) -> str | None:
    """Informa à clínica quais vacinas avaliar quando o pedido inclui vacinação."""
    if "Vacinação" not in agenda.servicos or request.animal is None:
        return None
    essenciais = VACINAS_ESSENCIAIS.get(especie_grupo(request.animal.tipo), {})
    if not essenciais:
        return None
    textos = [" ".join(_normalize(str(v)) for v in p.values() if v) for p in request.preventivos]
    pendentes = [
        vacina for vacina, termos in essenciais.items()
        if not any(_tem(t, termos) for t in textos)
    ]
    return f"Vacinas a avaliar: {', '.join(pendentes or essenciais)}."


def _sem_promessa_de_envio(texto: str, agenda: EstadoAgendamento) -> str:
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    mantidas = [f for f in frases if not re.search(r"confirm|solicitar|enviar|entrar em contato", _normalize(f))]
    pergunta = pergunta_quando(agenda)
    corpo = " ".join(mantidas).strip()
    if "?" in corpo and ("horario" in _normalize(corpo) or "dia" in _normalize(corpo)):
        return corpo
    if corpo and agenda.falta == "horario":
        pergunta = pergunta.split(". ", 1)[-1]
    return f"{corpo} {pergunta}".strip() if corpo else pergunta


def _resposta_agendamento(request: ChatRequest, agenda: EstadoAgendamento, vacinas: str | None) -> ChatResponse:
    partes = [vacinas] if vacinas else []
    if request.animal is None:
        partes.append(
            "Para agendar, preciso saber de qual pet. Abra o assistente pela tela "
            "do pet ou cadastre o animal aqui primeiro."
        )
        return ChatResponse(resposta="\n\n".join(partes), modo="mock")

    nome = request.animal.nome
    servicos = juntar(agenda.servicos)
    if not agenda.pronto:
        abertura = f"Posso pedir à clínica {servicos} para {nome}. " if agenda.falta == "dia" else ""
        partes.append(abertura + pergunta_quando(agenda))
        return ChatResponse(resposta="\n\n".join(partes), modo="mock")

    partes.append(
        f"Vou pedir à clínica: {servicos} para {nome}, {descrever_quando(agenda)}. "
        "Confirme na janela para enviar. A clínica confirma o horário e você "
        "recebe o aviso em Notificações."
    )
    return ChatResponse(
        resposta="\n\n".join(partes),
        acao="agendar",
        agendamento=agenda.para_pedido(_observacao_agendamento(request, agenda)),
        modo="mock",
    )


PERGUNTA_OBSERVACAO = "O que você quer registrar no histórico"


def _pedido_de_observacao(request: ChatRequest) -> bool:
    """Pedido na mensagem atual ou resposta à pergunta 'o que você quer registrar'."""
    if pede_registro_observacao(request.mensagem) and not quer_cadastrar_animal(request.mensagem):
        return True
    ultima = next((m.content for m in reversed(request.historico) if m.role == "assistant"), "")
    return PERGUNTA_OBSERVACAO in ultima


def _observacao(request: ChatRequest):
    observacao = observacao_da_mensagem(request)
    ultima = next((m.content for m in reversed(request.historico) if m.role == "assistant"), "")
    if observacao is None and PERGUNTA_OBSERVACAO in ultima:
        # Resposta direta à pergunta: a mensagem inteira é o conteúdo.
        observacao = observacao_da_mensagem(
            request.model_copy(update={"mensagem": f"registra que {request.mensagem}"})
        )
    return observacao


def _resposta_observacao(request: ChatRequest) -> ChatResponse:
    if request.animal is None:
        return ChatResponse(
            resposta=(
                "Para registrar no histórico, preciso saber de qual pet. Me diga o "
                "nome dele ou cadastre o animal aqui primeiro."
            ),
            modo="mock",
        )
    nome = request.animal.nome
    observacao = _observacao(request)
    if observacao is None:
        return ChatResponse(resposta=f"Claro. {PERGUNTA_OBSERVACAO} de {nome}?", modo="mock")
    complemento = (
        " Como é uma condição permanente, ela também fica nas observações do cadastro."
        if observacao.permanente else ""
    )
    return ChatResponse(
        resposta=(
            f"Entendi. Vou registrar no histórico de {nome}: \"{observacao.descricao}\"."
            f"{complemento} Confirme na janela para salvar."
        ),
        acao="registrar_observacao",
        observacao_cadastro=observacao,
        modo="mock",
    )


def _resposta_remocao(request: ChatRequest) -> ChatResponse:
    if request.animal is None:
        return ChatResponse(
            resposta=(
                "Qual pet você quer apagar? Me diga o nome dele, por exemplo: "
                "\"apaga o Draco\"."
            ),
            modo="mock",
        )
    nome = request.animal.nome
    return ChatResponse(
        resposta=(
            f"Entendi. Vou apagar {nome} do ByteCare, junto com o histórico e os "
            "agendamentos dele. Essa ação não pode ser desfeita. Confirme na janela para continuar."
        ),
        acao="apagar_animal",
        modo="mock",
    )


def _extras_cadastro(estado: EstadoCadastro) -> str:
    """Resumo do que será registrado no histórico depois do cadastro."""
    itens = []
    for vacina in estado.vacinas:
        proxima = (
            f", próxima dose em {date.fromisoformat(vacina.proximo_previsto).strftime('%d/%m/%Y')}"
            if vacina.proximo_previsto else ""
        )
        itens.append(f"vacina {vacina.nome_vacina}{proxima}")
    if estado.observacao:
        itens.append(f"a observação \"{estado.observacao.descricao}\"")
    if not itens:
        return ""
    lista = itens[0] if len(itens) == 1 else f"{', '.join(itens[:-1])} e {itens[-1]}"
    return f" Também anotei {lista}: registro no histórico logo depois do cadastro."


def _resposta_cadastro(estado: EstadoCadastro, primeira: bool) -> ChatResponse:
    extras = _extras_cadastro(estado)
    if estado.pronto:
        return ChatResponse(
            resposta=(
                f"Perfeito! Confira os dados: {resumo_cadastro(estado)}.{extras} "
                "Toque em Cadastrar na confirmação para salvar no ByteCare."
            ),
            acao="cadastrar_animal",
            animal_cadastro=estado.para_cadastro(),
            vacinas_cadastro=estado.vacinas,
            observacao_cadastro=estado.observacao,
            modo="mock",
        )
    abertura = "Claro, vamos cadastrar! " if primeira else ""
    return ChatResponse(resposta=abertura + pergunta_faltando(estado) + extras, modo="mock")


def _resposta_historico(request: ChatRequest, nome: str) -> str:
    return (
        f"No ByteCare, {nome} tem {len(request.preventivos)} registro(s) "
        f"preventivo(s), {len(request.terapeuticos)} tratamento(s) e "
        f"{len(request.bem_estar)} registro(s) de bem-estar. Para ver as ações "
        "priorizadas, abra a Análise IA do pet."
    )


def create_mock_chat_response(
    request: ChatRequest,
) -> ChatResponse:

    animal = request.animal
    nome = animal.nome if animal else "seu pet"

    mensagens = _texto_usuario(request)
    conversa = " ".join(mensagens)
    atual = mensagens[-1]

    # Urgência: avaliada na mensagem atual e no restante da conversa.
    risco = evaluate_chat_risk(conversa)
    if risco.minimum_priority == "urgente":
        return ChatResponse(
            resposta=(
                f"Pelo que você descreveu, {nome} pode estar em uma situação "
                f"de urgência ({', '.join(risco.red_flags)}). Mantenha o animal "
                "em segurança e procure atendimento veterinário agora. "
                "Não ofereça medicamentos por conta própria."
            ),
            nivel_atencao="urgente",
            procurar_veterinario=True,
            modo="mock",
        )

    ultima_resposta = next(
        (m.content for m in reversed(request.historico) if m.role == "assistant"),
        "",
    )
    if _tem(atual, ENCERRAMENTOS) and len(atual.split()) <= 4:
        return ChatResponse(
            resposta=(
                f"Por nada! Estou por aqui se precisar. Desejo melhoras para {nome}."
                if "Entendi o quadro" in ultima_resposta
                else f"Por nada! Se notar qualquer mudança em {nome}, é só me chamar."
            ),
            modo="mock",
        )

    # Lista dos pets do usuário: quem monta a lista é o app, com a API principal.
    if pede_lista_pets(atual):
        return ChatResponse(resposta="Claro! Vou buscar os pets cadastrados no seu nome.", acao="listar_animais", modo="mock")

    # Pedido para apagar o pet aberto (o app confirma e a API checa o dono).
    if pedido_remocao(request):
        return _resposta_remocao(request)

    # Registro de condição ou observação no histórico do pet.
    if _pedido_de_observacao(request):
        return _resposta_observacao(request)

    estado = estado_cadastro(request)

    # Pedido de agendamento (pode vir junto com uma pergunta sobre vacinas).
    agenda = estado_agendamento(request)
    if agenda.ativo and not estado.ativo:
        vacinas = _resposta_vacinas(request, estado) if _pergunta_sobre_vacinas(atual) else None
        return _resposta_agendamento(request, agenda, vacinas)

    pergunta_vacina = _tem(atual, ["vacin", "imuniz", "reforco"]) and not _tem(atual, TERMOS_QUEIXA)
    # No meio de um cadastro, "tem uma vacina V10" é informação, não pergunta.
    if estado.ativo and not (_pergunta_sobre_vacinas(atual) or "?" in atual):
        pergunta_vacina = False

    # Perguntas sobre vacinas usam o pet aberto ou o cadastro em andamento.
    if pergunta_vacina:
        resposta = _resposta_vacinas(request, estado)
        if estado.ativo and estado.pronto:
            return ChatResponse(
                resposta=f"{resposta}\nQuando quiser, confirme o cadastro de {estado.nome}.",
                acao="cadastrar_animal",
                animal_cadastro=estado.para_cadastro(),
                modo="mock",
            )
        if estado.ativo:
            resposta = f"{resposta}\n{pergunta_faltando(estado)}"
        return ChatResponse(resposta=resposta, modo="mock")

    # Cadastro de novo animal: pergunta o que falta e depois pede a confirmação.
    if estado.ativo:
        return _resposta_cadastro(estado, primeira=quer_cadastrar_animal(atual))

    em_triagem = _tem(conversa, TERMOS_QUEIXA) or risco.minimum_priority == "alta"

    if not _tem(atual, TERMOS_QUEIXA) and _tem(atual, ["historico", "registro", "resumo"]):
        return ChatResponse(resposta=_resposta_historico(request, nome), modo="mock")

    if not em_triagem:
        return ChatResponse(
            resposta=(
                "Posso ajudar com sintomas, vacinas, alimentação, comportamento "
                f"ou o histórico de {nome}. O que você observou?"
            ),
            modo="mock",
        )

    respondidas = [slot for slot, termos, _ in TRIAGEM if _tem(conversa, termos)]
    faltando = [pergunta for slot, termos, pergunta in TRIAGEM if slot not in respondidas]
    perguntas_feitas = sum(1 for m in request.historico if m.role == "assistant" and "?" in m.content)

    # Ainda falta informação importante: pergunta só o que falta (até 2 por vez).
    if faltando and len(respondidas) < 4 and perguntas_feitas < 3:
        if len(mensagens) == 1:
            abertura = f"Sinto muito que {nome} não esteja bem. Vou te ajudar a entender melhor."
        else:
            abertura = "Obrigado, isso ajuda."
        return ChatResponse(
            resposta=f"{abertura} {' '.join(faltando[:2])}",
            nivel_atencao="atencao",
            procurar_veterinario=False,
            modo="mock",
        )

    # Informação suficiente: resumo e orientação.
    piora = _sinais(conversa, SINAIS_PIORA)
    leves = _sinais(conversa, SINAIS_LEVES)
    relatados = piora + leves
    resumo = (
        f"Entendi o quadro de {nome}: {', '.join(relatados)}."
        if relatados
        else f"Entendi o quadro de {nome}."
    )

    if piora:
        orientacao = (
            f"Com esses sinais, o recomendado é levar {nome} para avaliação "
            "veterinária nas próximas 24 horas. Se piorar antes disso, procure "
            "atendimento imediato."
        )
    else:
        orientacao = (
            f"Observe {nome} nas próximas 24 a 48 horas, mantenha água fresca "
            "à disposição e registre qualquer mudança no ByteCare. Se os sinais "
            "persistirem ou piorarem, agende uma consulta."
        )

    return ChatResponse(
        resposta=(
            f"{resumo} {orientacao} "
            "Não ofereça medicamentos sem orientação do veterinário."
        ),
        nivel_atencao="atencao",
        procurar_veterinario=bool(piora),
        modo="mock",
    )


class GeminiChatService:

    def __init__(self) -> None:
        self.client = get_client()

    def _build_history(
        self,
        request: ChatRequest,
    ) -> list[types.Content]:

        history: list[
            types.Content
        ] = []

        historico = list(request.historico)

        # O app pode enviar a mensagem atual também no histórico.
        if (
            historico
            and historico[-1].role == "user"
            and historico[-1].content.strip()
            == request.mensagem.strip()
        ):
            historico = historico[:-1]

        recent_history = historico[-16:]

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

        while history and history[0].role == "model":
            history.pop(0)

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
            context.append(_resumo_plano(request))

        estado = estado_cadastro(request)
        if estado.ativo:
            context.append(
                "\nCADASTRO DE NOVO ANIMAL EM ANDAMENTO:\n"
                f"- Nome: {estado.nome or 'não informado'}\n"
                f"- Espécie: {estado.especie or 'não informada'}\n"
                f"- Raça: {estado.raca or 'não informada'}\n"
                f"- Idade em meses: {estado.idade_meses if estado.idade_meses is not None else 'não informada'}\n"
                f"- Faltando: {', '.join(estado.faltando) or 'nada'}\n"
                f"- Vacinas já tomadas (vão para o histórico depois do cadastro): "
                f"{', '.join(v.nome_vacina + (' (próxima ' + v.proximo_previsto + ')' if v.proximo_previsto else '') for v in estado.vacinas) or 'nenhuma'}\n"
                f"- Observação de saúde (vai para o histórico): {estado.observacao.descricao if estado.observacao else 'nenhuma'}\n"
                "- Não pergunte de novo o que já foi informado; pergunte só o que estiver faltando."
            )

        context.insert(0, f"DATA DE HOJE: {date.today().isoformat()} ({DIAS[date.today().weekday()]})")

        agenda = estado_agendamento(request)
        if agenda.ativo:
            context.append(
                "\nPEDIDO DE AGENDAMENTO EM ANDAMENTO:\n"
                f"- Serviços: {', '.join(agenda.servicos)}\n"
                f"- Data preferida: {agenda.data.isoformat() if agenda.data else ('qualquer dia' if agenda.dia_flexivel else 'não informada')}\n"
                f"- Horário: {agenda.hora or ('qualquer horário' if agenda.hora_flexivel else 'não informado')}\n"
                f"- Período: {agenda.periodo or 'não informado'}\n"
                f"- Pronto para enviar: {'sim' if agenda.pronto else 'não, falta perguntar o ' + ('dia e o horário' if agenda.falta == 'dia' else 'horário')}"
            )

        if animal and pedido_remocao(request):
            context.append(
                "\nPEDIDO PARA APAGAR O PET IDENTIFICADO:\n"
                f"- Pet: {animal.nome}\n"
                "- Retorne acao = \"apagar_animal\"."
            )

        observacao = _observacao(request)
        if observacao and animal:
            context.append(
                "\nPEDIDO DE REGISTRO NO HISTÓRICO IDENTIFICADO:\n"
                f"- Título sugerido: {observacao.titulo}\n"
                f"- Descrição: {observacao.descricao}\n"
                f"- Categoria: {observacao.categoria}\n"
                f"- Permanente: {'sim' if observacao.permanente else 'não'}"
            )

        referencia = _referencia_vacinas(request, estado)
        if referencia:
            context.append(referencia)


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

        # Mensagens anteriores + mensagem atual com o contexto do pet.
        contents = [
            *history,
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=current_message)],
            ),
        ]

        gemini_response = generate(
            self.client,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=CHAT_SYSTEM_PROMPT,
                temperature=0.35,
                response_mime_type="application/json",
                response_schema=ChatResponse,
            ),
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

def apply_output_guardrails(response: ChatResponse, request: ChatRequest) -> ChatResponse:
    """Últimas verificações antes de a resposta chegar ao app (os dois modos)."""
    response.resposta = texto_simples(response.resposta)
    if response.fora_do_escopo:
        response.resposta = MENSAGEM_FORA_DO_ESCOPO
        response.nivel_atencao = "normal"
        response.procurar_veterinario = False
        response.acao = "nenhuma"
        response.animal_cadastro = None
        response.vacina_cadastro = None
        response.observacao_cadastro = None
        response.agendamento = None
        return response

    if contem_dose(response.resposta):
        response.resposta = MENSAGEM_SEM_DOSE

    # Cadastro de animal: completa com o que foi lido da conversa e exige os
    # quatro dados obrigatórios. Se o modelo esqueceu a ação, ela é sugerida.
    estado = estado_cadastro(request)
    cadastro = response.animal_cadastro
    if response.acao == "cadastrar_animal" and cadastro is not None:
        if cadastro.idade_meses is None:
            cadastro.idade_meses = estado.idade_meses if estado.idade_meses is not None else cadastro.idade * 12
        cadastro.raca = cadastro.raca or estado.raca
        if not (cadastro.nome and cadastro.raca):
            cadastro = None
    if response.acao == "cadastrar_animal" and cadastro is None and estado.pronto:
        cadastro = estado.para_cadastro()
    if response.acao == "nenhuma" and estado.pronto:
        response.acao = "cadastrar_animal"
        cadastro = estado.para_cadastro()
    response.animal_cadastro = cadastro if response.acao == "cadastrar_animal" else None
    # Extras do cadastro vêm da conversa (regras), não do modelo.
    extras_observacao = None
    if response.acao == "cadastrar_animal":
        response.vacinas_cadastro = estado.vacinas or response.vacinas_cadastro
        extras_observacao = estado.observacao or response.observacao_cadastro
    else:
        response.vacinas_cadastro = []
    if response.acao == "cadastrar_animal" and cadastro is None:
        response.acao = "nenhuma"
    if response.acao == "cadastrar_vacina" and (response.vacina_cadastro is None or request.animal is None):
        response.acao = "nenhuma"
        response.vacina_cadastro = None

    # Registro no histórico: exige um pet aberto; completa o que o modelo esqueceu.
    observacao = _observacao(request)
    if request.animal and observacao and response.acao == "nenhuma":
        response.acao = "registrar_observacao"
    if response.acao == "registrar_observacao":
        response.observacao_cadastro = response.observacao_cadastro or observacao
        if response.observacao_cadastro:
            descricao = PRONOMES.sub("", response.observacao_cadastro.descricao.strip())
            if descricao:
                response.observacao_cadastro.descricao = descricao[0].upper() + descricao[1:]
        if request.animal is None or response.observacao_cadastro is None:
            response.acao = "nenhuma"
    if response.acao != "registrar_observacao":
        response.observacao_cadastro = extras_observacao if response.acao == "cadastrar_animal" else None

    # Agendamento: só sai com pet, serviço, dia e horário informados pelo tutor
    # (ou "qualquer dia"). Dia e horário vêm da conversa, nunca do modelo.
    agenda = estado_agendamento(request)
    if request.animal and agenda.pronto and response.acao == "nenhuma":
        response.acao = "agendar"
    if agenda.ativo and request.animal and not agenda.pronto:
        # Falta dia ou horário: o texto não pode prometer confirmação e precisa perguntar.
        response.resposta = _sem_promessa_de_envio(response.resposta, agenda)
    if response.acao == "agendar":
        if request.animal is None or not agenda.pronto:
            response.acao = "nenhuma"
        else:
            pedido = agenda.para_pedido(
                _observacao_agendamento(request, agenda)
                or (response.agendamento.observacao if response.agendamento else None)
            )
            if response.agendamento and response.agendamento.servicos:
                pedido.servicos = list(dict.fromkeys(agenda.servicos + response.agendamento.servicos))
            response.agendamento = pedido
    if response.acao != "agendar":
        response.agendamento = None

    # Apagar o pet: só com pet aberto e pedido explícito na mensagem atual.
    # O modelo nunca dispara essa ação sozinho.
    remocao = request.animal is not None and pedido_remocao(request)
    if remocao and response.acao in ("nenhuma", "apagar_animal"):
        response.acao = "apagar_animal"
        if not re.search(r"\bconfirm", response.resposta, re.I):
            response.resposta = (
                f"{response.resposta} Essa ação não pode ser desfeita. Confirme na janela para continuar."
            ).strip()
    elif response.acao == "apagar_animal":
        response.acao = "nenhuma"

    # Listar os pets: só leitura, o app busca na API principal.
    if pede_lista_pets(request.mensagem) and response.acao == "nenhuma":
        response.acao = "listar_animais"

    # Piso de urgência determinístico.
    if has_urgent_signal(request.mensagem):
        response.nivel_atencao = "urgente"
        response.procurar_veterinario = True

    return response
