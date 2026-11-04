import unittest

from app.care_engine import calendario_vacinas, especie_detalhada
from app.chat_service import apply_output_guardrails, create_mock_chat_response
from app.schemas import AnimalContext, ChatMessage, ChatRequest


def responder(mensagem, animal, historico=None):
    request = ChatRequest(mensagem=mensagem, animal=animal, historico=historico or [])
    return apply_output_guardrails(create_mock_chat_response(request), request)


class VacinasPorEspecieTest(unittest.TestCase):

    def test_papagaio_pela_subcategoria(self):
        draco = AnimalContext(id="1", nome="Draco", tipo="PASSARO", subcategoria="Papagaio",
                              dataNascimento="2025-11-01")
        resposta = responder("quais vacinas ele precisa?", draco).resposta
        self.assertIn("Papagaio não tem vacinas de rotina", resposta)
        self.assertNotIn("depende da espécie", resposta)

    def test_papagaio_pela_conversa(self):
        draco = AnimalContext(id="1", nome="Draco", tipo="PASSARO")
        historico = [ChatMessage(role="user", content="cadastra meu papagaio Draco de 1 ano")]
        resposta = responder("e as vacinas?", draco, historico).resposta
        self.assertIn("papagaio", resposta.lower())
        self.assertIn("clamidiose", resposta)

    def test_cao_nao_vira_papagaio_pela_conversa(self):
        thor = AnimalContext(id="2", nome="Thor", tipo="CACHORRO", dataNascimento="2020-01-01")
        historico = [ChatMessage(role="user", content="meu vizinho tem um papagaio")]
        resposta = responder("quais vacinas ele precisa?", thor, historico).resposta
        self.assertIn("V8/V10", resposta)

    def test_galinha_tem_calendario(self):
        vacinas, _, _ = calendario_vacinas("ave", 0.1, "galinha")
        self.assertTrue(any("Marek" in v for v in vacinas))

    def test_equino_e_bovino_tem_calendario_por_fase(self):
        adulto, _, _ = calendario_vacinas("equino", 5)
        self.assertTrue(any("Influenza" in v for v in adulto))
        bezerro, _, _ = calendario_vacinas("bovino", 0.4)
        self.assertTrue(any("Brucelose" in v for v in bezerro))

    def test_peixe_e_coelho_tem_orientacao(self):
        for grupo in ["peixe", "coelho"]:
            vacinas, _, orientacao = calendario_vacinas(grupo, 1)
            self.assertEqual(vacinas, [])
            self.assertTrue(orientacao)

    def test_especie_detalhada(self):
        self.assertEqual(especie_detalhada(None, "Papagaio-verdadeiro"), "papagaio")
        self.assertEqual(especie_detalhada("Canário"), "canário")
        self.assertIsNone(especie_detalhada("Husky Siberiano"))


if __name__ == "__main__":
    unittest.main()
