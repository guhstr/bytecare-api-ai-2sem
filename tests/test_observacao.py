import unittest

from app.chat_service import apply_output_guardrails, create_mock_chat_response
from app.schemas import AnimalContext, ChatMessage, ChatRequest, ChatResponse

DRACO = AnimalContext(id="1", nome="Draco", tipo="CACHORRO", dataNascimento="2026-01-04")


def responder(mensagem, animal=DRACO, historico=None):
    request = ChatRequest(mensagem=mensagem, animal=animal, historico=historico or [])
    return apply_output_guardrails(create_mock_chat_response(request), request)


class RegistroObservacaoTest(unittest.TestCase):

    def test_condicao_permanente(self):
        resposta = responder("quero registrar que ele tem uma pata a menos")
        self.assertEqual(resposta.acao, "registrar_observacao")
        self.assertEqual(resposta.observacao_cadastro.descricao, "Tem uma pata a menos")
        self.assertTrue(resposta.observacao_cadastro.permanente)

    def test_observacao_nao_vira_cadastro_de_animal(self):
        resposta = responder("registra que meu cachorro tem uma pata a menos")
        self.assertEqual(resposta.acao, "registrar_observacao")
        self.assertIsNone(resposta.animal_cadastro)

    def test_comportamento_nao_e_permanente(self):
        resposta = responder("anota que ele fica muito agressivo com visitas")
        self.assertEqual(resposta.observacao_cadastro.categoria, "COMPORTAMENTO")
        self.assertFalse(resposta.observacao_cadastro.permanente)

    def test_pedido_vago_pergunta_o_conteudo(self):
        primeira = responder("quero registrar um problema dele")
        self.assertEqual(primeira.acao, "nenhuma")
        historico = [
            ChatMessage(role="user", content="quero registrar um problema dele"),
            ChatMessage(role="assistant", content=primeira.resposta),
        ]
        segunda = responder("ele nasceu sem a pata traseira", historico=historico)
        self.assertEqual(segunda.acao, "registrar_observacao")
        self.assertEqual(segunda.observacao_cadastro.descricao, "Nasceu sem a pata traseira")

    def test_sem_pet_nao_registra(self):
        resposta = responder("registra que ele tem uma pata a menos", animal=None)
        self.assertEqual(resposta.acao, "nenhuma")

    def test_guardrail_completa_acao_esquecida_pelo_modelo(self):
        request = ChatRequest(mensagem="registra que ele é alérgico a frango", animal=DRACO)
        resposta = apply_output_guardrails(ChatResponse(resposta="Certo!"), request)
        self.assertEqual(resposta.acao, "registrar_observacao")
        self.assertTrue(resposta.observacao_cadastro.permanente)


class CondicoesNoPerfilTest(unittest.TestCase):

    ANIMAL = {
        "id": "1", "nome": "Draco", "tipo": "CACHORRO", "dataNascimento": "2026-01-04",
        "observacaoGeral": "Idade informada: 10 meses. | Condição: Tem uma pata a menos",
    }
    BEM_ESTAR = [{"atividade": "Condição física: ausência de membro", "observacao": "Tem uma pata a menos"}]

    def test_analise_cita_a_condicao(self):
        from app.mock_service import create_mock_analysis
        from app.schemas import AnaliseRequest

        analise = create_mock_analysis(AnaliseRequest(animal=self.ANIMAL, bem_estar=self.BEM_ESTAR))
        self.assertIn("Tem uma pata a menos", analise.resumo)
        self.assertEqual(analise.fatores_relevantes[0], "Condição registrada: Tem uma pata a menos")

    def test_plano_inclui_condicao_acao_e_fisioterapia(self):
        from app.mock_service import build_care_plan
        from app.schemas import PlanoCuidadoRequest

        plano = build_care_plan(PlanoCuidadoRequest(animal=self.ANIMAL, bem_estar=self.BEM_ESTAR))
        self.assertEqual(plano.perfil.condicoes, ["Tem uma pata a menos"])
        self.assertTrue(any("pata a menos" in a.titulo for a in plano.acoes))
        self.assertIn("FISIOTERAPIA", [s.codigo for s in plano.servicos_recomendados])


if __name__ == "__main__":
    unittest.main()
