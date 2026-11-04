import json
import unittest
from pathlib import Path

from app.care_engine import fase_vida, gerar_plano, idade_em_anos, parse_date
from app.mock_service import build_care_plan, prioritize_patients
from app.schemas import AnimalContext, PlanoCuidadoRequest, PriorizacaoClinicaRequest

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
HOJE = "2026-11-03"


def _plano(animal, **dados):
    return gerar_plano(
        PlanoCuidadoRequest(animal=animal, data_referencia=HOJE, **dados)
    )


class CareEngineTests(unittest.TestCase):
    def test_parse_date_formats(self):
        self.assertEqual(str(parse_date("2026-09-15T10:00:00")), "2026-09-15")
        self.assertEqual(str(parse_date("15/09/2026")), "2026-09-15")
        self.assertIsNone(parse_date("em breve"))

    def test_life_stage_personalization(self):
        hoje = parse_date(HOJE)
        senior = AnimalContext(id=1, nome="Thor", tipo="CACHORRO", dataNascimento="2017-05-10")
        filhote = AnimalContext(id=2, nome="Luna", tipo="CACHORRO", idade="4 meses")
        self.assertEqual(fase_vida("cao", idade_em_anos(senior, hoje)), "senior")
        self.assertEqual(fase_vida("cao", idade_em_anos(filhote, hoje)), "filhote")

    def test_missing_core_vaccine_is_recommended(self):
        resultado = _plano(AnimalContext(id=1, nome="Bob", tipo="CACHORRO", idade=3))
        self.assertIn("Antirrábica", resultado.perfil.vacinas_pendentes)
        self.assertIn("VACINACAO", [s.codigo for s in resultado.servicos])

    def test_overdue_booster_is_high_priority(self):
        resultado = _plano(
            AnimalContext(id=1, nome="Bob", tipo="CACHORRO", idade=3),
            preventivos=[{"nomeServico": "Vacina V10", "proximoPrevisto": "2026-09-15"}],
        )
        atrasada = [a for a in resultado.acoes if a.titulo.startswith("Reforço atrasado")]
        self.assertEqual(atrasada[0].prioridade, "alta")

    def test_recent_red_flag_makes_plan_urgent(self):
        resultado = _plano(
            AnimalContext(id=2, nome="Mia", tipo="GATO", idade=3),
            bem_estar=[{"observacao": "dificuldade para respirar", "dataHoraRegistro": "2026-11-03T07:00:00"}],
        )
        self.assertEqual(resultado.prioridade, "urgente")
        self.assertTrue(resultado.procurar_veterinario)
        self.assertEqual(resultado.acoes[0].categoria, "urgencia")

    def test_old_record_is_history_not_current_signal(self):
        resultado = _plano(
            AnimalContext(id=2, nome="Mia", tipo="GATO", idade=3),
            bem_estar=[{"observacao": "convulsão", "dataHoraRegistro": "2024-01-10T07:00:00"}],
        )
        self.assertNotEqual(resultado.prioridade, "urgente")

    def test_pet_name_does_not_trigger_signal(self):
        resultado = _plano(AnimalContext(id=3, nome="Teodoro", tipo="GATO", idade=3))
        self.assertEqual(resultado.sinais_atencao, [])
        self.assertNotIn("CONSULTA_CLINICA", [s.codigo for s in resultado.servicos])

    def test_actions_are_sorted_by_priority(self):
        plano = build_care_plan(
            PlanoCuidadoRequest.model_validate(json.loads((EXAMPLES / "plano_cao_senior.json").read_text()))
        )
        ordem = {"baixa": 0, "moderada": 1, "alta": 2, "urgente": 3}
        valores = [ordem[a.prioridade] for a in plano.acoes]
        self.assertEqual(valores, sorted(valores, reverse=True))
        self.assertEqual(plano.perfil.fase_vida, "senior")

    def test_clinic_queue_puts_urgent_first(self):
        resultado = prioritize_patients(
            PriorizacaoClinicaRequest.model_validate(
                json.loads((EXAMPLES / "priorizacao_clinica.json").read_text())
            )
        )
        self.assertEqual(resultado.pacientes[0].nome_animal, "Mia")
        self.assertEqual(resultado.pacientes[0].prioridade, "urgente")
        self.assertEqual(resultado.pacientes[-1].prioridade, "baixa")


if __name__ == "__main__":
    unittest.main()
