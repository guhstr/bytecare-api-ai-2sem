import unittest

from app.chat_service import apply_output_guardrails, create_mock_chat_response
from app.remocao import pede_lista_pets, pede_remocao_animal
from app.schemas import AnimalContext, ChatRequest, ChatResponse

DRACO = AnimalContext(id="1", nome="Draco", tipo="CACHORRO", dataNascimento="2026-01-04")


def responder(mensagem, animal=DRACO):
    request = ChatRequest(mensagem=mensagem, animal=animal)
    return apply_output_guardrails(create_mock_chat_response(request), request)


class RemocaoAnimalTest(unittest.TestCase):

    def test_pedidos_de_remocao(self):
        for texto in [
            "apaga o Draco",
            "quero excluir o cadastro dele",
            "remove esse pet do aplicativo",
            "pode deletar ele",
            "Exclua o animal",
        ]:
            self.assertTrue(pede_remocao_animal(texto, "Draco"), texto)

    def test_outros_pedidos_nao_apagam_o_pet(self):
        for texto in [
            "apaga o agendamento do Draco",
            "como remover carrapato do cachorro",
            "exclui a vacina V10 dele",
            "o Draco adora correr",
            "quero cadastrar um gato",
            "remove a observação que eu registrei",
        ]:
            self.assertFalse(pede_remocao_animal(texto, "Draco"), texto)

    def test_mock_pede_confirmacao(self):
        resposta = responder("quero apagar o Draco")
        self.assertEqual(resposta.acao, "apagar_animal")
        self.assertIn("Draco", resposta.resposta)
        self.assertIn("Confirme", resposta.resposta)

    def test_sem_pet_aberto_nao_apaga(self):
        resposta = responder("apaga meu pet", animal=None)
        self.assertEqual(resposta.acao, "nenhuma")
        self.assertIn("nome dele", resposta.resposta)

    def test_modelo_nao_apaga_sem_pedido(self):
        request = ChatRequest(mensagem="ele está comendo pouco", animal=DRACO)
        resposta = apply_output_guardrails(
            ChatResponse(resposta="Vou apagar o pet.", acao="apagar_animal"), request
        )
        self.assertEqual(resposta.acao, "nenhuma")

    def test_modelo_esqueceu_a_acao(self):
        request = ChatRequest(mensagem="exclui o Draco do sistema", animal=DRACO)
        resposta = apply_output_guardrails(ChatResponse(resposta="Certo, vou remover o Draco."), request)
        self.assertEqual(resposta.acao, "apagar_animal")
        self.assertIn("Confirme", resposta.resposta)


class ListaPetsTest(unittest.TestCase):

    def test_pedidos_de_lista(self):
        for texto in ["quais são os meus pets?", "lista meus animais", "quantos pets eu tenho cadastrados", "mostra meus pets", "meus pets"]:
            self.assertTrue(pede_lista_pets(texto), texto)

    def test_outros_pedidos_nao_listam(self):
        for texto in ["apaga meus pets", "meu pet está vomitando", "meus gatos estão vomitando", "quais vacinas ele precisa?", "quais cuidados com filhotes de gatos?"]:
            self.assertFalse(pede_lista_pets(texto), texto)

    def test_chat_devolve_a_acao(self):
        resposta = responder("quais são os meus pets?", animal=None)
        self.assertEqual(resposta.acao, "listar_animais")


if __name__ == "__main__":
    unittest.main()
