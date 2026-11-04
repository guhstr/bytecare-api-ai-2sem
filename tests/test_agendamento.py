import unittest
from datetime import date

from app.agendamento import data_do_texto, estado_agendamento, hora_do_texto, quer_agendar
from app.chat_service import apply_output_guardrails, create_mock_chat_response
from app.schemas import AnimalContext, ChatMessage, ChatRequest, ChatResponse

DRACO = AnimalContext(id="1", nome="Draco", tipo="CACHORRO", dataNascimento="2026-01-04")
QUARTA = date(2026, 11, 4)


def conversar(mensagens, animal=DRACO):
    historico, respostas = [], []
    for mensagem in mensagens:
        request = ChatRequest(mensagem=mensagem, historico=list(historico), animal=animal)
        resposta = apply_output_guardrails(create_mock_chat_response(request), request)
        respostas.append(resposta)
        historico += [
            ChatMessage(role="user", content=mensagem),
            ChatMessage(role="assistant", content=resposta.resposta),
        ]
    return respostas


class AgendamentoTest(unittest.TestCase):

    def test_agendamento_e_pergunta_de_vacinas_na_mesma_mensagem(self):
        primeira, segunda, terceira = conversar([
            "Quero agendar uma consulta de rotina, e a vacinacao nele, quais vacinas voce me recomenda",
            "sexta de manhã",
            "às 10h",
        ])
        self.assertIn("Antirrábica", primeira.resposta)
        self.assertIn("Qual dia e horário", primeira.resposta)
        self.assertEqual(primeira.acao, "nenhuma")
        self.assertIn("Qual horário", segunda.resposta)
        self.assertEqual(segunda.acao, "nenhuma")
        self.assertEqual(terceira.acao, "agendar")
        self.assertEqual(terceira.agendamento.servicos, ["Consulta de rotina", "Vacinação"])
        self.assertEqual(terceira.agendamento.horario, "10:00")
        self.assertEqual(terceira.agendamento.periodo, "manha")
        self.assertIn("Vacinas a avaliar", terceira.agendamento.observacao)

    def test_dia_e_horario_na_mesma_frase(self):
        [resposta] = conversar(["quero marcar banho e tosa amanhã às 2 da tarde"])
        self.assertEqual(resposta.acao, "agendar")
        self.assertEqual(resposta.agendamento.horario, "14:00")

    def test_qualquer_horario(self):
        respostas = conversar(["quero agendar uma consulta na sexta", "qualquer horário"])
        self.assertEqual(respostas[0].acao, "nenhuma")
        self.assertEqual(respostas[1].acao, "agendar")
        self.assertIsNone(respostas[1].agendamento.horario)

    def test_modelo_nao_envia_pedido_sem_dia(self):
        request = ChatRequest(
            mensagem="Quero agendar uma consulta de rotina e a vacinação dele, quais vacinas?",
            animal=DRACO,
        )
        resposta = ChatResponse(
            resposta="Qual dia você prefere?",
            acao="agendar",
            agendamento={"servicos": ["Consulta de rotina", "Vacinação"], "periodo": "tarde"},
        )
        resposta = apply_output_guardrails(resposta, request)
        self.assertEqual(resposta.acao, "nenhuma")
        self.assertIsNone(resposta.agendamento)

    def test_data_inventada_pelo_modelo_e_ignorada(self):
        request = ChatRequest(mensagem="quero agendar uma consulta para ele", animal=DRACO)
        resposta = ChatResponse(
            resposta="Certo!",
            acao="agendar",
            agendamento={"servicos": ["Consulta de rotina"], "data_preferida": "2026-11-10"},
        )
        self.assertEqual(apply_output_guardrails(resposta, request).acao, "nenhuma")

    def test_qualquer_dia(self):
        respostas = conversar(["preciso de uma consulta pra ele", "tanto faz"])
        self.assertEqual(respostas[1].acao, "agendar")
        self.assertIsNone(respostas[1].agendamento.data_preferida)

    def test_datas(self):
        self.assertEqual(data_do_texto("amanhã", QUARTA), date(2026, 11, 5))
        self.assertEqual(data_do_texto("na sexta-feira", QUARTA), date(2026, 11, 6))
        self.assertEqual(data_do_texto("quarta que vem", QUARTA), date(2026, 11, 11))
        self.assertEqual(data_do_texto("dia 2", QUARTA), date(2026, 12, 2))
        self.assertEqual(data_do_texto("10/12", QUARTA), date(2026, 12, 10))
        self.assertEqual(data_do_texto("15 de dezembro", QUARTA), date(2026, 12, 15))

    def test_horarios(self):
        self.assertEqual(hora_do_texto("14h30"), "14:30")
        self.assertEqual(hora_do_texto("às 9"), "09:00")
        self.assertEqual(hora_do_texto("2 da tarde"), "14:00")
        self.assertEqual(hora_do_texto("meio dia"), "12:00")
        self.assertIsNone(hora_do_texto("as 2 vacinas"))
        self.assertIsNone(hora_do_texto("10 meses"))

    def test_consultar_historico_nao_e_agendamento(self):
        self.assertFalse(quer_agendar("quero consultar o histórico dele"))

    def test_pedido_enviado_encerra(self):
        historico = [
            ChatMessage(role="user", content="quero agendar banho amanhã"),
            ChatMessage(role="assistant", content="Pronto! Pedido de agendamento enviado para a clínica."),
        ]
        estado = estado_agendamento(ChatRequest(mensagem="obrigado", historico=historico))
        self.assertFalse(estado.ativo)

    def test_sem_pet_nao_agenda(self):
        [resposta] = conversar(["quero agendar uma consulta amanhã"], animal=None)
        self.assertEqual(resposta.acao, "nenhuma")

    def test_guardrail_completa_acao_esquecida_pelo_modelo(self):
        request = ChatRequest(mensagem="quero marcar vacinação amanhã às 15h", animal=DRACO)
        resposta = apply_output_guardrails(ChatResponse(resposta="Certo!"), request)
        self.assertEqual(resposta.acao, "agendar")
        self.assertEqual(resposta.agendamento.horario, "15:00")
        self.assertEqual(resposta.agendamento.periodo, "tarde")


if __name__ == "__main__":
    unittest.main()
