import unittest

from app.chat_service import create_mock_chat_response
from app.schemas import ChatRequest

ANIMAL = {"id": 1, "nome": "Thor", "tipo": "CACHORRO"}


def conversar(mensagens):
    historico, respostas = [], []
    for mensagem in mensagens:
        resposta = create_mock_chat_response(
            ChatRequest(
                mensagem=mensagem,
                historico=historico + [{"role": "user", "content": mensagem}],
                animal=ANIMAL,
            )
        )
        historico += [
            {"role": "user", "content": mensagem},
            {"role": "assistant", "content": resposta.resposta},
        ]
        respostas.append(resposta)
    return respostas


class MockChatMemoryTests(unittest.TestCase):
    def test_does_not_repeat_answered_questions(self):
        respostas = conversar(["meu cachorro está doente", "desde ontem, ele não quer comer"])
        segunda = respostas[1].resposta
        self.assertNotIn("quanto tempo", segunda)
        self.assertNotIn("comendo normalmente", segunda)

    def test_gives_guidance_after_enough_information(self):
        respostas = conversar([
            "meu cachorro está doente",
            "desde ontem, ele não quer comer",
            "bebe água, não vomitou, mas está quieto",
        ])
        final = respostas[-1]
        self.assertIn("Entendi o quadro", final.resposta)
        self.assertIn("não está comendo", final.resposta)
        self.assertNotIn("vômito", final.resposta)
        self.assertTrue(final.procurar_veterinario)

    def test_mild_case_recommends_observation(self):
        respostas = conversar([
            "ele está tossindo desde hoje",
            "está comendo e bebendo normal, sem vômito, e brincando",
        ])
        self.assertFalse(respostas[-1].procurar_veterinario)
        self.assertIn("tosse", respostas[-1].resposta)

    def test_urgent_signal_any_turn(self):
        respostas = conversar(["meu gato comeu veneno de rato"])
        self.assertEqual(respostas[0].nivel_atencao, "urgente")


if __name__ == "__main__":
    unittest.main()
