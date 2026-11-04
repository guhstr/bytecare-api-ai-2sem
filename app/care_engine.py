"""
Motor de Recomendação de Cuidado Contínuo (ByteCare / CLYVO VET).

Transforma o histórico do pet (perfil, vacinas, preventivos, tratamentos,
consultas, bem-estar e comportamento) em:

- um plano de ações priorizadas, com prazo e justificativa;
- uma lista de serviços da clínica recomendados;
- um score de risco (0-100) usado para priorizar pacientes na clínica.

As decisões são determinísticas e explicáveis: cada ação informa o motivo e
os dados de origem. O LLM (Gemini) apenas reescreve os textos para o tutor e
para a clínica; ele nunca altera prioridades, ações ou serviços.
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .risk_engine import PRIORITY_ORDER, _normalize, contains_term, evaluate_risk
from .schemas import (
    AcaoCuidado,
    PerfilPersonalizacao,
    PlanoCuidadoRequest,
    ServicoRecomendado,
)


AVISO_SEGURANCA = (
    "Este plano organiza o cuidado contínuo e prioriza ações com base nos "
    "dados cadastrados. Ele não substitui consulta, diagnóstico ou conduta "
    "de um médico-veterinário."
)


# ---------------------------------------------------------------------------
# Catálogo de serviços da clínica
# ---------------------------------------------------------------------------

SERVICOS: dict[str, tuple[str, str]] = {
    "ATENDIMENTO_URGENCIA": (
        "Atendimento de urgência",
        "Avaliação imediata para sinais potencialmente graves.",
    ),
    "CONSULTA_CLINICA": (
        "Consulta clínica",
        "Avaliação de sinais ou alterações relatadas pelo tutor.",
    ),
    "CONSULTA_ROTINA": (
        "Consulta de rotina / check-up",
        "Exame clínico periódico para acompanhamento preventivo.",
    ),
    "CHECKUP_GERIATRICO": (
        "Check-up sênior",
        "Avaliação ampliada para pets em fase sênior.",
    ),
    "EXAMES_LABORATORIAIS": (
        "Exames laboratoriais",
        "Exames de rotina solicitados a critério do veterinário.",
    ),
    "VACINACAO": (
        "Vacinação",
        "Aplicação ou reforço de vacinas do protocolo da espécie.",
    ),
    "CONTROLE_PARASITARIO": (
        "Controle parasitário",
        "Vermifugação e prevenção de pulgas e carrapatos.",
    ),
    "CONSULTA_RETORNO": (
        "Consulta de retorno",
        "Acompanhamento de tratamento em andamento.",
    ),
    "AVALIACAO_COMPORTAMENTAL": (
        "Avaliação comportamental",
        "Orientação para alterações de comportamento.",
    ),
    "AVALIACAO_NUTRICIONAL": (
        "Avaliação nutricional",
        "Ajuste de dieta e controle de peso.",
    ),
    "ODONTOLOGIA": (
        "Avaliação odontológica",
        "Avaliação de dentes e gengivas.",
    ),
    "CASTRACAO": (
        "Avaliação para castração",
        "Conversa com o veterinário sobre indicação de castração.",
    ),
    "FISIOTERAPIA": (
        "Fisioterapia e reabilitação",
        "Exercícios e fortalecimento para pets com limitação de mobilidade.",
    ),
}


# ---------------------------------------------------------------------------
# Personalização por espécie
# ---------------------------------------------------------------------------

ESPECIES = {
    "cachorro": "cao", "cao": "cao", "dog": "cao", "canino": "cao",
    "gato": "gato", "felino": "gato", "cat": "gato",
    "equino": "equino", "cavalo": "equino",
    "bovino": "bovino", "vaca": "bovino", "boi": "bovino",
    "coelho": "coelho",
    "peixe": "peixe",
    "passaro": "ave", "galinha": "ave", "papagaio": "ave",
    "canario": "ave", "calopsita": "ave", "ave": "ave",
}

# (limite de filhote, início da fase sênior) em anos
FASES_VIDA = {
    "cao": (1, 7),
    "gato": (1, 10),
    "equino": (2, 15),
    "bovino": (1, 10),
    "coelho": (0.5, 5),
    "ave": (0.5, 8),
}

# Vacinas essenciais por espécie: nome exibido -> termos de busca
VACINAS_ESSENCIAIS: dict[str, dict[str, list[str]]] = {
    "cao": {
        "Polivalente (V8/V10)": ["v8", "v10", "v11", "polivalente", "multipla"],
        "Antirrábica": ["antirrabica", "raiva", "rabica"],
    },
    "gato": {
        "Polivalente felina (V3/V4/V5)": [
            "v3", "v4", "v5", "triplice", "quadrupla", "quintupla",
        ],
        "Antirrábica": ["antirrabica", "raiva", "rabica"],
    },
    "equino": {
        "Tétano": ["tetano"],
        "Influenza equina": ["influenza"],
        "Encefalomielite": ["encefalo"],
        "Antirrábica": ["antirrabica", "raiva", "rabica"],
    },
    "bovino": {
        "Brucelose": ["brucel"],
        "Clostridioses": ["clostrid"],
        "Antirrábica": ["antirrabica", "raiva", "rabica"],
    },
}

TERMOS_VACINA = ["vacin", "v8", "v10", "v4", "v5", "antirrabica", "dose", "reforco"]

TERMOS_COMPORTAMENTO = [
    "ansied", "agressiv", "medo", "estress", "lambendo", "latindo muito",
    "destrui", "xixi fora", "escondend", "isolad", "mordend", "miando muito",
]
TERMOS_NUTRICAO = [
    "obes", "sobrepeso", "acima do peso", "emagrec", "perdeu peso",
    "ganhou peso", "ganho de peso", "dieta", "comendo demais",
]
TERMOS_ODONTO = ["tartaro", "mau halito", "dente", "gengiva"]
TERMOS_PARASITAS = ["pulga", "carrapato", "verme", "vermifug"]
TERMOS_PELE = ["cocei", "cocando", "queda de pelo", "alergia", "feridinha"]

PESO_PRIORIDADE = {"baixa": 3, "moderada": 10, "alta": 20, "urgente": 45}
SCORE_SERVICO = {"baixa": 35, "moderada": 60, "alta": 80, "urgente": 100}


# ---------------------------------------------------------------------------
# Utilitários de dados
# ---------------------------------------------------------------------------


def parse_date(value: Any) -> date | None:
    """Aceita YYYY-MM-DD, ISO com horário e DD/MM/YYYY."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        y, m, d = map(int, match.groups())
    else:
        match = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
        if not match:
            return None
        d, m, y = map(int, match.groups())

    try:
        return date(y, m, d)
    except ValueError:
        return None


