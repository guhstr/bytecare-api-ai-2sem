"""
Pedido de agendamento pelo chat (consulta, vacinação, exames etc.).

Lê a conversa e identifica os serviços, o dia e o período preferidos. A IA
só monta o pedido; o tutor confirma no app, a API principal registra e a
clínica confirma ou recusa, notificando o tutor.
"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from .risk_engine import _normalize
from .schemas import ChatAgendamento, ChatRequest

INTENCAO = re.compile(r"\b(agend\w*|marc(ar|a|o|ando)|reserv\w*|solicit\w*)\b")

SERVICOS = [
    ("Consulta de rotina", r"\b(consultas?|check ?up|avaliacao|rotina)\b"),
    ("Vacinação", r"\b(vacin\w*|antirrabica|reforco)\b"),
    ("Vermifugação", r"\bvermif\w*"),
    ("Exames", r"\bexame\w*"),
    ("Banho e tosa", r"\b(banho|tosa)\b"),
    ("Castração", r"\bcastra\w*"),
    ("Retorno", r"\bretorno\b"),
]

DIAS_SEMANA = {
    "segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5, "domingo": 6,
}

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

FLEXIVEL = re.compile(
    r"\b(qualquer dia|tanto faz|quando (puder|tiver)|o quanto antes|primeiro horario|"
    r"mais cedo possivel|qualquer horario|sem preferencia)\b"
)

PERIODOS = [("manha", r"\b(manha|cedo)\b"), ("tarde", r"\btarde\b"), ("noite", r"\bnoite\b")]

# Mensagens do app que encerram o pedido (enviado ou cancelado).
FIM_AGENDAMENTO = ("pedido de agendamento enviado", "agendamento cancelado")

NOME_PERIODO = {"manha": "de manhã", "tarde": "à tarde", "noite": "à noite"}


@dataclass
class EstadoAgendamento:
    ativo: bool = False
    servicos: list[str] = field(default_factory=list)
    data: date | None = None
    hora: str | None = None
    periodo: str | None = None
    dia_flexivel: bool = False
    hora_flexivel: bool = False

    @property
    def falta(self) -> str | None:
        """O que ainda precisa ser perguntado: 'dia', 'horario' ou None."""
        if self.dia_flexivel:
            return None
        if self.data is None:
            return "dia"
        if self.hora is None and not self.hora_flexivel:
            return "horario"
        return None

    @property
    def pronto(self) -> bool:
        return self.ativo and bool(self.servicos) and self.falta is None

    def para_pedido(self, observacao: str | None = None) -> ChatAgendamento:
        return ChatAgendamento(
            servicos=self.servicos,
            data_preferida=self.data.isoformat() if self.data else None,
            horario=self.hora,
            periodo=self.periodo,
            observacao=observacao,
        )


def quer_agendar(texto: str) -> bool:
    texto = _normalize(texto)
    if INTENCAO.search(texto) and servicos_do_texto(texto):
        return True
    return bool(re.search(r"\b(quero|preciso|gostaria de)\s+(uma\s+|de\s+uma\s+)?(consulta|vacinar|levar)\b", texto))


def servicos_do_texto(texto: str) -> list[str]:
    texto = _normalize(texto)
    return [nome for nome, padrao in SERVICOS if re.search(padrao, texto)]


def data_do_texto(texto: str, hoje: date | None = None) -> date | None:
    texto = _normalize(texto)
    hoje = hoje or date.today()

    if re.search(r"\bdepois de amanha\b", texto):
        return hoje + timedelta(days=2)
    if re.search(r"\bamanha\b", texto):
        return hoje + timedelta(days=1)
    if re.search(r"\bhoje\b", texto):
        return hoje
    if re.search(r"\b(semana que vem|proxima semana)\b", texto):
        return hoje + timedelta(days=7 - hoje.weekday())

    for nome, indice in DIAS_SEMANA.items():
        if re.search(rf"\b{nome}(-feira| feira)?\b", texto):
            dias = (indice - hoje.weekday()) % 7 or 7
            return hoje + timedelta(days=dias)

    achado = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", texto)
    if achado:
        dia, mes = int(achado.group(1)), int(achado.group(2))
        ano = int(achado.group(3)) if achado.group(3) else hoje.year
        ano = ano + 2000 if ano < 100 else ano
        try:
            escolhida = date(ano, mes, dia)
        except ValueError:
            return None
        if escolhida < hoje and not achado.group(3):
            escolhida = escolhida.replace(year=hoje.year + 1)
        return escolhida

    meses = "|".join(MESES)
    achado = re.search(rf"\b(\d{{1,2}})\s+de\s+({meses})\b", texto)
    if achado:
        dia, mes = int(achado.group(1)), MESES[achado.group(2)]
        try:
            escolhida = date(hoje.year, mes, dia)
        except ValueError:
            return None
        return escolhida if escolhida >= hoje else escolhida.replace(year=hoje.year + 1)

    achado = re.search(r"\bdia\s+(\d{1,2})\b", texto)
    if achado:
        dia = int(achado.group(1))
        mes, ano = hoje.month, hoje.year
        if dia < hoje.day:
            mes, ano = (1, ano + 1) if mes == 12 else (mes + 1, ano)
        try:
            return date(ano, mes, dia)
        except ValueError:
            return None
    return None


HORA_FLEXIVEL = re.compile(r"\b(qualquer (horario|hora)|tanto faz o horario|horario tanto faz|sem preferencia de horario)\b")


def hora_do_texto(texto: str) -> str | None:
    """Lê '14h', '14:30', '9h30', 'às 9', '2 da tarde', 'meio dia'. Devolve 'HH:MM'."""
    texto = _normalize(texto)
    if re.search(r"\bmeio[ -]dia\b", texto):
        return "12:00"
    padroes = [
        r"\b(\d{1,2})[:h](\d{2})\b",
        r"\b(\d{1,2})\s*(?:h|hs|horas?)\b()",
        r"\bas\s+(\d{1,2})\b(?!\s*(?:[/:]|vacinas?|doses?|semanas?|meses|anos|dias|vezes|horas?\s+de))()",
        r"\b(\d{1,2})\s+da\s+(?:manha|tarde|noite)\b()",
    ]
    for padrao in padroes:
        achado = re.search(padrao, texto)
        if not achado:
            continue
        hora = int(achado.group(1))
        minuto = int(achado.group(2)) if achado.group(2) else 0
        if re.search(r"\bda (tarde|noite)\b", texto[achado.start():achado.end() + 12]) and hora < 12:
            hora += 12
        if 6 <= hora <= 22 and minuto < 60:
            return f"{hora:02d}:{minuto:02d}"
    return None


def periodo_da_hora(hora: str) -> str:
    h = int(hora[:2])
    return "manha" if h < 12 else "tarde" if h < 18 else "noite"


def periodo_do_texto(texto: str) -> str | None:
    texto = _normalize(texto)
    for nome, padrao in PERIODOS:
        if re.search(padrao, texto):
            return nome
    return None


def estado_agendamento(request: ChatRequest, hoje: date | None = None) -> EstadoAgendamento:
    turnos = [(m.role, _normalize(m.content)) for m in request.historico]
    atual = _normalize(request.mensagem)
    if not turnos or turnos[-1] != ("user", atual):
        turnos.append(("user", atual))

    inicio = None
    for i, (papel, texto) in enumerate(turnos):
        if papel == "user" and quer_agendar(texto):
            inicio = i if inicio is None else inicio
        elif papel == "assistant" and inicio is not None and any(f in texto for f in FIM_AGENDAMENTO):
            inicio = None

    estado = EstadoAgendamento()
    if inicio is None:
        return estado
    estado.ativo = True

    for papel, texto in turnos[inicio:]:
        if papel != "user":
            continue
        for servico in servicos_do_texto(texto):
            if servico not in estado.servicos:
                estado.servicos.append(servico)
        estado.data = data_do_texto(texto, hoje) or estado.data
        estado.hora = hora_do_texto(texto) or estado.hora
        estado.periodo = periodo_do_texto(texto) or estado.periodo
        if HORA_FLEXIVEL.search(texto):
            estado.hora_flexivel = True
        elif FLEXIVEL.search(texto):
            # "tanto faz" antes do dia vale para dia e horário; depois, só para o horário.
            if estado.data is None:
                estado.dia_flexivel = True
            estado.hora_flexivel = True

    if estado.hora:
        estado.periodo = periodo_da_hora(estado.hora)

    if not estado.servicos:
        estado.servicos = ["Consulta de rotina"]
    return estado


DIAS_EXIBICAO = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def descrever_quando(estado: EstadoAgendamento) -> str:
    if estado.data is None:
        return "no primeiro horário disponível"
    quando = f"{DIAS_EXIBICAO[estado.data.weekday()]}, {estado.data.strftime('%d/%m')}"
    if estado.hora:
        return f"{quando} às {estado.hora.replace(':00', 'h').replace(':', 'h')}"
    if estado.periodo:
        return f"{quando} {NOME_PERIODO[estado.periodo]}, horário a combinar"
    return f"{quando}, horário a combinar"


def pergunta_quando(estado: EstadoAgendamento) -> str:
    if estado.falta == "dia":
        return "Qual dia e horário você prefere? Se tanto faz, é só dizer \"qualquer dia\"."
    dia = f"{DIAS_EXIBICAO[estado.data.weekday()]}, {estado.data.strftime('%d/%m')}"
    periodo = f" {NOME_PERIODO[estado.periodo]}" if estado.periodo else ""
    exemplo = {"manha": "10h", "tarde": "14h", "noite": "19h"}.get(estado.periodo, "10h")
    return f"Anotei {dia}{periodo}. Qual horário você prefere (por exemplo, {exemplo})? Se tanto faz, diga \"qualquer horário\"."


def juntar(itens: list[str]) -> str:
    itens = [i.lower() if n else i for n, i in enumerate(itens)]
    return itens[0] if len(itens) == 1 else f"{', '.join(itens[:-1])} e {itens[-1]}"
