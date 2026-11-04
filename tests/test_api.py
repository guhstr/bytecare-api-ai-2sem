import json
import os
import unittest
from pathlib import Path

os.environ["BYTECARE_AI_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
client = TestClient(app)


def _example(name):
    return json.loads((EXAMPLES / name).read_text())


class ApiTests(unittest.TestCase):
    def test_health(self):
        response = client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_plano_cuidado(self):
        response = client.post("/api/v1/plano-cuidado", json=_example("plano_cao_senior.json"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["nome_animal"], "Thor")
        self.assertTrue(body["acoes"])
        self.assertTrue(body["servicos_recomendados"])

    def test_priorizacao_clinica(self):
        response = client.post("/api/v1/clinica/priorizacao", json=_example("priorizacao_clinica.json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_pacientes"], 4)

    def test_servicos(self):
        response = client.get("/api/v1/servicos")
        self.assertEqual(response.status_code, 200)
        self.assertIn("VACINACAO", [s["codigo"] for s in response.json()])

    def test_analise_existente_continua_compativel(self):
        payload = _example("plano_gato_urgente.json")
        response = client.post("/api/v1/analises", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prioridade"], "urgente")

    def test_chat_mock(self):
        response = client.post("/api/v1/chat", json={"mensagem": "meu gato está com convulsão"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nivel_atencao"], "urgente")


if __name__ == "__main__":
    unittest.main()
