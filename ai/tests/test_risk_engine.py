import unittest
from app.risk_engine import evaluate_risk, enforce_minimum_priority


class RiskEngineTests(unittest.TestCase):
    def test_therapeutic_context_sets_moderate_minimum(self):
        result = evaluate_risk({"terapeuticos": [{"medicamento": "X"}]})
        self.assertEqual(result.minimum_priority, "moderada")

    def test_respiratory_red_flag_sets_urgent(self):
        result = evaluate_risk({"bem_estar": [{"observacao": "dificuldade para respirar"}]})
        self.assertEqual(result.minimum_priority, "urgente")
        self.assertTrue(result.seek_vet)

    def test_llm_cannot_lower_priority(self):
        self.assertEqual(enforce_minimum_priority("baixa", "alta"), "alta")
        self.assertEqual(enforce_minimum_priority("urgente", "alta"), "urgente")


if __name__ == "__main__":
    unittest.main()
