import unittest

from app.chat_service import apply_output_guardrails, create_mock_chat_response
from app.schemas import AnimalContext, ChatMessage, ChatRequest, ChatResponse


def conversar(mensagens, animal=None):
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


class CadastroAnimalTest(unittest.TestCase):

    def test_cadastro_completo_em_uma_mensagem(self):
        [resposta] = conversar(
            ["quero fazer o cadastro do meu cão, o Draco de 10 meses e husky siberiano"]
        )
        self.assertEqual(resposta.acao, "cadastrar_animal")
        dados = resposta.animal_cadastro
        self.assertEqual(dados.nome, "Draco")
        self.assertEqual(dados.especie, "CACHORRO")
        self.assertEqual(dados.raca, "Husky Siberiano")
        self.assertEqual(dados.idade_meses, 10)

    def test_pergunta_so_o_que_falta(self):
        respostas = conversar(["quero cadastrar meu cachorro", "Draco", "10 meses", "husky"])
        self.assertIn("nome", respostas[0].resposta)
        self.assertNotIn("nome", respostas[1].resposta)
        self.assertIn("raça", respostas[2].resposta)
        self.assertNotIn("idade", respostas[2].resposta)
        self.assertEqual(respostas[3].acao, "cadastrar_animal")
        self.assertEqual(respostas[3].animal_cadastro.nome, "Draco")

    def test_cadastro_encerrado_nao_repete(self):
        historico = [
            ChatMessage(role="user", content="cadastra meu gato Mia, persa, 3 anos"),
            ChatMessage(role="assistant", content="Confira os dados."),
            ChatMessage(role="assistant", content="Pronto! Mia foi cadastrado no ByteCare."),
        ]
        request = ChatRequest(mensagem="obrigado", historico=historico)
        resposta = apply_output_guardrails(create_mock_chat_response(request), request)
        self.assertEqual(resposta.acao, "nenhuma")

    def test_guardrail_completa_acao_esquecida_pelo_modelo(self):
        request = ChatRequest(
            mensagem="quero cadastrar meu cão, o Draco de 10 meses, husky siberiano"
        )
        resposta = apply_output_guardrails(ChatResponse(resposta="Certo!"), request)
        self.assertEqual(resposta.acao, "cadastrar_animal")
        self.assertEqual(resposta.animal_cadastro.idade_meses, 10)


class VacinasRecomendadasTest(unittest.TestCase):

    def test_vacinas_do_filhote_durante_cadastro(self):
        respostas = conversar([
            "quero fazer o cadastro do meu cão, o Draco de 10 meses e husky siberiano",
            "quais vacinas eu preciso fazer?",
        ])
        texto = respostas[1].resposta
        self.assertIn("V8/V10", texto)
        self.assertIn("Antirrábica", texto)
        self.assertIn("série inicial", texto)
        self.assertNotIn("?", texto.split("\n")[0])

    def test_vacinas_do_pet_cadastrado_adulto(self):
        animal = AnimalContext(id=1, nome="Thor", tipo="CACHORRO", dataNascimento="2020-01-01")
        [resposta] = conversar(["quais vacinas ele precisa?"], animal=animal)
        self.assertIn("reforço anual", resposta.resposta)
        self.assertIn("Sem registro", resposta.resposta)

    def test_especie_sem_idade_lista_os_dois_calendarios(self):
        [resposta] = conversar(["quais vacinas meu gato precisa?"])
        self.assertIn("Filhote", resposta.resposta)
        self.assertIn("Adulto", resposta.resposta)

    def test_sem_especie_pergunta(self):
        [resposta] = conversar(["quais vacinas?"])
        self.assertIn("espécie", resposta.resposta)


if __name__ == "__main__":
    unittest.main()


class CadastroComExtrasTest(unittest.TestCase):
    """Resposta em lista com vacina já tomada e sinal de saúde no meio do cadastro."""

    MENSAGEM = (
        "Thor, sem raca definida, 5 anos, tem uma vacina v10 com a proxima no dia 2 de novembro, "
        "e ele ganhou muito e esta cansando muito rapido nos passeios"
    )

    def conversar(self, mensagens):
        from app.chat_service import apply_output_guardrails, create_mock_chat_response
        from app.schemas import ChatMessage, ChatRequest
        historico, resposta = [], None
        for mensagem in mensagens:
            request = ChatRequest(mensagem=mensagem, historico=historico)
            resposta = apply_output_guardrails(create_mock_chat_response(request), request)
            historico += [
                ChatMessage(role="user", content=mensagem),
                ChatMessage(role="assistant", content=resposta.resposta),
            ]
        return resposta

    def test_le_o_nome_e_nao_responde_calendario(self):
        resposta = self.conversar(["quero cadastrar um animal", self.MENSAGEM])
        self.assertNotIn("nome dele", resposta.resposta)
        self.assertIn("espécie", resposta.resposta)
        self.assertNotIn("Vacinas recomendadas", resposta.resposta)
        self.assertIn("V10", resposta.resposta)

    def test_cadastro_leva_vacina_e_observacao(self):
        resposta = self.conversar(["quero cadastrar um animal", self.MENSAGEM, "cachorro"])
        self.assertEqual(resposta.acao, "cadastrar_animal")
        self.assertEqual(resposta.animal_cadastro.nome, "Thor")
        self.assertEqual(resposta.animal_cadastro.idade_meses, 60)
        self.assertEqual(resposta.vacinas_cadastro[0].nome_vacina, "V10")
        self.assertTrue(resposta.vacinas_cadastro[0].proximo_previsto.endswith("-11-02"))
        self.assertIn("cansando", resposta.observacao_cadastro.descricao)

    def test_data_sem_ano(self):
        from datetime import date
        from app.cadastro import _data_proxima
        hoje = date(2026, 11, 4)
        self.assertEqual(_data_proxima("2 de novembro", hoje), "2026-11-02")
        self.assertEqual(_data_proxima("10/01", hoje), "2027-01-10")
        self.assertEqual(_data_proxima("15/03/2027", hoje), "2027-03-15")

    def test_pergunta_sobre_vacina_no_cadastro_continua_respondida(self):
        resposta = self.conversar([
            "quero cadastrar meu cachorro Rex de 2 meses",
            "quais vacinas ele precisa?",
        ])
        self.assertIn("Polivalente", resposta.resposta)