def _first_date(record: dict[str, Any], keys: list[str]) -> date | None:
    for key in keys:
        parsed = parse_date(record.get(key))
        if parsed:
            return parsed
    return None


def _registro_date(record: dict[str, Any]) -> date | None:
    return _first_date(
        record,
        ["dataHoraRegistro", "data_hora_registro", "data", "dataConsulta", "data_consulta"],
    )


def _proximo_date(record: dict[str, Any]) -> date | None:
    return _first_date(record, ["proximoPrevisto", "proximo_previsto", "proximaData"])


def _record_text(record: dict[str, Any]) -> str:
    return _normalize(" ".join(str(v) for v in record.values() if v is not None))


def _record_label(record: dict[str, Any]) -> str:
    for key in ["nomeServico", "nome_servico", "nome", "medicamento", "atividade", "descricao"]:
        if record.get(key):
            return str(record[key])
    return "registro"


def _fmt(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def especie_grupo(tipo: str | None) -> str:
    return ESPECIES.get(_normalize(tipo or "").strip(), "outro")


def idade_em_anos(animal: Any, hoje: date) -> float | None:
    """Usa idade (número, '3 anos', '6 meses') ou data de nascimento."""
    for value in [animal.dataNascimento, animal.idade]:
        nascimento = parse_date(value)
        if nascimento:
            return round((hoje - nascimento).days / 365.25, 1)

    if animal.idade is None:
        return None
    if isinstance(animal.idade, int):
        return float(animal.idade)

    text = _normalize(str(animal.idade))
    number = re.search(r"\d+([.,]\d+)?", text)
    if not number:
        return None
    valor = float(number.group().replace(",", "."))
    return round(valor / 12, 1) if "mes" in text else valor


def fase_vida(grupo: str, idade: float | None) -> str:
    if idade is None or grupo not in FASES_VIDA:
        return "indefinida"
    filhote, senior = FASES_VIDA[grupo]
    if idade < filhote:
        return "filhote"
    if idade >= senior:
        return "senior"
    return "adulto"


def _max_priority(values: list[str]) -> str:
    return max(values, key=lambda p: PRIORITY_ORDER[p], default="baixa")


# ---------------------------------------------------------------------------
# Construção do plano
# ---------------------------------------------------------------------------


@dataclass
class ResultadoMotor:
    perfil: PerfilPersonalizacao
    acoes: list[AcaoCuidado]
    servicos: list[ServicoRecomendado]
    score_risco: int
    prioridade: str
    procurar_veterinario: bool
    sinais_atencao: list[str] = field(default_factory=list)


class _Builder:
    def __init__(self) -> None:
        self.acoes: list[AcaoCuidado] = []
        self.servicos: dict[str, ServicoRecomendado] = {}

    def acao(self, titulo, descricao, categoria, prioridade, prazo, motivo, origem):
        self.acoes.append(
            AcaoCuidado(
                titulo=titulo,
                descricao=descricao,
                categoria=categoria,
                prioridade=prioridade,
                prazo_dias=max(0, prazo),
                motivo=motivo,
                origem_dados=origem,
            )
        )

    def servico(self, codigo, prioridade, motivo, bonus=0):
        score = min(100, SCORE_SERVICO[prioridade] + bonus)
        atual = self.servicos.get(codigo)
        if atual and atual.score >= score:
            return
        self.servicos[codigo] = ServicoRecomendado(
            codigo=codigo,
            nome=SERVICOS[codigo][0],
            motivo=motivo,
            prioridade=prioridade,
            score=score,
        )


def _avaliar_vacinas(b: _Builder, grupo, fase, preventivos, hoje):
    essenciais = VACINAS_ESSENCIAIS.get(grupo, {})
    registradas: list[str] = []
    pendentes: list[str] = []
    usados: set[int] = set()

    for nome, termos in essenciais.items():
        matches = [
            (i, p) for i, p in enumerate(preventivos)
            if any(contains_term(_record_text(p), t) for t in termos)
        ]
        if not matches:
            pendentes.append(nome)
            prioridade = "alta" if fase == "filhote" else "moderada"
            b.acao(
                f"Atualizar vacina: {nome}",
                f"Confirme com a clínica a aplicação da vacina {nome}.",
                "preventivo", prioridade, 7 if fase == "filhote" else 15,
                "Vacina essencial para a espécie sem registro no histórico.",
                ["perfil.tipo", "preventivos"],
            )
            b.servico("VACINACAO", prioridade, f"{nome} sem registro no histórico.")
            continue

        registradas.append(nome)
        usados.update(i for i, _ in matches)
        ultimo = max(
            (p for _, p in matches),
            key=lambda p: (_proximo_date(p) or _registro_date(p) or date.min),
        )
        _avaliar_prazo(b, ultimo, nome, hoje, essencial=True)

    # Demais preventivos com próxima data (vermífugo, antipulgas, etc.)
    for i, p in enumerate(preventivos):
        if i in usados:
            continue
        _avaliar_prazo(b, p, _record_label(p), hoje, essencial=False)

    return list(essenciais.keys()), registradas, pendentes


def _avaliar_prazo(b: _Builder, registro, nome, hoje, essencial):
    proximo = _proximo_date(registro)
    registro_em = _registro_date(registro)
    texto = _record_text(registro)
    eh_vacina = essencial or any(contains_term(texto, t) for t in TERMOS_VACINA)
    servico = "VACINACAO" if eh_vacina else (
        "CONTROLE_PARASITARIO" if any(contains_term(texto, t) for t in TERMOS_PARASITAS) else "CONSULTA_ROTINA"
    )

    if proximo:
        dias = (proximo - hoje).days
        if dias < 0:
            b.acao(
                f"{'Reforço atrasado' if eh_vacina else 'Prazo vencido'}: {nome}",
                f"O próximo evento de {nome} estava previsto para {_fmt(proximo)}.",
                "preventivo", "alta", 3,
                f"Prazo vencido há {-dias} dia(s).",
                ["preventivos.proximoPrevisto"],
            )
            b.servico(servico, "alta", f"{nome} com prazo vencido em {_fmt(proximo)}.", bonus=min(15, -dias // 10))
        elif dias <= 30:
            b.acao(
                f"Lembrete: {nome}",
                f"{nome} previsto para {_fmt(proximo)}. Agende com antecedência.",
                "preventivo", "moderada", dias,
                f"Evento preventivo nos próximos {dias} dia(s).",
                ["preventivos.proximoPrevisto"],
            )
            b.servico(servico, "moderada", f"{nome} previsto para {_fmt(proximo)}.")
        return

    if essencial and registro_em and (hoje - registro_em).days > 365:
        b.acao(
            f"Verificar reforço anual: {nome}",
            f"O último registro de {nome} é de {_fmt(registro_em)}.",
            "preventivo", "moderada", 15,
            "Último registro com mais de 12 meses e sem próxima data cadastrada.",
            ["preventivos.dataHoraRegistro"],
        )
        b.servico("VACINACAO", "moderada", f"Último registro de {nome} há mais de 1 ano.")


def _avaliar_consultas(b: _Builder, grupo, fase, request, hoje):
    if grupo == "peixe":
        b.acao(
            "Monitorar parâmetros da água",
            "Registre pH, temperatura e amônia do aquário periodicamente.",
            "bem_estar", "baixa", 7,
            "Para peixes, a qualidade da água é o principal fator preventivo.",
            ["perfil.tipo"],
        )
        return

    datas = [d for d in (_registro_date(c) for c in request.consultas) if d]
    ultima = max(datas) if datas else None
    sem_consulta = ultima is None or (hoje - ultima).days > 365
    if fase == "senior":
        sem_consulta = ultima is None or (hoje - ultima).days > 180

    if not sem_consulta:
        return

    motivo = (
        f"Última consulta registrada em {_fmt(ultima)}."
        if ultima else "Nenhuma consulta registrada no histórico."
    )
    if fase == "senior":
        b.acao(
            "Agendar check-up sênior",
            "Pets sênior se beneficiam de check-ups semestrais com exames.",
            "consulta", "moderada", 30, motivo, ["perfil.idade", "consultas"],
        )
        b.servico("CHECKUP_GERIATRICO", "moderada", "Fase sênior. " + motivo, bonus=10)
        b.servico("EXAMES_LABORATORIAIS", "moderada", "Indicados a critério do veterinário no check-up sênior.")
    else:
        b.acao(
            "Agendar consulta de rotina",
            "Um check-up anual ajuda a manter o acompanhamento em dia.",
            "consulta", "moderada" if fase == "filhote" else "baixa", 30,
            motivo, ["consultas"],
        )
        b.servico("CONSULTA_ROTINA", "moderada" if fase == "filhote" else "baixa", motivo)


def _avaliar_terapeuticos(b: _Builder, terapeuticos, hoje):
    if not terapeuticos:
        return
    nomes = ", ".join(dict.fromkeys(_record_label(t) for t in terapeuticos[-5:]))
    b.acao(
        "Manter adesão ao tratamento prescrito",
        f"Siga exatamente a prescrição registrada ({nomes}). Não altere doses por conta própria.",
        "terapeutico", "moderada", 0,
        "Há tratamento terapêutico cadastrado.",
        ["terapeuticos"],
    )
    datas = [d for d in (_registro_date(t) for t in terapeuticos) if d]
    recente = not datas or (hoje - max(datas)).days <= 60
    if recente:
        b.servico("CONSULTA_RETORNO", "moderada", f"Acompanhamento do tratamento: {nomes}.")


def _avaliar_comportamento(b: _Builder, grupo, fase, request):
    registros = [*request.bem_estar, *request.comportamento]
    texto = " ".join(_record_text(r) for r in registros)
    texto += " " + _normalize(request.animal.observacaoGeral or "")

    def hit(termos):
        return [t for t in termos if contains_term(texto, t)]

    if hit(TERMOS_COMPORTAMENTO):
        b.acao(
            "Acompanhar alteração de comportamento",
            "Registre quando o comportamento acontece e o que mudou na rotina.",
            "comportamento", "moderada", 14,
            "Registros de bem-estar ou comportamento indicam alteração de comportamento.",
            ["comportamento", "bem_estar"],
        )
        b.servico("AVALIACAO_COMPORTAMENTAL", "moderada", "Alteração de comportamento registrada.")

    if hit(TERMOS_NUTRICAO):
        b.acao(
            "Revisar alimentação e peso",
            "Registre peso e alimentação semanalmente para acompanhar a evolução.",
            "bem_estar", "moderada", 14,
            "Registros mencionam peso ou dieta.",
            ["bem_estar", "perfil.peso"],
        )
        b.servico("AVALIACAO_NUTRICIONAL", "moderada", "Registros mencionam alteração de peso ou dieta.")

    if hit(TERMOS_ODONTO):
        b.servico("ODONTOLOGIA", "baixa", "Registros mencionam dentes, gengiva ou hálito.")

    if hit(TERMOS_PARASITAS):
        b.servico("CONTROLE_PARASITARIO", "moderada", "Registros mencionam parasitas.")

    if hit(TERMOS_PELE):
        b.servico("CONSULTA_CLINICA", "moderada", "Registros mencionam coceira ou alteração de pele.")

    if not registros and grupo != "peixe":
        b.acao(
            "Registrar rotina de bem-estar",
            "Anote alimentação, atividade e comportamento para personalizar o acompanhamento.",
            "bem_estar", "baixa", 7,
            "Não há registros de bem-estar ou comportamento.",
            ["bem_estar", "comportamento"],
        )

    if grupo in ("cao", "gato") and request.animal.castrado is False and fase == "adulto":
        b.servico("CASTRACAO", "baixa", "Pet adulto não castrado; avaliar indicação com o veterinário.")


# ---------------------------------------------------------------------------
# Condições registradas pelo tutor (perfil e histórico de bem-estar)
# ---------------------------------------------------------------------------

TITULOS_CONDICAO = ("condicao", "alergia", "saude: relato")
TERMOS_MOBILIDADE = [
    "pata", "membro", "amput", "tres patas", "displasia", "paralis", "paraplegi", "manca", "artrose",
]


def condicoes_registradas(animal: Any, bem_estar: list[dict[str, Any]]) -> list[str]:
    """Condições de saúde informadas: 'Condição: ...' no perfil e registros de saúde do histórico."""
    from .observacao import PERMANENTES, PRONOMES

    condicoes: list[str] = []
    for parte in (animal.observacaoGeral or "").split("|"):
        achado = re.search(r"condi[cç][aã]o\s*:\s*(.+)", parte.strip(), re.I)
        if achado:
            condicoes.append(achado.group(1).strip(" ."))

    for registro in bem_estar:
        titulo = _normalize(str(registro.get("atividade") or registro.get("nomeAtividade") or ""))
        descricao = str(registro.get("observacao") or "").strip(" .")
        texto = _normalize(descricao)
        if descricao and (titulo.startswith(TITULOS_CONDICAO) or any(t in texto for t in PERMANENTES)):
            condicoes.append(descricao)

    vistas, unicas = set(), []
    for condicao in condicoes:
        condicao = PRONOMES.sub("", condicao.strip())
        if not condicao:
            continue
        chave = _normalize(condicao)
        if chave not in vistas:
            vistas.add(chave)
            unicas.append(condicao[0].upper() + condicao[1:])
    return unicas


def _avaliar_condicoes(b: _Builder, condicoes: list[str]) -> None:
    for condicao in condicoes:
        mobilidade = any(t in _normalize(condicao) for t in TERMOS_MOBILIDADE)
        b.acao(
            f"Cuidados com condição registrada: {condicao}",
            (
                "Adapte exercícios e brincadeiras para evitar impacto e sobrecarga nos outros "
                "membros, e leve a condição à próxima consulta."
                if mobilidade else
                "Considere essa condição na rotina e leve-a à próxima consulta para o veterinário avaliar."
            ),
            "bem_estar", "moderada", 30,
            f"Condição informada pelo tutor e registrada no perfil: {condicao}.",
            ["perfil.observacaoGeral", "bem_estar"],
        )
        if mobilidade:
            b.servico("FISIOTERAPIA", "moderada", f"Condição de mobilidade registrada: {condicao}.")
        b.servico("CONSULTA_ROTINA", "moderada", f"Acompanhamento da condição registrada: {condicao}.")


def _recentes(registros, hoje, dias=30):
    """Registros sem data ou dos últimos `dias` dias (sinais atuais)."""
    return [
        r for r in registros
        if (d := _registro_date(r)) is None or (hoje - d).days <= dias
    ]


def _avaliar_sinais(b: _Builder, request, hoje) -> tuple[str, list[str], bool]:
    # Tratamentos e registros antigos são histórico, não sinal atual.
    # O nome do pet fica de fora para evitar falsos positivos.
    risk = evaluate_risk(
        {
            "observacao": request.animal.observacaoGeral,
            "bem_estar": _recentes(request.bem_estar, hoje),
            "comportamento": _recentes(request.comportamento, hoje),
            "consultas": _recentes(request.consultas, hoje),
        }
    )
    if risk.minimum_priority == "urgente":
        b.acao(
            "Procurar atendimento veterinário imediato",
            "Há sinais potencialmente graves no histórico recente. Não medique por conta própria.",
            "urgencia", "urgente", 0,
            "; ".join(risk.red_flags),
            ["bem_estar", "comportamento", "consultas"],
        )
        b.servico("ATENDIMENTO_URGENCIA", "urgente", "; ".join(risk.red_flags))
    elif risk.minimum_priority == "alta":
        b.acao(
            "Agendar avaliação dos sinais relatados",
            "Observe a evolução e agende avaliação clínica nos próximos dias.",
            "consulta", "alta", 2,
            "; ".join(risk.reasons),
            ["bem_estar", "comportamento", "consultas"],
        )
        b.servico("CONSULTA_CLINICA", "alta", "; ".join(risk.reasons))
    return risk.minimum_priority, risk.red_flags, risk.seek_vet


def _priority_from_score(score: int) -> str:
    if score >= 60:
        return "alta"
    if score >= 25:
        return "moderada"
    return "baixa"


def gerar_plano(request: PlanoCuidadoRequest) -> ResultadoMotor:
    hoje = parse_date(request.data_referencia) or date.today()
    animal = request.animal
    grupo = especie_grupo(animal.tipo)
    idade = idade_em_anos(animal, hoje)
    fase = fase_vida(grupo, idade)

    b = _Builder()
    prioridade_sinais, sinais, procurar_vet = _avaliar_sinais(b, request, hoje)
    essenciais, registradas, pendentes = _avaliar_vacinas(b, grupo, fase, request.preventivos, hoje)
    _avaliar_terapeuticos(b, request.terapeuticos, hoje)
    _avaliar_consultas(b, grupo, fase, request, hoje)
    _avaliar_comportamento(b, grupo, fase, request)
    condicoes = condicoes_registradas(animal, request.bem_estar)
    _avaliar_condicoes(b, condicoes)

    acoes = sorted(b.acoes, key=lambda a: (-PRIORITY_ORDER[a.prioridade], a.prazo_dias))
    servicos = sorted(b.servicos.values(), key=lambda s: -s.score)

    score = sum(PESO_PRIORIDADE[a.prioridade] for a in acoes)
    score += 10 if fase == "senior" else 5 if fase == "filhote" else 0
    score = min(100, score)
    if prioridade_sinais == "urgente":
        score = max(score, 90)

    prioridade = _max_priority(
        [prioridade_sinais, _priority_from_score(score), *[a.prioridade for a in acoes]]
    )

    return ResultadoMotor(
        perfil=PerfilPersonalizacao(
            especie=grupo,
            fase_vida=fase,
            idade_anos=idade,
            vacinas_essenciais=essenciais,
            vacinas_registradas=registradas,
            vacinas_pendentes=pendentes,
            condicoes=condicoes,
        ),
        acoes=acoes,
        servicos=servicos,
        score_risco=score,
        prioridade=prioridade,
        procurar_veterinario=procurar_vet or prioridade == "urgente",
        sinais_atencao=sinais,
    )


def catalogo_servicos() -> list[dict[str, str]]:
    return [
        {"codigo": codigo, "nome": nome, "descricao": descricao}
        for codigo, (nome, descricao) in SERVICOS.items()
    ]


# ---------------------------------------------------------------------------
# Calendário de vacinas recomendado por espécie e fase de vida.
# Referência geral para orientar o tutor; o calendário final é do veterinário.
# ---------------------------------------------------------------------------

CALENDARIO_VACINAS = {
    "cao": {
        "filhote": [
            "Polivalente (V8/V10): série inicial a partir de 6 a 8 semanas de vida, "
            "com reforços a cada 3 a 4 semanas até cerca de 16 semanas",
            "Antirrábica: a partir de 12 semanas de vida",
        ],
        "adulto": [
            "Polivalente (V8/V10): reforço anual",
            "Antirrábica: reforço anual",
        ],
        "opcionais": (
            "gripe canina (tosse dos canis), giardíase e leishmaniose, "
            "conforme a rotina do cão e a região"
        ),
    },
    "gato": {
        "filhote": [
            "Polivalente felina (V3/V4/V5): série inicial a partir de 8 semanas de vida, "
            "com reforços a cada 3 a 4 semanas até cerca de 16 semanas",
            "Antirrábica: a partir de 12 semanas de vida",
        ],
        "adulto": [
            "Polivalente felina (V3/V4/V5): reforço anual ou conforme o veterinário",
            "Antirrábica: reforço anual",
        ],
        "opcionais": "FeLV (leucemia felina), principalmente para gatos com acesso à rua, após teste",
    },
}


CALENDARIO_VACINAS["equino"] = {
    "filhote": [
        "Tétano, influenza equina, encefalomielite e antirrábica: primeira dose a partir "
        "de 4 a 6 meses de idade, com reforço cerca de 30 dias depois",
    ],
    "adulto": [
        "Tétano: reforço anual",
        "Influenza equina: reforço anual, ou semestral para cavalos que viajam e competem",
        "Encefalomielite: reforço anual",
        "Antirrábica: reforço anual",
    ],
    "opcionais": "rinopneumonite, garrotilho e leptospirose, conforme a região e a rotina do cavalo",
}
CALENDARIO_VACINAS["bovino"] = {
    "filhote": [
        "Brucelose (B19 ou RB51): dose única em fêmeas de 3 a 8 meses, obrigatória",
        "Clostridioses: primeira dose a partir de 2 a 4 meses, com reforço cerca de 30 dias depois",
        "Antirrábica: a partir de 3 meses em regiões de risco, com reforço cerca de 30 dias depois",
    ],
    "adulto": [
        "Clostridioses: reforço anual",
        "Antirrábica: reforço anual em regiões de risco",
    ],
    "opcionais": "leptospirose e IBR/BVD, conforme o rebanho e o calendário oficial do estado",
}
CALENDARIO_VACINAS["galinha"] = {
    "filhote": [
        "Marek: no primeiro dia de vida (normalmente já aplicada no incubatório)",
        "Newcastle e bronquite infecciosa: nas primeiras semanas de vida, com reforços conforme o veterinário",
        "Gumboro: nas primeiras semanas de vida",
        "Bouba aviária: a partir de 4 a 6 semanas de vida",
    ],
    "adulto": [
        "Newcastle e bronquite infecciosa: reforços periódicos conforme o veterinário",
    ],
    "opcionais": "coriza infecciosa e outras, conforme a região e o tamanho da criação",
}

# Espécies sem vacinas de rotina no Brasil: orientação preventiva no lugar do calendário.
SEM_VACINAS = {
    "ave": (
        "{Especie} não tem vacinas de rotina no Brasil. A prevenção é feita com check-up "
        "anual com veterinário de aves ou de animais silvestres, exame de fezes para "
        "parasitas e, em papagaios e calopsitas, exame para clamidiose (psitacose), que "
        "também pode passar para pessoas. Vermífugo só com indicação do veterinário."
    ),
    "peixe": (
        "Peixes ornamentais não recebem vacinas. A prevenção é manter a qualidade da "
        "água (temperatura, pH, amônia), fazer quarentena de peixes novos e não "
        "superlotar o aquário."
    ),
    "coelho": (
        "No Brasil não há vacinas de rotina disponíveis para coelhos. A prevenção é o "
        "check-up anual com veterinário de animais exóticos, a avaliação dos dentes, "
        "que crescem a vida toda, alimentação com bastante feno e controle de parasitas."
    ),
}

# Espécie exata, quando o tipo é amplo (ex.: PASSARO pode ser papagaio ou canário).
ESPECIES_DETALHADAS = [
    ("papagaio", "papagaio"), ("calopsita", "calopsita"), ("periquito", "periquito"),
    ("arara", "arara"), ("cacatua", "cacatua"), ("canario", "canário"),
    ("galinha", "galinha"), ("frango", "galinha"), ("pintinho", "galinha"), ("galo", "galinha"),
]


def especie_detalhada(*textos: Any) -> str | None:
    """Primeira espécie exata citada nos textos, na ordem em que foram passados."""
    for texto in textos:
        normalizado = _normalize(str(texto or ""))
        for termo, nome in ESPECIES_DETALHADAS:
            if re.search(rf"\b{termo}\w*", normalizado):
                return nome
    return None


def calendario_vacinas(
    grupo: str, idade: float | None, especie: str | None = None
) -> tuple[list[str], str | None, str | None]:
    """Devolve (vacinas recomendadas, vacinas opcionais, observação).

    Para espécies sem vacina de rotina, a lista vem vazia e a observação traz a
    orientação preventiva da espécie.
    """
    chave = "galinha" if grupo == "ave" and especie == "galinha" else grupo
    calendario = CALENDARIO_VACINAS.get(chave)
    if not calendario:
        if grupo in SEM_VACINAS:
            nome = (especie or {"ave": "Ave de estimação", "peixe": "Peixe", "coelho": "Coelho"}[grupo])
            return [], None, SEM_VACINAS[grupo].format(Especie=nome[0].upper() + nome[1:])
        essenciais = list(VACINAS_ESSENCIAIS.get(grupo, {}))
        return essenciais, None, None

    fase = fase_vida(grupo, idade)
    observacao = None
    if idade is None:
        vacinas = [f"Filhote - {v}" for v in calendario["filhote"]]
        vacinas += [f"Adulto - {v}" for v in calendario["adulto"]]
        observacao = "Se me disser a idade, deixo o calendário certo para ele."
    elif fase == "filhote":
        vacinas = list(calendario["filhote"])
        if idade is not None and idade >= 0.4:
            observacao = (
                "Nessa idade a série inicial e a antirrábica já deveriam ter sido "
                "aplicadas. Se faltou alguma, a clínica completa o esquema e o "
                "próximo reforço passa a ser anual."
            )
    else:
        vacinas = list(calendario["adulto"])
    return vacinas, calendario["opcionais"], observacao


def descrever_idade(idade: float | None) -> str:
    if idade is None:
        return "idade não informada"
    if idade < 1:
        meses = max(1, round(idade * 12))
        return f"{meses} {'mês' if meses == 1 else 'meses'}"
    anos = int(idade)
    return f"{anos} {'ano' if anos == 1 else 'anos'}"
